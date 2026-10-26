"""The default converge review is one verifier, with a recorded way back."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReviewDefaultTests(unittest.TestCase):
    def test_live_docs_spawn_one_verifier(self):
        integration = (ROOT / "references/pstack-integration.md").read_text()
        self.assertIn("one independent verifier", integration)
        self.assertIn("### Restoring a wider review panel", integration)
        self.assertIn("docs/evals/2026-10-25-perfect", integration)
        self.assertIn("C1–C9", integration)
        self.assertIn("at least twice", integration)
        self.assertNotIn("2 reviewers, different families", integration)
        self.assertNotIn("sheet default (4)", integration)

        for rel in (
            "references/cost-modes.md",
            "references/model-routing.md",
            "references/multi-perspective-review.md",
            "references/single-loop-default.md",
            "references/phase-card.md",
            "references/harness-layers.md",
            "README.md",
            "SKILL.md",
        ):
            text = (ROOT / rel).read_text()
            self.assertNotIn("two-to-four", text, rel)
            self.assertNotIn("spawn at least two", text, rel)
            self.assertNotIn("2-reviewer", text, rel)


if __name__ == "__main__":
    unittest.main()
