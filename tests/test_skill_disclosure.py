"""SKILL.md keeps the rules a run follows and leaves phase procedure on the card."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillDisclosureTests(unittest.TestCase):
    def test_entrypoint_keeps_gates_and_points_at_the_card(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertLess(len(text.splitlines()), 180)
        for needle in (
            "scripts/progress_gate.py",
            "one independent verifier",
            "ScheduleWakeup",
            "Implement inline",
            "rea-agents@6.7.0",
            "## Hard boundaries",
            "| **Claude Code** |",
            "column 1",
        ):
            self.assertIn(needle, text)
        self.assertIn("Do not read [phase-contract.md](references/phase-contract.md) on every phase.", text)
        self.assertNotIn("when entering a phase", text)


if __name__ == "__main__":
    unittest.main()
