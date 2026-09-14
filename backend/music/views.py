from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .services.music_service import search_tracks, get_trending, get_track
from .models import Song


class SearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.GET.get("q", "")
        provider = request.GET.get("provider", "audius")
        enriched = request.GET.get("enriched", "1") != "0"
        try:
            page = max(1, int(request.GET.get("page", "1")))
            limit = min(30, max(1, int(request.GET.get("limit", "12"))))
        except:
            page, limit = 1, 12
        from music.search.normalizer import normalize_query

        nq = normalize_query(q)
        if not nq:
            return Response({"results": [], "page": page, "cached": False, "query": ""})
        offset = (page - 1) * limit
        import time
        from django.core.cache import cache
        from music.search.normalizer import cache_key
        from music.services.music_service import search_enriched

        key = cache_key(nq, page, limit)
        t0 = time.monotonic()
        cached_before = (
            cache.get(key if not enriched else f"music:enriched:{nq}:{limit}")
            is not None
        )
        try:
            if enriched:
                results = search_enriched(nq, limit)
            else:
                results = search_tracks(nq, provider, limit, offset)
            language = request.GET.get("language")
            if language:
                results = [
                    r
                    for r in results
                    if language.lower() in (r.get("language") or "").lower()
                ]
            total_ms = (time.monotonic() - t0) * 1000
            resp = Response(
                {
                    "results": results,
                    "page": page,
                    "limit": limit,
                    "query": nq,
                    "cached": cached_before,
                }
            )
            resp["X-Cache"] = "HIT" if cached_before else "MISS"
            resp["X-Response-Time"] = f"{total_ms:.0f}ms"
            return resp
        except Exception:
            stale = cache.get(key)
            if stale is not None:
                return Response(
                    {"results": stale, "page": page, "cached": True, "stale": True}
                )
            return Response(
                {"detail": "Music provider temporarily unavailable", "results": []},
                status=502,
            )


class TrendingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        provider = request.GET.get("provider", "audius")
        limit = int(request.GET.get("limit", "20"))
        try:
            results = get_trending(limit, provider)
        except Exception as e:
            return Response({"detail": "provider unavailable"}, status=502)
        return Response({"results": results})


class TrackDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, provider, track_id):
        track = get_track(provider, track_id)
        if not track:
            return Response({"detail": "not found"}, status=404)
        return Response(track)


class ResolveSongView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        provider = data.get("provider")
        pid = data.get("provider_song_id") or data.get("id")
        if not provider or not pid:
            return Response({"detail": "provider and id required"}, status=400)
        song, created = Song.objects.get_or_create(
            provider=provider,
            provider_song_id=str(pid),
            defaults={
                "title": data.get("title", "Unknown"),
                "artist": data.get("artist", "Unknown"),
                "album": data.get("album", ""),
                "cover_url": data.get("cover_url", ""),
                "duration": data.get("duration", 0),
                "stream_url": data.get("stream_url", ""),
                "language": data.get("language", ""),
            },
        )
        return Response(
            {
                "id": song.id,
                "provider": song.provider,
                "provider_song_id": song.provider_song_id,
            }
        )
