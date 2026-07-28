"""
Tests for tier.py
"""
import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import tier

class TestTierEngine(unittest.TestCase):

    @patch("tier.os.path.exists")
    def test_missing_model_env(self, mock_exists):
        mock_exists.return_value = False
        config = tier.parse_model_env()
        self.assertEqual(config["context_window"], 8000)
        self.assertFalse(config["parallel_subagents"])

    @patch("tier.os.path.exists")
    @patch("tier.safe_read")
    def test_parse_model_env_valid(self, mock_read, mock_exists):
        mock_exists.return_value = True
        mock_read.return_value = "context_window: 128000\nparallel_subagents: true\ncost_aware: false\nmodel_type: cloud"
        
        config = tier.parse_model_env()
        self.assertEqual(config["context_window"], 128000)
        self.assertTrue(config["parallel_subagents"])
        self.assertFalse(config["cost_aware"])
        self.assertEqual(config["model_type"], "cloud")

    @patch("tier.os.path.exists")
    @patch("tier.safe_read")
    def test_parse_model_env_with_comments_and_spaces(self, mock_read, mock_exists):
        mock_exists.return_value = True
        mock_read.return_value = "  context_window:   32000  # inline comment \n  parallel_subagents: False\n"
        
        config = tier.parse_model_env()
        self.assertEqual(config["context_window"], 32000)
        self.assertFalse(config["parallel_subagents"])
        
    @patch("tier.os.path.exists")
    @patch("tier.safe_read")
    def test_parse_model_env_malformed_values(self, mock_read, mock_exists):
        mock_exists.return_value = True
        mock_read.return_value = "context_window: N/A\n"
        
        config = tier.parse_model_env()
        # Should fallback to default 8000
        self.assertEqual(config["context_window"], 8000)

    def test_resolve_tier(self):
        self.assertEqual(tier.resolve_tier(8000), "SMALL")
        self.assertEqual(tier.resolve_tier(31999), "SMALL")
        self.assertEqual(tier.resolve_tier(32000), "MEDIUM")
        self.assertEqual(tier.resolve_tier(100000), "MEDIUM")
        self.assertEqual(tier.resolve_tier(127999), "MEDIUM")
        self.assertEqual(tier.resolve_tier(128000), "LARGE")
        self.assertEqual(tier.resolve_tier(2000000), "LARGE")

if __name__ == "__main__":
    unittest.main()
