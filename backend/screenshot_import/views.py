from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from playlists.models import Playlist, PlaylistSong
from playlists.serializers import PlaylistSerializer
from music.models import Song
from .services.image_processor import validate_image, preprocess
from .services.ocr import extract_lines
from .services.song_extractor import extract_candidates
from .services.song_matcher import match_candidates


class ScreenshotAnalyzeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        f = request.FILES.get("image")
        if not f:
            return Response({"detail": "image required"}, status=400)
        try:
            validate_image(f)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        try:
            raw = f.read()
            if not raw or len(raw) < 100:
                return Response({"detail": "Empty or corrupted image"}, status=400)
            try:
                pre = preprocess(raw)
            except Exception as e:
                return Response({"detail": f"Image processing failed: {e}"}, status=422)
            lines = extract_lines(pre)
            if not lines:
                try:
                    lines = extract_lines(raw)
                except:
                    lines = []
            if not lines:
                return Response(
                    {
                        "detail": "OCR found no text — try a clearer screenshot (avoid stylized fonts, ensure 720p+, light background or will auto-invert dark UI). You can still manually type songs below",
                        "lines": [],
                        "hint": "Tesseract installed but text too small/blurry; try cropping to song list only",
                    },
                    status=422,
                )
            cands = extract_candidates(lines)
            if not cands:
                return Response(
                    {"detail": "no songs detected", "lines": lines}, status=422
                )
            matched = match_candidates(cands)
            return Response({"lines": lines, "candidates": cands, "matched": matched})
        except Exception as e:
            return Response(
                {"detail": "processing failed", "error": str(e)}, status=500
            )


class ScreenshotConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name = request.data.get("name") or "Screenshot Playlist"
        description = request.data.get("description", "")
        songs = request.data.get("songs", [])
        if not songs:
            return Response({"detail": "songs required"}, status=400)
        pl = Playlist.objects.create(
            user=request.user, name=name, description=description
        )
        for idx, s in enumerate(songs, start=1):
            provider = s.get("provider") or "audius"
            pid = (
                s.get("id")
                or s.get("provider_song_id")
                or s.get("provider_id")
                or s.get("musicbrainz_id")
            )
            if not pid:
                pid = f"manual-{s.get('title', 'unknown')[:30]}-{s.get('artist', '')[:20]}".lower().replace(
                    " ", "-"
                )
                provider = provider if provider != "audius" or not pid else "detected"
            if not provider:
                provider = "detected"
            song, _ = Song.objects.get_or_create(
                provider=provider,
                provider_song_id=str(pid),
                defaults={
                    "title": s.get("title", "Unknown"),
                    "artist": s.get("artist", "Unknown"),
                    "album": s.get("album", ""),
                    "cover_url": s.get("cover_url", ""),
                    "duration": s.get("duration", 0),
                    "stream_url": s.get("stream_url", ""),
                },
            )
            PlaylistSong.objects.create(playlist=pl, song=song, position=idx)
        return Response(
            PlaylistSerializer(pl, context={"request": request}).data, status=201
        )
