import time
import logging
from typing import List, Dict, Optional
from django.core.cache import cache
from music.search.normalizer import normalize_query, cache_key
from music.search.ranking import rank_results
from music.search.matcher import rank_candidates
from .musicapi import MusicApiProvider

log = logging.getLogger("music.search")

_providers = {
    "musicapi": MusicApiProvider(),
}

STREAM_CACHE_TTL = 600
SEARCH_TTL = 900
STALE_TTL = 86400


def get_provider(name: str):
    return _providers.get(name)


def _stream_cache_key(provider, pid):
    return f"music:stream:{provider}:{pid}"


def get_stream_cached(provider: str, pid: str) -> Optional[str]:
    k = _stream_cache_key(provider, pid)
    v = cache.get(k)
    if v:
        return v
    p = _providers.get(provider)
    if not p:
        return None
    url = p.get_stream_url(pid)
    if url:
        cache.set(k, url, STREAM_CACHE_TTL)
        return url
    return None


def search_enriched(query: str, limit: int = 12) -> List[Dict]:
    from music.services.musicbrainz import search_recordings

    nq = normalize_query(query)
    if not nq:
        return []
    key = f"music:enriched:{nq}:{limit}"
    cached = cache.get(key)
    if cached is not None:
        log.debug(f'ENRICHED q="{nq}" cache=HIT')
        return cached
    t0 = time.monotonic()
    mb_results = []
    try:
        mb_results = search_recordings(query, limit=5)
    except Exception as e:
        log.debug(f"MB fail {e}")
    if mb_results:
        best_mb = mb_results[0]
        musicapi_q = f"{best_mb['title']} {best_mb['artist']}".strip()
        candidates = _providers["musicapi"].search_tracks(
            musicapi_q, limit=20, offset=0
        )
        if not candidates:
            candidates = _providers["musicapi"].search_tracks(nq, limit=20, offset=0)
        ranked = rank_candidates(best_mb, candidates)
        out = []
        for r in ranked[:limit]:
            out.append(
                {
                    "id": r["id"],
                    "provider": "musicapi",
                    "provider_id": r["id"],
                    "title": r["title"],
                    "artist": r["artist"],
                    "album": r.get("album") or best_mb.get("album", ""),
                    "cover_url": r.get("cover_url", ""),
                    "artwork": r.get("cover_url", ""),
                    "duration": r.get("duration", 0),
                    "stream_url": r.get("stream_url", ""),
                    "musicbrainz_id": best_mb.get("mbid"),
                    "match_score": round(r["match_score"] / 100, 2),
                    "match_status": r["match_status"],
                    "playable": bool(r.get("stream_url")),
                }
            )
        if not out:
            out = [
                {
                    "title": best_mb["title"],
                    "artist": best_mb["artist"],
                    "album": best_mb.get("album", ""),
                    "duration": best_mb.get("duration") or 0,
                    "musicbrainz_id": best_mb.get("mbid"),
                    "provider": "musicapi",
                    "provider_id": "",
                    "playable": False,
                    "match_score": 0,
                }
            ]
        cache.set(key, out, SEARCH_TTL)
        log.debug(
            f'ENRICHED q="{nq}" MB->MusicAPI total={(time.monotonic() - t0) * 1000:.0f}ms'
        )
        return out
    candidates = _providers["musicapi"].search_tracks(nq, limit=20, offset=0)
    ranked = rank_results(nq, candidates) if candidates else []
    out = [
        {
            **r,
            "musicbrainz_id": None,
            "match_score": 0.5,
            "match_status": "medium",
            "playable": bool(r.get("stream_url")),
            "provider_id": r.get("id"),
        }
        for r in ranked[:limit]
    ]
    cache.set(key, out, SEARCH_TTL)
    return out


def search_tracks(
    query: str, provider: str = "musicapi", limit: int = 12, offset: int = 0
) -> List[Dict]:
    if provider == "enriched":
        return search_enriched(query, limit)
    if "musicbrainz" in provider:
        return search_enriched(query, limit)
    nq = normalize_query(query)
    if not nq:
        return []
    page = offset // limit + 1 if limit else 1
    key = cache_key(nq, page, limit, provider)
    cached = cache.get(key)
    if cached is not None:
        return cached
    stale_key = f"{key}:stale"
    stale = cache.get(stale_key)
    if stale is not None:
        return stale
    results = (
        _providers.get(provider, _providers["musicapi"]).search_tracks(
            nq, limit, offset
        )
        if provider in _providers
        else []
    )
    results = rank_results(nq, results)
    results = [r for r in results if r.get("title")]
    results = [
        {
            k: r[k]
            for k in (
                "id",
                "title",
                "artist",
                "album",
                "cover_url",
                "duration",
                "stream_url",
                "provider",
                "language",
            )
            if k in r
        }
        for r in results
    ]
    try:
        cache.set(key, results, SEARCH_TTL)
        cache.set(stale_key, results, STALE_TTL)
    except:
        pass
    return results


def get_trending(limit: int = 12, provider: str = "musicapi") -> List[Dict]:
    key = f"music:trending:{provider}:{limit}"
    c = cache.get(key)
    if c is not None:
        return c
    stale_key = f"{key}:stale"
    stale = cache.get(stale_key)
    p = _providers.get(provider, _providers["musicapi"])
    try:
        r = p.get_trending_tracks(limit)
        cache.set(key, r, 600)
        cache.set(stale_key, r, STALE_TTL)
        return r
    except:
        return stale or c or []


def get_track(provider: str, track_id: str) -> Optional[Dict]:
    p = _providers.get(provider)
    if not p:
        return None
    return p.get_track(track_id)
