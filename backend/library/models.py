from django.db import models
from django.contrib.auth.models import User
from music.models import Song


class LikedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_songs")
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "song")]
        indexes = [models.Index(fields=["user"])]


class RecentlyPlayed(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recent_songs"
    )
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-played_at"]
        indexes = [models.Index(fields=["user", "-played_at"])]


class SavedAlbum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.CharField(max_length=300)
    artist = models.CharField(max_length=300, blank=True)

    class Meta:
        unique_together = [("user", "album")]


class SavedArtist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.CharField(max_length=300)

    class Meta:
        unique_together = [("user", "artist")]
