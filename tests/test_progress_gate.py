#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from progress_gate import check

GOOD = """# Progress
pstack: O-poteto|claude|inline → T001–T004 verified
pstack: O-interrogate|claude|pstack:effort-medium → 2 findings
rea: 001-todo-edit|pass|ev_adf6e4ce87099f67
"""


class ProgressGateTest(unittest.TestCase):
    def run_gate(self, text: str, features=("001-todo-edit",)) -> list[str]:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for f in features:
                (root / "specs" / f).mkdir(parents=True)
            (root / "progress.md").write_text(text)
            return check(root / "progress.md")

    def test_complete_gate_passes(self):
        self.assertEqual(self.run_gate(GOOD), [])

    def test_bulleted_and_backticked_lines_are_reported(self):
        text = GOOD.replace("pstack: O-interrogate", "- `pstack: O-interrogate").replace("findings\n", "findings`\n", 1)
        problems = self.run_gate(text)
        self.assertTrue(any("column 1" in p for p in problems))
        self.assertTrue(any(p.startswith("missing: pstack: O-interrogate") for p in problems))

    def test_every_feature_needs_a_rea_pass_line(self):
        problems = self.run_gate(GOOD, features=("001-todo-edit", "002-errors"))
        self.assertEqual(problems, ["missing: rea: 002-errors|pass|<ev_… id copied verbatim>"])

    def test_blocked_review_keeps_gate_open(self):
        text = GOOD.replace("pstack:effort-medium → 2 findings", "BLOCKED: independent review")
        self.assertIn("review is BLOCKED: independent review; the Final Goal stays open", self.run_gate(text))


if __name__ == "__main__":
    unittest.main()
