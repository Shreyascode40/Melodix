from typing import List, Dict
from music.services.musicbrainz import search_recordings
from music.search.matcher import rank_candidates, match_song
from music.services.music_service import search_tracks


def match_candidates(candidates: List[Dict], limit: int = 3) -> List[Dict]:
    results = []
    for cand in candidates:
        title = cand.get("title") or ""
        artist = cand.get("artist") or ""
        query = f"{title} {artist}".strip() or title
        mb_results = []
        try:
            mb_results = search_recordings(query, limit=3)
        except Exception:
            mb_results = []
        best_mb = mb_results[0] if mb_results else None
        audius_q = (
            f"{best_mb['title']} {best_mb['artist']}".strip() if best_mb else query
        )
        tracks = []
        try:
            tracks = search_tracks(audius_q, limit=limit + 5)
            if not tracks and audius_q != query:
                tracks = search_tracks(query, limit=limit + 5)
        except Exception:
            tracks = []
        if best_mb:
            ranked = rank_candidates(best_mb, tracks) if tracks else []
            if ranked:
                best = ranked[0]
                results.append(
                    {
                        "detected": cand,
                        "musicbrainz": best_mb,
                        "matches": [
                            {
                                "track": t,
                                "score": t.get("match_score", 0) * 100
                                if t.get("match_score", 0) < 2
                                else t.get("match_score", 0),
                                "needs_review": t.get("match_status") != "high",
                            }
                            for t in ranked[:limit]
                        ],
                        "best": {
                            "track": {
                                "id": best["id"],
                                "provider": "audius",
                                "title": best["title"],
                                "artist": best["artist"],
                                "album": best.get("album") or best_mb.get("album", ""),
                                "cover_url": best.get("cover_url", ""),
                                "duration": best.get("duration", 0),
                                "stream_url": best.get("stream_url", ""),
                                "musicbrainz_id": best_mb.get("mbid"),
                                "playable": bool(best.get("stream_url")),
                            },
                            "score": best.get("match_score", 0) * 100
                            if best.get("match_score", 0) < 2
                            else best.get("match_score", 0),
                            "needs_review": best.get("match_status") != "high",
                            "source": "musicbrainz+audius",
                        },
                    }
                )
                continue
            else:
                mbid = (
                    best_mb.get("mbid")
                    or f"mb-{best_mb['title'][:20]}-{best_mb['artist'][:20]}"
                )
                results.append(
                    {
                        "detected": cand,
                        "musicbrainz": best_mb,
                        "matches": [],
                        "best": {
                            "track": {
                                "id": mbid,
                                "provider": "musicbrainz",
                                "provider_id": mbid,
                                "title": best_mb["title"],
                                "artist": best_mb["artist"],
                                "album": best_mb.get("album", ""),
                                "cover_url": "",
                                "duration": best_mb.get("duration") or 0,
                                "stream_url": "",
                                "musicbrainz_id": best_mb.get("mbid"),
                                "playable": False,
                            },
                            "score": 0,
                            "needs_review": True,
                            "source": "musicbrainz-only",
                        },
                    }
                )
                continue
        if tracks:
            from music.search.ranking import rank_results

            ranked_simple = rank_results(query, tracks)
            best = ranked_simple[0] if ranked_simple else tracks[0]
            score = 75 if ranked_simple else 50
            results.append(
                {
                    "detected": cand,
                    "musicbrainz": None,
                    "matches": [
                        {"track": t, "score": score, "needs_review": score < 70}
                        for t in ranked_simple[:limit]
                    ],
                    "best": {
                        "track": {
                            **best,
                            "musicbrainz_id": None,
                            "playable": bool(best.get("stream_url")),
                        },
                        "score": score,
                        "needs_review": score < 70,
                        "source": "audius-only",
                    },
                }
            )
        else:
            slug = (
                f"detected-{title[:20]}-{artist[:20]}".lower().replace(" ", "-")
                or "detected-unknown"
            )
            results.append(
                {
                    "detected": cand,
                    "musicbrainz": None,
                    "matches": [],
                    "best": {
                        "track": {
                            "id": slug,
                            "provider": "detected",
                            "provider_id": slug,
                            "title": title,
                            "artist": artist,
                            "album": cand.get("album", ""),
                            "cover_url": "",
                            "duration": 0,
                            "stream_url": "",
                            "musicbrainz_id": None,
                            "playable": False,
                        },
                        "score": 0,
                        "needs_review": True,
                        "source": "detected-only",
                    },
                }
            )
    return results
