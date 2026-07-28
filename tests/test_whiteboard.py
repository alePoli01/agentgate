"""
Tests for whiteboard.py
"""
import sys
import os
import unittest
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import whiteboard

class TestWhiteboard(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = os.path.join(self.tmpdir.name, "SUBAGENT_STATE.md")
        
        # Patch the SUBAGENT_STATE_PATH inside the whiteboard module
        self.patcher = patch("whiteboard.SUBAGENT_STATE_PATH", self.state_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmpdir.cleanup()

    def test_process_verb_invalid(self):
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.process_verb("INVALID", "payload")
        self.assertEqual(ctx.exception.code, 1)
        
    def test_process_verb_no_payload(self):
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.process_verb("ASK", "")
        self.assertEqual(ctx.exception.code, 1)

    def test_process_verb_success(self):
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.process_verb("ASK", "Do the task")
        self.assertEqual(ctx.exception.code, 0)
        
        self.assertTrue(os.path.exists(self.state_path))
        with open(self.state_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("| Timestamp | Verb | Payload | Status |", content)
        self.assertIn("| ASK | Do the task | PENDING |", content)

    @patch("whiteboard.VALID_AGENTS", ["RESEARCHER", "CODER"])
    @patch("briefing.generate_briefing_block")
    def test_route_subagent_success(self, mock_briefing):
        # Setup pending state
        with self.assertRaises(SystemExit):
            whiteboard.process_verb("ASK", "Do the task")
            
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.route_subagent("ROUTE_TO_CODER")
        self.assertEqual(ctx.exception.code, 0)
        
        mock_briefing.assert_called_once_with("CODER", "Do the task")

    @patch("whiteboard.VALID_AGENTS", ["RESEARCHER", "CODER"])
    def test_route_subagent_invalid_agent(self):
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.route_subagent("ROUTE_TO_INVALID")
        self.assertEqual(ctx.exception.code, 1)

    def test_route_subagent_no_state(self):
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.route_subagent("ROUTE_TO_CODER")
        self.assertEqual(ctx.exception.code, 1)

    def test_collect_subagent_result_no_state(self):
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.collect_subagent_result()
        self.assertEqual(ctx.exception.code, 0)  # it exits cleanly if no result found

    def test_collect_subagent_result_success(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            f.write("| Timestamp | Verb | Payload | Status |\n")
            f.write("|---|---|---|---|\n")
            f.write("| 2026-01-01 12:00:00 | TELL | RESEARCHER: Found info | COMPLETE |\n")
            
        # collect_subagent_result prints and sys.exit(0)
        with self.assertRaises(SystemExit) as ctx:
            whiteboard.collect_subagent_result()
        self.assertEqual(ctx.exception.code, 0)

if __name__ == "__main__":
    unittest.main()
