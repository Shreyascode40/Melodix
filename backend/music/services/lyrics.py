import os
from typing import Optional, Dict

RAPIDAPI_KEY = os.getenv(
    "RAPIDAPI_KEY", "7c226614edmsh71c43a9ea9bb0c0p1ddd4ejsn0e2f7e876a19"
)
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "spotify23.p.rapidapi.com")
BASE_URL = f"https://{RAPIDAPI_HOST}/track_lyrics/"


def get_lyrics(track_id: str) -> Optional[Dict]:
    if not track_id:
        return None
    try:
        from .session import get_session

        s = get_session()
        r = s.get(
            BASE_URL,
            params={"id": track_id},
            headers={
                "x-rapidapi-key": RAPIDAPI_KEY,
                "x-rapidapi-host": RAPIDAPI_HOST,
                "Content-Type": "application/json",
            },
            timeout=(2.5, 8),
        )
        r.raise_for_status()
        data = r.json()
        return data
    except Exception:
        return None
