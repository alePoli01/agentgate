"""
Tests for orchestrator.py (Integration)
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import orchestrator

class TestIntegration(unittest.TestCase):

    @patch("orchestrator.print_tier_info")
    def test_tier_info_flag(self, mock_print):
        with patch.object(sys, 'argv', ['orchestrator.py', '--tier-info']):
            with self.assertRaises(SystemExit) as ctx:
                orchestrator.main()
            self.assertEqual(ctx.exception.code, 0)
            mock_print.assert_called_once()

    @patch("orchestrator.run_health_check")
    def test_health_check_flag(self, mock_health):
        with patch.object(sys, 'argv', ['orchestrator.py', '--health-check']):
            with self.assertRaises(SystemExit) as ctx:
                orchestrator.main()
            self.assertEqual(ctx.exception.code, 0)
            mock_health.assert_called_once()
            
    @patch("rag.query_codebase")
    def test_query_flag(self, mock_query):
        # mock query to prevent real RAG execution
        mock_query.return_value = []
        with patch.object(sys, 'argv', ['orchestrator.py', '--query', 'test query']):
            with self.assertRaises(SystemExit) as ctx:
                orchestrator.main()
            self.assertEqual(ctx.exception.code, 0)
            mock_query.assert_called_once_with('test query')

    @patch("orchestrator.collapse_file_darrrms")
    def test_focus_flag(self, mock_collapse):
        mock_collapse.return_value = "collapsed text"
        with patch.object(sys, 'argv', ['orchestrator.py', '--focus', 'test.py']):
            with self.assertRaises(SystemExit) as ctx:
                orchestrator.main()
            self.assertEqual(ctx.exception.code, 0)
            mock_collapse.assert_called_once_with('test.py')

if __name__ == "__main__":
    unittest.main()
