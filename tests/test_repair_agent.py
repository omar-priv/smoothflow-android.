import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.repair_agent import extract_patch, patch_paths, _is_forbidden, redact


class RepairAgentSafetyTests(unittest.TestCase):
    def test_extracts_unified_diff_from_fence(self):
        fence = chr(96) * 3
        raw = (
            fence + "diff\n"
            "diff --git a/src/app.py b/src/app.py\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
            "@@ -1 +1 @@\n"
            "-old\n+new\n"
            + fence
        )
        self.assertTrue(extract_patch(raw).startswith("diff --git"))

    def test_patch_paths_returns_changed_file(self):
        patch = (
            "diff --git a/src/app.py b/src/app.py\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
        )
        self.assertEqual(patch_paths(patch), ["src/app.py"])

    def test_rejects_deletions(self):
        with self.assertRaises(ValueError):
            patch_paths("diff --git a/src/app.py b/src/app.py\n+++ /dev/null\n")

    def test_blocks_workflows_secrets_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertTrue(_is_forbidden(".github/workflows/test.yml", root))
            self.assertTrue(_is_forbidden("../outside.py", root))
            self.assertTrue(_is_forbidden(".env.production", root))
            self.assertFalse(_is_forbidden("src/fix.py", root))

    def test_existing_tests_are_immutable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tests").mkdir()
            (root / "tests" / "test_old.py").write_text("assert True", encoding="utf-8")
            self.assertTrue(_is_forbidden("tests/test_old.py", root))
            self.assertFalse(_is_forbidden("tests/test_new.py", root))

    def test_redacts_tokens_and_credentials(self):
        value = "api_key=secret-value Bearer abcdef ghp_abcdefghijklmnopqrstuvwxyz"
        cleaned = redact(value)
        self.assertNotIn("secret-value", cleaned)
        self.assertNotIn("ghp_abcdefghijklmnopqrstuvwxyz", cleaned)
        self.assertIn("[REDACTED]", cleaned)


if __name__ == "__main__":
    unittest.main()
