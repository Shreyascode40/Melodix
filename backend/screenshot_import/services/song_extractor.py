import re
from typing import List, Dict

CLEAN_RE = re.compile(r"\s+")


def normalize_text(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = CLEAN_RE.sub(" ", s)
    return s.strip()


def _clean_raw(raw: str) -> str:
    raw = raw.replace("�", "•").replace("·", "•").replace("·", "•")
    raw = re.sub(r"^\d+[\.\)\s]*", "", raw).strip()
    raw = re.sub(r"\s+rs\s*$", "", raw, flags=re.I).strip()
    raw = re.sub(r"\s+rs\s+\d+:\d+\s*$", "", raw, flags=re.I).strip()
    raw = re.sub(r"\s+\d+:\d+\s*$", "", raw).strip()
    raw = re.sub(r"\s+\d{3,4}\s*$", "", raw).strip()
    if re.match(r"^\d+[A-Za-z]", raw):
        raw = re.sub(r"^\d+", "", raw).strip()
    return raw


def parse_line(line: str) -> Dict:
    raw = _clean_raw(line.strip())
    if not raw or len(raw) < 2:
        return None
    if re.search(r"[•·●]", raw):
        parts = re.split(r"\s*[•·●]\s*", raw, maxsplit=1)
        artist = parts[0].strip()
        album = parts[1].strip() if len(parts) > 1 else ""
        return {
            "raw": line,
            "title": "",
            "artist": artist,
            "album": album,
            "_is_artist_line": True,
        }
    parts = re.split(r"\s*[-–—]\s*|\s+by\s+|\s+\|\s*", raw, maxsplit=1)
    if len(parts) == 2:
        a, b = parts[0].strip(), parts[1].strip()
        a = re.sub(r"^\d+\s*", "", a).strip()
        b = re.sub(r"\s*\d+:\d+\s*$", "", b).strip()
        if len(b) < 2:
            return {"raw": line, "title": a, "artist": "", "album": ""}
        return {"raw": line, "title": a, "artist": b, "album": ""}
    return {"raw": line, "title": raw, "artist": "", "album": ""}


def _strip_chrome_prefix(s: str) -> str:
    s = re.sub(r"^[I|]\s*Home\s*", "", s).strip()
    s = re.sub(r"^(Home|Explore|Library|Upgrade)\s+", "", s, flags=re.I).strip()
    return s


def _is_chrome(line: str) -> bool:
    s = _strip_chrome_prefix(line.strip())
    if len(s) < 4:
        return True
    low = s.lower()
    if low in (
        "liked music",
        "auto playlist",
        "home",
        "explore",
        "library",
        "upgrade",
        "new playlist",
        "search songs, albums, artists, podcasts",
    ):
        return True
    if "music.youtube.com" in low or "youtube.com/playlist" in low:
        return True
    if "://".lower() in low and "youtube" in low:
        return True
    if low.count("@") >= 2:
        return True
    if re.match(r"^WE \d+", s):
        return True
    if low.startswith("we ") and "@" in low:
        return True
    if "search songs, albums" in low:
        return True
    if "shreyas more" in low and len(s) < 30:
        return True
    if "auto playlist" in low or "episodes for later" in low:
        return True
    if re.search(r"[\\/>]{2,}", s) and len(re.findall(r"[a-zA-Z]", s)) < len(s) * 0.4:
        return True
    if re.search(r"\d\s*/\s*\d+", s) and len(s) < 20:
        return True
    if s.count(">") >= 2 or s.count("\\") >= 2:
        return True
    if re.search(r"/\d", s) and len(re.findall(r"[A-Za-z]{3,}", s)) < 2:
        return True
    if re.match(r"^/[\d: ]+$", s):
        return True
    if len(re.findall(r"[A-Za-z]{3,}", s)) == 0 and len(s) < 15:
        return True
    return False


def extract_candidates(lines: List[str]) -> List[Dict]:
    cleaned = []
    for l in lines:
        s = _strip_chrome_prefix(l.strip())
        if not s:
            continue
        if re.match(r"^\d+:\d+$", s):
            continue
        if re.match(r"^\d+$", s):
            continue
        if _is_chrome(l) or _is_chrome(s):
            if (
                len(s) > 15
                and not _is_chrome(s)
                and "@" not in s
                and "http" not in s.lower()
            ):
                cleaned.append(s)
            continue
        cleaned.append(s if s != l.strip() else l)
    out = []
    i = 0
    while i < len(cleaned):
        line = cleaned[i]
        parsed = parse_line(line)
        if not parsed:
            i += 1
            continue
        if parsed.get("_is_artist_line"):
            if out and not out[-1].get("artist"):
                out[-1]["artist"] = parsed["artist"]
                out[-1]["album"] = parsed.get("album", "")
                out[-1]["raw"] = out[-1]["raw"] + " | " + line
            elif out and out[-1].get("artist") and not parsed.get("title"):
                pass
            else:
                if parsed["artist"] and len(parsed["artist"]) > 2:
                    out.append(
                        {
                            "raw": line,
                            "title": parsed["artist"],
                            "artist": "",
                            "album": parsed.get("album", ""),
                        }
                    )
            i += 1
            continue
        if i + 1 < len(cleaned):
            nxt = cleaned[i + 1]
            nxt_parsed = parse_line(nxt)
            is_next_artist = nxt_parsed and (
                nxt_parsed.get("_is_artist_line")
                or ("•" in nxt or " - " in nxt or " – " in nxt)
            )
            if is_next_artist and not parsed.get("artist"):
                if nxt_parsed.get("_is_artist_line"):
                    parsed["artist"] = nxt_parsed["artist"]
                    parsed["album"] = nxt_parsed.get("album", "")
                elif nxt_parsed.get("artist"):
                    parsed["artist"] = nxt_parsed["artist"]
                    parsed["album"] = nxt_parsed.get("album", "")
                else:
                    parsed["artist"] = (
                        _clean_raw(nxt).split("•")[0].strip()
                        if "•" in nxt
                        else _clean_raw(nxt).split("-")[0].strip()
                    )
                parsed["raw"] = line + " | " + nxt
                i += 1
        if parsed.get("title") and len(parsed["title"]) >= 2:
            parsed.pop("_is_artist_line", None)
            parsed["title"] = re.sub(r"\s+", " ", parsed["title"]).strip()
            out.append(parsed)
        i += 1
    filtered = []
    for p in out:
        t = p["title"].lower()
        if t in ("liked music", "upgrade", "home", "explore") or len(t) < 3:
            continue
        filtered.append(p)
    return filtered
