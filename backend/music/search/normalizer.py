import re
import unicodedata

_WS = re.compile(r"\s+")
_PUNCT = re.compile(
    r"[^\w\s\u00C0-\u024F\u0400-\u04FF\u0600-\u06FF\u0900-\u097F\u4E00-\u9FFF]+",
    re.UNICODE,
)


def normalize_query(q: str) -> str:
    if not q:
        return ""
    q = q.strip().lower()
    q = _WS.sub(" ", q)
    q = _PUNCT.sub(" ", q)
    q = _WS.sub(" ", q).strip()
    return q


def cache_key(
    query: str, page: int = 1, limit: int = 12, provider: str = "musicapi"
) -> str:
    nq = normalize_query(query)
    return f"music:search:{provider}:{nq}:{page}:{limit}"
