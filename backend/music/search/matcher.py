import re
from typing import Dict, List

try:
    from rapidfuzz import fuzz

    def sim(a, b):
        return fuzz.ratio(a.lower(), b.lower())
except:
    import difflib

    def sim(a, b):
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100


_NEG = re.compile(
    r"\b(remix|cover|instrumental|karaoke|slowed|sped ?up|nightcore|lofi|8d|live)\b",
    re.I,
)


def title_score(q_title: str, cand_title: str) -> float:
    if not q_title or not cand_title:
        return 0
    return sim(q_title.strip(), cand_title.strip())


def artist_score(q_artist: str, cand_artist: str) -> float:
    if not q_artist or not cand_artist:
        return 50
    return sim(q_artist.strip(), cand_artist.strip())


def duration_score(mb_len, cand_dur) -> float:
    if not mb_len or not cand_dur:
        return 50
    try:
        mb = int(mb_len) / 1000
        cd = int(cand_dur)
        diff = abs(mb - cd)
        if diff <= 2:
            return 100
        if diff <= 5:
            return 85
        if diff <= 10:
            return 60
        if diff <= 20:
            return 35
        return 10
    except:
        return 50


def match_song(mb: Dict, cand: Dict) -> Dict:
    t = title_score(mb.get("title", ""), cand.get("title", ""))
    a = artist_score(mb.get("artist", ""), cand.get("artist", ""))
    combined = sim(
        f"{mb.get('title', '')} {mb.get('artist', '')}".strip(),
        f"{cand.get('title', '')} {cand.get('artist', '')}".strip(),
    )
    d = duration_score(mb.get("duration") or mb.get("length"), cand.get("duration"))
    score = t * 0.4 + a * 0.3 + combined * 0.2 + d * 0.1
    if _NEG.search(cand.get("title", "")):
        score -= 22
    if _NEG.search(cand.get("artist", "")):
        score -= 10
    score = max(0, min(100, score))
    status = "high" if score >= 80 else "medium" if score >= 55 else "low"
    return {
        "score": round(score, 1),
        "status": status,
        "title_sim": round(t, 1),
        "artist_sim": round(a, 1),
        "duration_sim": round(d, 1),
    }


def rank_candidates(mb: Dict, candidates: List[Dict]) -> List[Dict]:
    scored = []
    for c in candidates:
        m = match_song(mb, c)
        scored.append(
            {**c, "match_score": m["score"], "match_status": m["status"], "_m": m}
        )
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored


def best_match_for_query(query: str, candidates: List[Dict]) -> List[Dict]:
    fake_mb = {"title": query, "artist": "", "duration": None}
    return rank_candidates(fake_mb, candidates)
