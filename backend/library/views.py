from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from music.models import Song
from .models import LikedSong, RecentlyPlayed
from playlists.serializers import SongSerializer


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        provider = request.data.get("provider")
        pid = request.data.get("provider_song_id") or request.data.get("id")
        if not provider or not pid:
            return Response({"detail": "provider and id required"}, status=400)
        song, _ = Song.objects.get_or_create(
            provider=provider,
            provider_song_id=str(pid),
            defaults={
                "title": request.data.get("title", "Unknown"),
                "artist": request.data.get("artist", "Unknown"),
                "album": request.data.get("album", ""),
                "cover_url": request.data.get("cover_url", ""),
                "duration": request.data.get("duration", 0),
                "stream_url": request.data.get("stream_url", ""),
            },
        )
        LikedSong.objects.get_or_create(user=request.user, song=song)
        return Response({"detail": "liked"})


class UnlikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, song_id):
        ls = get_object_or_404(LikedSong, user=request.user, song__id=song_id)
        ls.delete()
        return Response(status=204)

    def post(self, request):
        sid = request.data.get("song_id") or request.data.get("id")
        if not sid:
            return Response(status=400)
        LikedSong.objects.filter(user=request.user, song__id=sid).delete()
        return Response(status=204)


class LikedListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (
            LikedSong.objects.filter(user=request.user)
            .select_related("song")
            .order_by("-created_at")
        )
        return Response(SongSerializer([x.song for x in qs], many=True).data)


class RecentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (
            RecentlyPlayed.objects.filter(user=request.user)
            .select_related("song")
            .order_by("-played_at")[:50]
        )
        return Response(SongSerializer([x.song for x in qs], many=True).data)


class RecordPlayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        provider = request.data.get("provider")
        pid = request.data.get("provider_song_id") or request.data.get("id")
        if not provider or not pid:
            return Response(status=400)
        song, _ = Song.objects.get_or_create(
            provider=provider,
            provider_song_id=str(pid),
            defaults={
                "title": request.data.get("title", "Unknown"),
                "artist": request.data.get("artist", "Unknown"),
                "album": request.data.get("album", ""),
                "cover_url": request.data.get("cover_url", ""),
                "duration": request.data.get("duration", 0),
                "stream_url": request.data.get("stream_url", ""),
            },
        )
        RecentlyPlayed.objects.create(user=request.user, song=song)
        qs = RecentlyPlayed.objects.filter(user=request.user).order_by("-played_at")
        if qs.count() > 100:
            for r in qs[100:]:
                r.delete()
        return Response({"detail": "recorded"})
