from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Max
from .models import Playlist, PlaylistSong
from .serializers import PlaylistSerializer
from music.models import Song
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


def is_owner_or_public(user, playlist):
    return playlist.is_public or playlist.user == user


class PlaylistListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = (
            Playlist.objects.filter(user=request.user)
            if request.user.is_authenticated
            else Playlist.objects.filter(is_public=True)
        )
        if not request.user.is_authenticated:
            qs = Playlist.objects.filter(is_public=True)
        else:
            qs = Playlist.objects.filter(user=request.user) | Playlist.objects.filter(
                is_public=True
            )
            qs = qs.distinct()
            # For authenticated, show own + public; filter via query param if needed
            mine = request.GET.get("mine")
            if mine == "1":
                qs = Playlist.objects.filter(user=request.user)
        return Response(
            PlaylistSerializer(qs, many=True, context={"request": request}).data
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)
        s = PlaylistSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        pl = s.save(user=request.user)
        return Response(
            PlaylistSerializer(pl, context={"request": request}).data, status=201
        )


class PlaylistDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk, user):
        pl = get_object_or_404(Playlist, pk=pk)
        if not is_owner_or_public(user, pl):
            return None
        return pl

    def get(self, request, pk):
        pl = self.get_object(pk, request.user)
        if not pl:
            return Response(status=404 if not request.user.is_authenticated else 403)
        return Response(PlaylistSerializer(pl, context={"request": request}).data)

    def patch(self, request, pk):
        pl = get_object_or_404(Playlist, pk=pk)
        if pl.user != request.user:
            return Response(status=403)
        s = PlaylistSerializer(
            pl, data=request.data, partial=True, context={"request": request}
        )
        s.is_valid(raise_exception=True)
        s.save()
        return Response(PlaylistSerializer(pl, context={"request": request}).data)

    def delete(self, request, pk):
        pl = get_object_or_404(Playlist, pk=pk)
        if pl.user != request.user:
            return Response(status=403)
        pl.delete()
        return Response(status=204)


class PlaylistAddSongView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        pl = get_object_or_404(Playlist, pk=pk)
        if pl.user != request.user:
            return Response(status=403)
        provider = request.data.get("provider")
        pid = request.data.get("provider_song_id") or request.data.get("id")
        if not provider or not pid:
            return Response(
                {"detail": "provider and provider_song_id required"}, status=400
            )
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
        if PlaylistSong.objects.filter(playlist=pl, song=song).exists():
            return Response({"detail": "already in playlist"}, status=400)
        max_pos = (
            PlaylistSong.objects.filter(playlist=pl).aggregate(Max("position"))[
                "position__max"
            ]
            or 0
        )
        ps = PlaylistSong.objects.create(playlist=pl, song=song, position=max_pos + 1)
        pl.save(update_fields=["updated_at"])
        return Response({"detail": "added", "position": ps.position}, status=201)


class PlaylistRemoveSongView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, song_id):
        pl = get_object_or_404(Playlist, pk=pk)
        if pl.user != request.user:
            return Response(status=403)
        ps = get_object_or_404(PlaylistSong, playlist=pl, song__id=song_id)
        ps.delete()
        for i, item in enumerate(
            PlaylistSong.objects.filter(playlist=pl).order_by("position"), start=1
        ):
            if item.position != i:
                item.position = i
                item.save(update_fields=["position"])
        return Response(status=204)


class PlaylistReorderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        pl = get_object_or_404(Playlist, pk=pk)
        if pl.user != request.user:
            return Response(status=403)
        order = request.data.get("order")
        if not isinstance(order, list):
            return Response({"detail": "order must be list of song ids"}, status=400)
        for idx, sid in enumerate(order, start=1):
            PlaylistSong.objects.filter(playlist=pl, song__id=sid).update(position=idx)
        return Response({"detail": "reordered"})


class PlaylistDuplicateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        pl = get_object_or_404(Playlist, pk=pk)
        if not (pl.is_public or pl.user == request.user):
            return Response(status=403)
        new = Playlist.objects.create(
            user=request.user,
            name=f"{pl.name} (copy)",
            description=pl.description,
            is_public=False,
        )
        for ps in pl.playlist_songs.order_by("position"):
            PlaylistSong.objects.create(
                playlist=new, song=ps.song, position=ps.position
            )
        return Response(
            PlaylistSerializer(new, context={"request": request}).data, status=201
        )
