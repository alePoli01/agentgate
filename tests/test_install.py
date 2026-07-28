"""
Tests for install.py
"""
import sys
import os
import unittest
import tempfile
import subprocess
import json

class TestInstaller(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.install_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "install.py"))

    def tearDown(self):
        self.tmpdir.cleanup()

    def run_install(self, *args):
        cmd = [sys.executable, self.install_script] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_install_fresh(self):
        result = self.run_install(self.tmpdir.name)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir.name, ".ai", "registry.json")))
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir.name, ".ai", "src", "orchestrator.py")))

    def test_install_missing_args(self):
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("usage:" in result.stdout.lower() or "usage:" in result.stderr.lower())

    def test_install_invalid_target(self):
        result = self.run_install("/mock/invalid/path/that/does/not/exist")
        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        self.assertIn("Error:", output)

    def test_install_upgrade_preserves_registry(self):
        # 1. Fresh install
        self.run_install(self.tmpdir.name)
        
        # 2. Modify registry
        reg_path = os.path.join(self.tmpdir.name, ".ai", "registry.json")
        with open(reg_path, "w") as f:
            json.dump({"valid_agents": ["CUSTOM"]}, f)
            
        # 3. Upgrade
        result = self.run_install(self.tmpdir.name, "--upgrade")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Upgrade complete", result.stdout)
        
        # 4. Verify registry was not overwritten
        with open(reg_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["valid_agents"], ["CUSTOM"])

    def test_install_upgrade_nonexistent(self):
        result = self.run_install(self.tmpdir.name, "--upgrade")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Not installed", result.stdout)

    def test_install_uninstall_requires_yes(self):
        # 1. Fresh install
        self.run_install(self.tmpdir.name)
        
        # 2. Try uninstall without --yes
        result = self.run_install(self.tmpdir.name, "--uninstall")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Pass --yes to confirm", result.stdout)
        
        # 3. Verify it was not deleted
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir.name, ".ai")))

    def test_install_uninstall_with_yes(self):
        # 1. Fresh install
        self.run_install(self.tmpdir.name)
        
        # 2. Try uninstall with --yes
        result = self.run_install(self.tmpdir.name, "--uninstall", "--yes")
        self.assertEqual(result.returncode, 0)
        self.assertIn("AgentGate uninstalled", result.stdout)
        
        # 3. Verify it was deleted
        self.assertFalse(os.path.exists(os.path.join(self.tmpdir.name, ".ai")))

    def test_install_uninstall_self_protection(self):
        repo_root = os.path.dirname(self.install_script)
        result = self.run_install(repo_root, "--uninstall", "--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing to uninstall the development repository", result.stdout)

if __name__ == "__main__":
    unittest.main()
