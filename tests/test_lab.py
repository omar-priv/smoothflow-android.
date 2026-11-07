import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("universal_lab", ROOT / "tools" / "lab.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LabTests(unittest.TestCase):
    def test_detects_python_stack_and_writes_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "hello.py").write_text("print('hello')\n", encoding="utf-8")
            lab = MODULE.Lab(root, root / ".report", 5)
            lab.check()
            lab.report()
            self.assertTrue((root / ".report" / "report.md").exists())
            self.assertTrue((root / ".report" / "report.json").exists())
            self.assertIn("Python", lab.stacks)

    def test_invalid_python_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "broken.py").write_text("def broken(:\n", encoding="utf-8")
            lab = MODULE.Lab(root, root / ".report", 5)
            lab.check()
            self.assertTrue(any(x["name"] == "Python syntax" and x["status"] == "FAIL"
                                for x in lab.results))


if __name__ == "__main__":
    unittest.main()
