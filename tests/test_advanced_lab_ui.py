"""Static smoke tests for the independently served ADVANCED LAB page."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


PAGE = Path(__file__).resolve().parents[1] / "advanced-lab.html"


class AdvancedLabUiTests(unittest.TestCase):
    def test_source_and_definitions_present(self):
        page = PAGE.read_text(encoding="utf-8")
        for marker in ('fetch("./data/stats.json"', "Official Stats",
                       "DEF RTG", "TOV%*", "eFG%*", "TS%*",
                       "3PAr%*", "FTr%*", "OPP TOV%"):
            with self.subTest(marker=marker):
                self.assertIn(marker, page)
        self.assertNotIn("impactmetrics.jp", page)

    def test_inline_javascript_syntax(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node executable unavailable")
        page = PAGE.read_text(encoding="utf-8")
        match = re.search(r"<script>(.*?)</script>", page, re.DOTALL)
        self.assertIsNotNone(match)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "advanced-lab.js"
            path.write_text(match.group(1), encoding="utf-8")
            result = subprocess.run([node, "--check", str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
