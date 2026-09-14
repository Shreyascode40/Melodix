from django.db import models
from django.contrib.auth.models import User
from music.models import Song


def playlist_cover_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"playlists/{instance.id}.{ext}"


class Playlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="playlists", db_index=True
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to=playlist_cover_path, blank=True, null=True
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["user"])]

    def __str__(self):
        return self.name


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="playlist_songs", db_index=True
    )
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]
        unique_together = [("playlist", "song")]
        indexes = [models.Index(fields=["playlist", "position"])]

    def __str__(self):
        return f"{self.playlist.name} - {self.song.title}"
