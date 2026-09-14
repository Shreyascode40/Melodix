import os
import requests
from typing import List, Dict, Optional
from .base import BaseProvider, normalize_track

JAMENDO_API = "https://api.jamendo.com/v3.0"
TIMEOUT = 8


class JamendoProvider(BaseProvider):
    name = "jamendo"

    def _client_id(self):
        return os.getenv("JAMENDO_CLIENT_ID", "")

    def search_tracks(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        cid = self._client_id()
        if not cid:
            return []
        try:
            from .session import get_session

            r = get_session().get(
                f"{JAMENDO_API}/tracks",
                params={
                    "client_id": cid,
                    "format": "json",
                    "search": query,
                    "limit": limit,
                    "offset": offset,
                    "include": "musicinfo",
                },
                timeout=(2.5, 5),
            )
            r.raise_for_status()
            data = r.json()
            out = []
            for t in data.get("results", []):
                out.append(
                    normalize_track(
                        "jamendo",
                        {
                            "id": t.get("id"),
                            "title": t.get("name"),
                            "artist": t.get("artist_name"),
                            "album": t.get("album_name") or "",
                            "cover_url": t.get("album_image") or t.get("image") or "",
                            "duration": int(float(t.get("duration") or 0)),
                            "stream_url": t.get("audio") or "",
                            "language": t.get("musicinfo", {}).get("lang") or "",
                        },
                    )
                )
            return out
        except Exception:
            return []

    def get_track(self, track_id: str) -> Optional[Dict]:
        cid = self._client_id()
        if not cid:
            return None
        try:
            from .session import get_session

            r = get_session().get(
                f"{JAMENDO_API}/tracks",
                params={"client_id": cid, "format": "json", "id": track_id},
                timeout=(2.5, 5),
            )
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            if not results:
                return None
            t = results[0]
            return normalize_track(
                "jamendo",
                {
                    "id": t.get("id"),
                    "title": t.get("name"),
                    "artist": t.get("artist_name"),
                    "album": t.get("album_name") or "",
                    "cover_url": t.get("album_image") or "",
                    "duration": int(float(t.get("duration") or 0)),
                    "stream_url": t.get("audio") or "",
                },
            )
        except Exception:
            return None

    def get_trending_tracks(self, limit: int = 20) -> List[Dict]:
        cid = self._client_id()
        if not cid:
            return []
        try:
            from .session import get_session

            r = get_session().get(
                f"{JAMENDO_API}/tracks",
                params={
                    "client_id": cid,
                    "format": "json",
                    "order": "popularity_week",
                    "limit": limit,
                },
                timeout=(2.5, 5),
            )
            r.raise_for_status()
            data = r.json()
            return [
                normalize_track(
                    "jamendo",
                    {
                        "id": t.get("id"),
                        "title": t.get("name"),
                        "artist": t.get("artist_name"),
                        "album": t.get("album_name") or "",
                        "cover_url": t.get("album_image") or "",
                        "duration": int(float(t.get("duration") or 0)),
                        "stream_url": t.get("audio") or "",
                    },
                )
                for t in data.get("results", [])
            ]
        except Exception:
            return []
