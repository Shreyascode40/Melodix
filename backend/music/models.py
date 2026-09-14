from django.db import models


class Song(models.Model):
    provider = models.CharField(max_length=20, db_index=True)
    provider_song_id = models.CharField(max_length=200)
    title = models.CharField(max_length=300, db_index=True)
    artist = models.CharField(max_length=300, db_index=True)
    album = models.CharField(max_length=300, blank=True)
    cover_url = models.URLField(blank=True)
    duration = models.IntegerField(null=True, blank=True)
    stream_url = models.URLField(blank=True)
    language = models.CharField(max_length=30, blank=True)

    class Meta:
        unique_together = [("provider", "provider_song_id")]
        indexes = [
            models.Index(fields=["provider", "provider_song_id"]),
            models.Index(fields=["title"]),
            models.Index(fields=["artist"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.artist}"
