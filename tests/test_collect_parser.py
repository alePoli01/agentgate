"""
Regression lock for the ROW_PATTERN regex in orchestrator.py (--collect branch).
Introduced in Phase 30 to fix silent payload corruption when | appears in message text.

If these tests fail after a change to orchestrator.py, the collect parser was broken.

Lifecycle: update this file if ROW_PATTERN changes. Delete if --collect is removed.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from whiteboard import ROW_PATTERN  # imports the live definition, never a stale copy


class TestRowPatternHappyPath(unittest.TestCase):

    def test_clean_tell_row_extracts_all_fields(self):
        line = "| T-1234 | 2024-01-01 12:00:00 | TELL | CODER: task done | COMPLETE |"
        m = ROW_PATTERN.match(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group("payload"), "CODER: task done")
        self.assertEqual(m.group("verb"), "TELL")
        self.assertEqual(m.group("ts"), "2024-01-01 12:00:00")

    def test_ask_verb_matches(self):
        line = "| T-1234 | 2024-01-01 12:00:00 | ASK | PLANNER: what is next? | COMPLETE |"
        m = ROW_PATTERN.match(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group("verb"), "ASK")

    def test_case_insensitive_complete(self):
        line = "| T-1234 | 2024-01-01 12:00:00 | tell | CODER: done | complete |"
        m = ROW_PATTERN.match(line)
        self.assertIsNotNone(m)


class TestRowPatternPipeInPayload(unittest.TestCase):
    """
    Regression cases for the original split("|") bug.
    These inputs would silently return the wrong payload before Phase 30.
    """

    def test_single_pipe_in_payload_preserved(self):
        # Before Phase 30: split("|") would return "CODER: config" instead of full payload
        line = "| T-1234 | 2024-01-01 12:00:00 | TELL | CODER: config|settings updated | COMPLETE |"
        m = ROW_PATTERN.match(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group("payload"), "CODER: config|settings updated")

    def test_multiple_pipes_in_payload_preserved(self):
        line = "| T-1234 | 2024-01-01 12:00:00 | TELL | CODER: a|b|c result | COMPLETE |"
        m = ROW_PATTERN.match(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group("payload"), "CODER: a|b|c result")


class TestRowPatternRejectsInvalid(unittest.TestCase):

    def test_unknown_verb_rejected(self):
        line = "| T-1234 | 2024-01-01 | GARBAGE | something | COMPLETE |"
        self.assertIsNone(ROW_PATTERN.match(line))

    def test_missing_complete_marker_rejected(self):
        line = "| T-1234 | 2024-01-01 12:00:00 | TELL | CODER: done | PENDING |"
        self.assertIsNone(ROW_PATTERN.match(line))


class TestRowPatternMultiRow(unittest.TestCase):

    def test_last_complete_row_selected(self):
        """Multi-row collection must pick the last (most recent) row."""
        rows = [
            "| T-1234 | 2024-01-01 10:00:00 | TELL | CODER: first result | COMPLETE |",
            "| T-1234 | 2024-01-01 11:00:00 | TELL | CODER: second result | COMPLETE |",
        ]
        collected = []
        for line in rows:
            if "| COMPLETE |" not in line:
                continue
            m = ROW_PATTERN.match(line.strip())
            if m:
                collected.append(m.group("payload").strip())
        self.assertEqual(len(collected), 2)
        self.assertEqual(collected[-1], "CODER: second result")


if __name__ == "__main__":
    unittest.main()
