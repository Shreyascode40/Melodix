import re

_NEG = re.compile(r"(remix|cover|instrumental|karaoke|sped up|slowed|nightcore)", re.I)


def rank_score(query: str, song: dict) -> float:
    q = query.lower().strip()
    title = (song.get("title") or "").lower()
    artist = (song.get("artist") or "").lower()
    score = 0
    if title == q:
        score += 100
    elif title.startswith(q):
        score += 80
    elif q in title:
        score += 60
    if q in artist:
        score += 30
    if title and artist and q in f"{title} {artist}":
        score += 20
    if _NEG.search(title):
        score -= 25
    return score


def rank_results(query: str, results: list) -> list:
    scored = [(rank_score(query, r), r) for r in results]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored]
