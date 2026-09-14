import re
import difflib


def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0
    return (
        difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()
        * 100
    )


def duration_sim(d1, d2) -> float:
    if not d1 or not d2:
        return 50
    try:
        diff = abs(int(d1) - int(d2))
        if diff == 0:
            return 100
        if diff <= 2:
            return 95
        if diff <= 5:
            return 80
        if diff <= 10:
            return 60
        return 30
    except:
        return 50


def confidence_score(detected: dict, candidate: dict) -> float:
    title_s = sim(detected.get("title", ""), candidate.get("title", ""))
    artist_s = (
        sim(detected.get("artist", ""), candidate.get("artist", ""))
        if detected.get("artist")
        else 50
    )
    album_s = (
        sim(detected.get("album", ""), candidate.get("album", ""))
        if detected.get("album")
        else 50
    )
    dur_s = duration_sim(detected.get("duration"), candidate.get("duration"))
    overall = title_s * 0.4 + artist_s * 0.35 + album_s * 0.15 + dur_s * 0.1
    return round(overall, 1)


def needs_review(score: float) -> bool:
    return score < 70
