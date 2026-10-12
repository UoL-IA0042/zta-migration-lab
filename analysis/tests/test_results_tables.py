"""results_tables.py runs on the committed data and produces every section.

Run from analysis/:  python3 -m unittest discover -s tests
"""
import os
import subprocess
import sys
import tempfile
import unittest

ANALYSIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ResultsTables(unittest.TestCase):
    def test_all_sections_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "t.md")
            subprocess.run([sys.executable, os.path.join(ANALYSIS, "results_tables.py"), "--out", out],
                           check=True, capture_output=True)
            text = open(out).read()
        for heading in ("## Verification: access test matrix", "## Verification: performance per access path",
                        "## Effort: journal hours", "## Defects and unplanned work",
                        "## Size: code lines per component and tag", "## Rule-to-policy translation",
                        "### Consistency checks", "### Breadth at the network layer"):
            self.assertIn(heading, text)
        self.assertIn("| phase-2-netbird | remote-analyst | 2 | 15 | 1 | 0 | 93.8% |", text)


if __name__ == "__main__":
    unittest.main()
