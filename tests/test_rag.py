"""
Tests for rag.py
"""
import sys
import os
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import rag

class TestRAG(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._orig_search_index = rag.config.SEARCH_INDEX_PATH
        self._orig_embed_cache = rag.config.EMBEDDINGS_CACHE_PATH
        rag.config.SEARCH_INDEX_PATH = os.path.join(self.tmpdir.name, "search_index.json")
        rag.config.EMBEDDINGS_CACHE_PATH = os.path.join(self.tmpdir.name, "embeddings_cache.json")

    def tearDown(self):
        rag.config.SEARCH_INDEX_PATH = self._orig_search_index
        rag.config.EMBEDDINGS_CACHE_PATH = self._orig_embed_cache
        self.tmpdir.cleanup()

    def _write_temp(self, name, content):
        path = os.path.join(self.tmpdir.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_tokenize(self):
        self.assertEqual(rag.tokenize("MyClassMethod"), ["my", "class", "method"])
        self.assertEqual(rag.tokenize("snake_case_func"), ["snake", "case", "func"])
        self.assertEqual(rag.tokenize("UPPERCase"), ["uppercase"])
        self.assertEqual(rag.tokenize("normal word test!"), ["normal", "word", "test"])

    def test_cosine_similarity(self):
        self.assertAlmostEqual(rag.cosine_similarity([1, 0, 0], [1, 0, 0]), 1.0)
        self.assertAlmostEqual(rag.cosine_similarity([1, 0, 0], [0, 1, 0]), 0.0)
        self.assertAlmostEqual(rag.cosine_similarity([1, 0, 0], [-1, 0, 0]), -1.0)
        self.assertEqual(rag.cosine_similarity([0, 0, 0], [1, 1, 1]), 0.0)

    def test_bm25_math(self):
        documents = [
            ("doc1", "apple banana apple"),
            ("doc2", "banana orange"),
            ("doc3", "apple apple apple orange"),
        ]
        idf, tf_map, avg_dl, doc_lengths = rag.build_bm25_index(documents)
        
        self.assertIn("apple", idf)
        self.assertIn("banana", idf)
        
        score1 = rag.bm25_score(["apple"], "doc1", idf, tf_map, avg_dl, doc_lengths)
        score2 = rag.bm25_score(["apple"], "doc2", idf, tf_map, avg_dl, doc_lengths)
        score3 = rag.bm25_score(["apple"], "doc3", idf, tf_map, avg_dl, doc_lengths)
        
        # doc3 has most apples, should score highest
        self.assertTrue(score3 > score1 > score2)
        self.assertEqual(score2, 0.0)

    @patch("rag.get_embedding_ollama")
    def test_query_codebase_bm25_fallback(self, mock_get_embedding):
        # mock returns None to force BM25
        mock_get_embedding.return_value = None
        
        self._write_temp("apple.md", "apple banana")
        self._write_temp("orange.md", "orange grape")
        
        results = rag.query_codebase("apple", top_k=5, root=self.tmpdir.name)
        
        self.assertEqual(len(results), 1)
        self.assertIn("apple.md", results[0]["file"])
        self.assertEqual(results[0]["method"], "bm25")
        
    @patch("rag.get_embedding_ollama")
    def test_query_codebase_ollama(self, mock_get_embedding):
        def mock_embedding(text):
            if "apple" in text:
                return [1.0, 0.0]
            if "grape" in text:
                return [-1.0, 0.0]
            return [0.0, 1.0]
        
        mock_get_embedding.side_effect = mock_embedding
        
        file1 = self._write_temp("apple.md", "apple banana")
        file2 = self._write_temp("orange.md", "orange grape")
        
        results = rag.query_codebase("apple query", top_k=5, root=self.tmpdir.name)
        
        self.assertEqual(len(results), 2)
        # file1 has apple in it, so its vector is [1.0, 0.0]
        # query has apple in it, so its vector is [1.0, 0.0]
        # cosine sim is 1.0
        self.assertEqual(results[0]["file"], file1)
        self.assertEqual(results[0]["method"], "hybrid")
        self.assertTrue(results[0]["score"] > 0)
        
    @patch("rag.query_codebase")
    def test_check_arbiter(self, mock_query):
        path = self._write_temp("target.txt", "target")
        
        mock_query.return_value = [
            {"file": path, "score": 2.0},
            {"file": "other.txt", "score": 1.0}
        ]
        
        # Max score is 2.0, target file score is 2.0. Normalized = 1.0 >= 0.3
        is_relevant, score = rag.check_arbiter("query", path, threshold=0.3)
        self.assertTrue(is_relevant)
        self.assertEqual(score, 1.0)
        
        mock_query.return_value = [
            {"file": "top.txt", "score": 10.0},
            {"file": path, "score": 2.0}
        ]
        # Normalized = 2.0 / 10.0 = 0.2 < 0.3
        is_relevant, score = rag.check_arbiter("query", path, threshold=0.3)
        self.assertFalse(is_relevant)
        self.assertEqual(score, 0.2)

if __name__ == "__main__":
    unittest.main()
