import os
import requests
from typing import List, Dict, Optional
from .base import BaseProvider, normalize_track

AUDIUS_API = os.getenv("AUDIUS_API_BASE", "https://discoveryprovider.audius.co")
AUDIUS_API_AUTH = os.getenv("AUDIUS_API_AUTH_BASE", "https://api.audius.co")
TIMEOUT = 4


def _auth_headers():
    token = os.getenv("AUDIUS_BEARER_TOKEN", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}


class AudiusProvider(BaseProvider):
    name = "audius"

    def _get(self, path, params=None, use_auth=False):
        from .session import get_session

        try:
            base = AUDIUS_API_AUTH if use_auth and _auth_headers() else AUDIUS_API
            headers = _auth_headers() if use_auth else {}
            s = get_session()
            r = s.get(f"{base}{path}", params=params, headers=headers, timeout=(2.5, 5))
            if r.status_code == 429:
                return None
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            return None
        except Exception:
            return None

    def _get_trending_auth(self, limit):
        return self._get("/v1/tracks/trending", {"limit": limit}, use_auth=True)

    def search_tracks(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        data = self._get(
            "/v1/tracks/search", {"query": query, "limit": limit, "offset": offset}
        )
        if not data or "data" not in data:
            return []
        out = []
        for t in data["data"]:
            out.append(
                normalize_track(
                    "audius",
                    {
                        "id": t.get("id"),
                        "title": t.get("title"),
                        "artist": (t.get("user") or {}).get("name")
                        or t.get("artist")
                        or "Audius",
                        "album": t.get("album") or "",
                        "cover_url": (t.get("artwork") or {}).get("480x480")
                        or (t.get("artwork") or {}).get("150x150")
                        or "",
                        "duration": t.get("duration") or 0,
                        "stream_url": f"{AUDIUS_API}/v1/tracks/{t.get('id')}/stream",
                    },
                )
            )
        return out

    def get_track(self, track_id: str) -> Optional[Dict]:
        data = self._get(f"/v1/tracks/{track_id}")
        if not data or "data" not in data:
            return None
        t = data["data"]
        return normalize_track(
            "audius",
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "artist": (t.get("user") or {}).get("name") or "",
                "album": "",
                "cover_url": (t.get("artwork") or {}).get("480x480") or "",
                "duration": t.get("duration"),
                "stream_url": f"{AUDIUS_API}/v1/tracks/{t.get('id')}/stream",
            },
        )

    def get_trending_tracks(self, limit: int = 20) -> List[Dict]:
        data = self._get_trending_auth(limit)
        if data and "data" in data:
            pass
        else:
            data = self._get("/v1/tracks/trending", {"limit": limit, "time": "week"})
        if not data or "data" not in data:
            return []
        return [
            normalize_track(
                "audius",
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "artist": (t.get("user") or {}).get("name") or "",
                    "album": "",
                    "cover_url": (t.get("artwork") or {}).get("480x480") or "",
                    "duration": t.get("duration"),
                    "stream_url": f"{AUDIUS_API}/v1/tracks/{t.get('id')}/stream",
                },
            )
            for t in data["data"]
        ]
