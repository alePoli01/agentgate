"""
Regression lock for run_loop_check() in loop.py.
Introduced in Phase 29 to fix the consecutive-fail counter.
Refactored in Phase 40 to mock subprocess.run and avoid system python dependency.

Technical note: run_loop_check() calls sys.exit(exit_code) at the end.
Tests intercept this with assertRaises(SystemExit) and inspect .code.
setUp/tearDown change cwd to a temp dir to avoid writing .ai/LOOP_STATE.md
to the real workspace.
"""
import sys
import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import loop
import tier

class TestRunLoopCheck(unittest.TestCase):

    def setUp(self):
        """Redirect cwd to temp dir so state writes don't touch the real workspace."""
        self.original_cwd = os.getcwd()
        self.tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self.tmpdir.name)
        
        # Mock tier to always return LARGE to avoid hitting MAX_ITERATIONS gate during test
        self.patcher = patch("loop.get_tier_config")
        self.mock_tier = self.patcher.start()
        self.mock_tier.return_value = {
            "tier": "LARGE",
            "max_iterations": 10,
            "darrms_mandatory": False
        }

    def tearDown(self):
        self.patcher.stop()
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    def _state(self):
        with open(os.path.join(".ai", "LOOP_STATE.md"), "r", encoding="utf-8") as f:
            return f.read()

    @patch("loop.subprocess.run")
    def _run(self, cmd, mock_run, exit_code=0, stdout="test stdout", stderr=""):
        """Mock subprocess and run_loop_check, capturing SystemExit."""
        mock_result = MagicMock()
        mock_result.returncode = exit_code
        mock_result.stdout = stdout
        mock_result.stderr = stderr
        mock_run.return_value = mock_result
        
        with self.assertRaises(SystemExit) as ctx:
            loop.run_loop_check(cmd)
        return ctx.exception.code

    # --- Exit code propagation ---

    def test_pass_on_exit_code_zero(self):
        code = self._run('dummy_cmd', exit_code=0)
        self.assertEqual(code, 0)
        self.assertIn("Last result: PASS", self._state())

    def test_fail_on_nonzero_exit_code(self):
        code = self._run('dummy_cmd', exit_code=1)
        self.assertEqual(code, 1)
        self.assertIn("Last result: FAIL", self._state())

    # --- State file content ---

    def test_state_file_created_at_expected_path(self):
        self._run('dummy_cmd', exit_code=0)
        self.assertTrue(os.path.exists(".ai/LOOP_STATE.md"))

    def test_state_contains_command(self):
        self._run('dummy_cmd', exit_code=0)
        self.assertIn('dummy_cmd', self._state())

    # --- Consecutive fail counter (Phase 29 regression) ---

    def test_single_fail_sets_counter_to_one(self):
        self._run('dummy_cmd', exit_code=1)
        self.assertIn("Consecutive fails: 1", self._state())

    def test_two_consecutive_fails_sets_counter_to_two(self):
        self._run('dummy_cmd', exit_code=1)
        self._run('dummy_cmd', exit_code=1)
        self.assertIn("Consecutive fails: 2", self._state())

    def test_pass_resets_counter_to_zero(self):
        self._run('dummy_cmd', exit_code=1)
        self._run('dummy_cmd', exit_code=1)
        self._run('dummy_cmd', exit_code=0)
        self.assertIn("Consecutive fails: 0", self._state())
        self.assertIn("Last result: PASS", self._state())

    def test_iteration_increments_each_run(self):
        for expected in range(1, 4):
            self._run('dummy_cmd', exit_code=0)
            self.assertIn(f"- Iteration: {expected}", self._state())
            
    def test_max_iterations_gate(self):
        # Change tier max_iterations to 2
        self.mock_tier.return_value["max_iterations"] = 2
        
        # Run 1: ok
        self._run('dummy_cmd', exit_code=0)
        # Run 2: ok
        self._run('dummy_cmd', exit_code=0)
        
        # Run 3: should fail with exit code 1 without calling subprocess because iteration=3 > 2
        with patch("loop.subprocess.run") as mock_run:
            with self.assertRaises(SystemExit) as ctx:
                loop.run_loop_check('dummy_cmd')
            self.assertEqual(ctx.exception.code, 1)
            mock_run.assert_not_called()

if __name__ == "__main__":
    unittest.main()
