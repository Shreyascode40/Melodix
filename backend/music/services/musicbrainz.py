import time
import logging
from typing import List, Dict, Optional
from django.conf import settings
from django.core.cache import cache
from .session import get_session

log = logging.getLogger("music.musicbrainz")
BASE_URL = "https://musicbrainz.org/ws/2"
CACHE_TTL = 1800
_last_call = 0


def _throttle():
    global _last_call
    now = time.monotonic()
    wait = 1.0 - (now - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


def _headers():
    return {"User-Agent": settings.MUSICBRAINZ_USER_AGENT, "Accept": "application/json"}


def _handle_503_retry(func):
    def wrapper(*a, **kw):
        try:
            return func(*a, **kw)
        except Exception as e:
            log.debug(f"MB retry after 503/timeout: {e}")
            time.sleep(1.5)
            try:
                return func(*a, **kw)
            except Exception as e2:
                log.debug(f"MB retry failed: {e2}")
                return None

    return wrapper


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def _cache_set(key, val, ttl):
    try:
        cache.set(key, val, ttl)
    except Exception:
        pass


def search_recordings(query: str, limit: int = 8) -> List[Dict]:
    from music.search.normalizer import normalize_query

    nq = normalize_query(query)
    if not nq:
        return []
    key = f"musicbrainz:recording:{nq}:{limit}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    _throttle()
    try:
        s = get_session()
        r = s.get(
            f"{BASE_URL}/recording",
            params={"query": query, "fmt": "json", "limit": limit},
            headers=_headers(),
            timeout=(2.5, 5),
        )
        if r.status_code == 429:
            log.warning("MB 429")
            return cached or []
        if r.status_code == 503:
            time.sleep(1.2)
            r = s.get(
                f"{BASE_URL}/recording",
                params={"query": query, "fmt": "json", "limit": limit},
                headers=_headers(),
                timeout=(2.5, 5),
            )
        r.raise_for_status()
        data = r.json()
        out = []
        for rec in data.get("recordings", [])[:limit]:
            title = rec.get("title") or ""
            artist = ", ".join(
                a.get("name") or a.get("artist", {}).get("name", "")
                for a in rec.get("artist-credit", [])
            )
            artist_mbid = ""
            if rec.get("artist-credit") and len(rec["artist-credit"]) > 0:
                artist_mbid = rec["artist-credit"][0].get("artist", {}).get(
                    "id", ""
                ) or rec["artist-credit"][0].get("id", "")
            releases = rec.get("releases") or []
            album = releases[0].get("title") if releases else ""
            year = ""
            if releases and releases[0].get("date"):
                year = releases[0]["date"][:4]
            out.append(
                {
                    "mbid": rec.get("id"),
                    "title": title,
                    "artist": artist,
                    "artist_mbid": artist_mbid,
                    "album": album,
                    "duration": rec.get("length"),
                    "isrcs": rec.get("isrcs") or [],
                    "year": year,
                }
            )
        _cache_set(key, out, CACHE_TTL)
        return out
    except Exception as e:
        log.debug(f"MB search_recordings error {e}")
        return _cache_get(key) or []


def search_artists(query: str, limit: int = 5) -> List[Dict]:
    key = f"musicbrainz:artist:{query.lower().strip()}:{limit}"
    c = _cache_get(key)
    if c is not None:
        return c
    _throttle()
    try:
        s = get_session()
        r = s.get(
            f"{BASE_URL}/artist",
            params={"query": query, "fmt": "json", "limit": limit},
            headers=_headers(),
            timeout=(2.5, 5),
        )
        if r.status_code == 503:
            time.sleep(1.2)
            r = s.get(
                f"{BASE_URL}/artist",
                params={"query": query, "fmt": "json", "limit": limit},
                headers=_headers(),
                timeout=(2.5, 5),
            )
        r.raise_for_status()
        data = r.json()
        out = [
            {"mbid": a.get("id"), "name": a.get("name"), "type": a.get("type")}
            for a in data.get("artists", [])[:limit]
        ]
        _cache_set(key, out, CACHE_TTL)
        return out
    except Exception:
        return _cache_get(key) or []


def search_releases(query: str, limit: int = 5) -> List[Dict]:
    from music.search.normalizer import normalize_query

    nq = normalize_query(query)
    key = f"musicbrainz:release:{nq}:{limit}"
    c = cache.get(key)
    if c is not None:
        return c
    _throttle()
    try:
        s = get_session()
        r = s.get(
            f"{BASE_URL}/release",
            params={"query": query, "fmt": "json", "limit": limit},
            headers=_headers(),
            timeout=(2.5, 5),
        )
        if r.status_code == 503:
            time.sleep(1.2)
            r = s.get(
                f"{BASE_URL}/release",
                params={"query": query, "fmt": "json", "limit": limit},
                headers=_headers(),
                timeout=(2.5, 5),
            )
        r.raise_for_status()
        data = r.json()
        out = [
            {
                "mbid": r.get("id"),
                "title": r.get("title"),
                "artist": ", ".join(
                    a.get("artist", {}).get("name", "")
                    for a in r.get("artist-credit", [])
                ),
            }
            for r in data.get("releases", [])[:limit]
        ]
        _cache_set(key, out, CACHE_TTL)
        return out
    except Exception:
        return _cache_get(key) or []


def get_recording(mbid: str) -> Optional[Dict]:
    key = f"musicbrainz:recording:mbid:{mbid}"
    c = cache.get(key)
    if c is not None:
        return c
    _throttle()
    try:
        s = get_session()
        r = s.get(
            f"{BASE_URL}/recording/{mbid}",
            params={"fmt": "json", "inc": "artists+releases+isrcs"},
            headers=_headers(),
            timeout=(2.5, 5),
        )
        if r.status_code == 503:
            time.sleep(1.2)
            r = s.get(
                f"{BASE_URL}/recording/{mbid}",
                params={"fmt": "json", "inc": "artists+releases+isrcs"},
                headers=_headers(),
                timeout=(2.5, 5),
            )
        r.raise_for_status()
        d = r.json()
        out = {
            "mbid": d.get("id"),
            "title": d.get("title"),
            "artist": ", ".join(a.get("name", "") for a in d.get("artist-credit", [])),
            "length": d.get("length"),
            "isrcs": d.get("isrcs") or [],
        }
        _cache_set(key, out, CACHE_TTL)
        return out
    except Exception:
        return _cache_get(key) or None
