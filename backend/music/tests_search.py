from django.test import TestCase
from unittest.mock import patch
from music.search.normalizer import normalize_query, cache_key
from music.search.ranking import rank_results

class NormTest(TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_query("  ARIJIT   SINGH  "), "arijit singh")
        self.assertEqual(cache_key(" AriJit  Singh ",1,12), cache_key("arijit singh",1,12))
    def test_ranking(self):
        results=[{"title":"Arijit Singh Remix","artist":"A"},{"title":"Arijit Singh","artist":"Arijit Singh"}]
        ranked=rank_results("arijit singh", results)
        self.assertEqual(ranked[0]["title"],"Arijit Singh")
    def test_cache(self):
        from django.core.cache import cache
        from music.services.music_service import search_tracks
        cache.clear()
        with patch("music.services.music_service.AudiusProvider.search_tracks", return_value=[{"title":"x","artist":"y","id":"1","provider":"audius"}]) as m:
            r1=search_tracks("test", limit=12)
            r2=search_tracks("test", limit=12)
            self.assertEqual(m.call_count,1)
            self.assertEqual(r1,r2)
