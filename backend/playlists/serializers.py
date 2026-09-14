from rest_framework import serializers
from .models import Playlist, PlaylistSong
from music.models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = [
            "id",
            "provider",
            "provider_song_id",
            "title",
            "artist",
            "album",
            "cover_url",
            "duration",
            "stream_url",
            "language",
        ]


class PlaylistSongSerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)

    class Meta:
        model = PlaylistSong
        fields = ["id", "song", "position", "added_at"]


class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    song_count = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = [
            "id",
            "user",
            "name",
            "description",
            "cover_image",
            "cover_url",
            "is_public",
            "song_count",
            "songs",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_cover_url(self, obj):
        if obj.cover_image:
            r = self.context.get("request")
            return (
                r.build_absolute_uri(obj.cover_image.url) if r else obj.cover_image.url
            )
        return None

    def get_song_count(self, obj):
        return obj.playlist_songs.count()

    def get_songs(self, obj):
        qs = obj.playlist_songs.select_related("song").order_by("position")
        return PlaylistSongSerializer(qs, many=True).data

    def validate_cover_image(self, v):
        if v and v.size > 3 * 1024 * 1024:
            raise serializers.ValidationError("Max 3MB")
        return v
