from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def search_tracks(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        pass

    @abstractmethod
    def get_track(self, track_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_trending_tracks(self, limit: int = 20) -> List[Dict]:
        pass

    def get_stream_url(self, track_id: str) -> Optional[str]:
        track = self.get_track(track_id)
        return track.get("stream_url") if track else None

    def normalize(self, raw: dict) -> Dict:
        return raw


def normalize_track(provider: str, data: dict) -> dict:
    return {
        "id": str(data.get("id") or data.get("provider_song_id") or ""),
        "provider": provider,
        "title": data.get("title") or "Unknown",
        "artist": data.get("artist") or "Unknown",
        "album": data.get("album") or "",
        "cover_url": data.get("cover_url") or data.get("artwork") or "",
        "duration": int(data.get("duration") or 0),
        "stream_url": data.get("stream_url") or "",
        "language": data.get("language") or "",
    }
