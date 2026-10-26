import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LlmsTxtTests(unittest.TestCase):
    def test_generated_files_are_current_and_links_resolve(self):
        p = subprocess.run([sys.executable, str(ROOT / "scripts/build_llms.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        text = (ROOT / "llms.txt").read_text()
        self.assertTrue(text.startswith("# agentic-sdd\n\n> "))
        links = re.findall(r"\]\(https://raw\.githubusercontent\.com/jonsoku-dev/agentic-sdd/main/([^)]+)\)", text)
        self.assertGreater(len(links), 20)
        for rel in links:
            self.assertTrue((ROOT / rel).is_file(), rel)
        full = (ROOT / "llms-full.txt").read_text()
        self.assertIn("<!-- file: SKILL.md -->", full)
        self.assertIn("Do not paste it into a system prompt", text)
        self.assertIn("do not paste this file into a system prompt", full)
        self.assertIn("<!-- file: references/pstack-integration.md -->", full)


if __name__ == "__main__":
    unittest.main()
