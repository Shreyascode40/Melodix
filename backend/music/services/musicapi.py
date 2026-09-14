import os
from typing import List, Dict, Optional
from .base import BaseProvider, normalize_track

MUSICAPI_BASE = os.getenv("MUSICAPI_API_BASE", "https://api.musicapi.com")
TIMEOUT = (1.5, 3)
SOURCES = ["deezer", "spotify"]


class MusicApiProvider(BaseProvider):
    name = "musicapi"

    def _client_id(self):
        return os.getenv("MUSICAPI_CLIENT_ID", "").strip()

    def _headers(self):
        cid = self._client_id()
        return (
            {
                "Authorization": f"Token {cid}",
                "Content-Type": "application/json; charset=utf-8",
            }
            if cid
            else {}
        )

    def search_tracks(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        cid = self._client_id()
        if not cid or not query.strip():
            return []
        try:
            from .session import get_session

            parts = [p.strip() for p in query.replace(" - ", " - ").split(" - ")]
            if " - " in query:
                track = parts[0]
                artist = parts[1] if len(parts) > 1 else ""
            elif " by " in query.lower():
                sp = query.lower().split(" by ")
                track = query[: query.lower().index(" by ")].strip()
                artist = query[query.lower().index(" by ") + 4 :].strip()
            else:
                track = query.strip()
                artist = ""
            payload = {"sources": SOURCES[:2], "type": "track", "track": track}
            if artist:
                payload["artist"] = artist
            s = get_session()
            r = s.post(
                f"{MUSICAPI_BASE}/public/search",
                json=payload,
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()
            items = data.get("tracks") or []
            out = []
            for entry in items:
                if entry.get("status") != "success" or not entry.get("data"):
                    continue
                t = entry["data"]
                out.append(
                    normalize_track(
                        "musicapi",
                        {
                            "id": t.get("externalId") or t.get("id"),
                            "title": t.get("name") or t.get("title") or "Unknown",
                            "artist": ", ".join(t.get("artistNames") or [])
                            or t.get("artist")
                            or "Unknown",
                            "album": t.get("albumName") or "",
                            "cover_url": t.get("imageUrl") or "",
                            "duration": int((t.get("duration") or 0) / 1000)
                            if t.get("duration") and t.get("duration") > 1000
                            else int(t.get("duration") or 0),
                            "stream_url": t.get("previewUrl") or t.get("url") or "",
                            "language": "",
                        },
                    )
                )
            for item in out:
                if ".mp3" not in item.get("stream_url", ""):
                    try:
                        from .audius import AudiusProvider
                        from music.search.ranking import rank_results

                        a = AudiusProvider()
                        cand = a.search_tracks(
                            f"{item['title']} {item['artist']}", limit=5
                        )
                        cand = rank_results(f"{item['title']} {item['artist']}", cand)
                        if cand and cand[0].get("stream_url"):
                            item["stream_url"] = cand[0]["stream_url"]
                            item["fallback_stream"] = cand[0]["stream_url"]
                    except Exception:
                        pass
            if offset:
                out = out[offset : offset + limit]
            else:
                out = out[:limit]
            return out
        except Exception:
            return []

    def get_track(self, track_id: str) -> Optional[Dict]:
        cid = self._client_id()
        if not cid or not track_id:
            return None
        try:
            from .session import get_session

            s = get_session()
            url = f"https://open.spotify.com/track/{track_id}"
            r = s.post(
                f"{MUSICAPI_BASE}/public/inspect/url",
                json={"url": url},
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            if r.status_code == 200:
                j = r.json()
                if j.get("status") == "success" and j.get("data"):
                    t = j["data"]
                    return normalize_track(
                        "musicapi",
                        {
                            "id": t.get("externalId") or track_id,
                            "title": t.get("name") or "Unknown",
                            "artist": ", ".join(t.get("artistNames") or [])
                            or "Unknown",
                            "album": t.get("albumName") or "",
                            "cover_url": t.get("imageUrl") or "",
                            "duration": int((t.get("duration") or 0) / 1000)
                            if t.get("duration") and t.get("duration") > 1000
                            else 0,
                            "stream_url": t.get("url") or "",
                        },
                    )
            return None
        except Exception:
            return None

    def get_trending_tracks(self, limit: int = 20) -> List[Dict]:
        trending_queries = [
            "Blinding Lights - The Weeknd",
            "As It Was - Harry Styles",
            "Flowers - Miley Cyrus",
        ]
        out = []
        for q in trending_queries:
            out.extend(self.search_tracks(q, limit=5))
            if len(out) >= limit:
                break
        return out[:limit]
