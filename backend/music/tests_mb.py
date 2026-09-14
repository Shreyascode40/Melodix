from django.test import TestCase
from unittest.mock import patch, MagicMock
from music.search.normalizer import normalize_query
from music.search.matcher import match_song
from music.services import musicbrainz

class MBTest(TestCase):
    def test_unicode_preserve(self):
        self.assertEqual(normalize_query("  Kesariya  "), "kesariya")
        self.assertEqual(normalize_query("अरिजीत सिंह"), "अरिजीत सिंह")
    def test_remix_penalty(self):
        mb={"title":"Kesariya","artist":"Arijit Singh","duration":268000}
        cand={"title":"Kesariya Remix","artist":"Arijit Singh","duration":268}
        s=match_song(mb, cand)
        cand2={"title":"Kesariya","artist":"Arijit Singh","duration":268}
        s2=match_song(mb, cand2)
        self.assertTrue(s2["score"] > s["score"])
    def test_exact(self):
        mb={"title":"Kesariya","artist":"Arijit Singh","duration":268000}
        cand={"title":"Kesariya","artist":"Arijit Singh","duration":268}
        self.assertEqual(match_song(mb, cand)["status"],"high")
    def test_fallback(self):
        from django.core.cache import cache
        cache.clear()
        with patch("music.services.music_service.AudiusProvider.search_tracks", return_value=[{"id":"1","title":"Kesariya","artist":"Arijit Singh","cover_url":"","duration":268,"stream_url":"http://x","provider":"audius"}]):
            with patch("music.services.musicbrainz.search_recordings", return_value=[]):
                from music.services.music_service import search_enriched
                r=search_enriched("kesariya", limit=2)
                self.assertTrue(len(r)>=1)
    def test_mb_cache(self):
        from django.core.cache import cache
        cache.clear()
        mock_resp=MagicMock(status_code=200, json=lambda: {"recordings":[{"id":"m1","title":"Kesariya","artist-credit":[{"name":"Arijit Singh"}],"length":268000,"isrcs":[]}]})
        with patch("music.services.musicbrainz.get_session") as gs:
            gs.return_value.get.return_value=mock_resp
            r1=musicbrainz.search_recordings("kesariya")
            r2=musicbrainz.search_recordings("kesariya")
            self.assertEqual(gs.return_value.get.call_count,1)
