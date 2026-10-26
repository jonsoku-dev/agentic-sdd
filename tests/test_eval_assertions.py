"""Deterministic checks behind evals/evals.json. Live model runs stay out of CI."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import harness_probe  # noqa: E402
import progress_gate  # noqa: E402


def problems(progress: str, feature: str, tasks: str | None = None) -> list[str]:
    root = Path(tempfile.mkdtemp())
    spec = root / "specs" / feature
    spec.mkdir(parents=True)
    if tasks is not None:
        (spec / "tasks.md").write_text(tasks)
    path = root / "progress.md"
    path.write_text(progress)
    return progress_gate.check(path)


class EvalAssertionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evals = json.loads((ROOT / "evals/evals.json").read_text())["evals"]

    def test_sixteen_cases_have_assertions(self):
        self.assertEqual([case["id"] for case in self.evals], list(range(1, 17)))
        for case in self.evals:
            self.assertTrue(case["prompt"].strip(), case["id"])
            self.assertTrue(case["expected_output"].strip(), case["id"])
            self.assertGreaterEqual(len(case["assertions"]), 3, case["id"])
            for assertion in case["assertions"]:
                self.assertTrue(assertion.strip(), case["id"])

    def test_eval_10_does_not_require_port_only_skills(self):
        case = next(item for item in self.evals if item["id"] == 10)
        self.assertIn("deslop/thermos", " ".join(case["assertions"]))
        self.assertNotIn("deslop", harness_probe.COMMON_CORE)
        self.assertNotIn("thermos", harness_probe.COMMON_CORE)

    def test_eval_13_second_converge_is_refused(self):
        case = next(item for item in self.evals if item["id"] == 13)
        self.assertIn("Does not run a second converge on 006", case["assertions"])
        twice = "# Tasks\n## Convergence\nT001 fixed\n## Convergence\nT002 still failing\n"
        once = "# Tasks\n## Convergence\nT001 fixed\n"
        self.assertTrue(any("Convergence headers" in item for item in problems("", "006-persist", twice)))
        self.assertFalse(any("Convergence headers" in item for item in problems("", "006-persist", once)))

    def test_eval_14_inline_breadcrumb_is_not_a_self_review(self):
        case = next(item for item in self.evals if item["id"] == 14)
        self.assertIn("Records an O-poteto breadcrumb that says inline", case["assertions"])
        closed = (
            "pstack: O-poteto|claude|inline → T020–T022 verified\n"
            "pstack: O-interrogate|claude|pstack:effort-low → 0 findings\n"
            "rea: 008-module|pass|ev_abc123\n"
        )
        found = problems(closed, "008-module")
        self.assertFalse(any("self-review" in item for item in found), found)
        labeled = (
            "pstack: O-interrogate|claude|inline → 0 findings\n"
            "rea: 008-module|pass|ev_abc123\n"
        )
        self.assertTrue(any("self-review" in item for item in problems(labeled, "008-module")))

    def test_eval_16_one_reviewer_closes_and_a_blocked_review_does_not(self):
        case = next(item for item in self.evals if item["id"] == 16)
        self.assertIn("Spawns a separate reviewer subagent at converge", case["assertions"])
        closed = (
            "pstack: O-interrogate|claude|pstack:effort-low → 0 findings\n"
            "rea: 010-subcommand|pass|ev_abc123\n"
        )
        self.assertEqual(problems(closed, "010-subcommand"), [])
        blocked = (
            "pstack: O-interrogate|claude|BLOCKED: independent review\n"
            "rea: 010-subcommand|pass|ev_abc123\n"
        )
        self.assertTrue(any("BLOCKED" in item for item in problems(blocked, "010-subcommand")))
        own = (
            "pstack: O-interrogate|claude|self-review → 0 findings\n"
            "rea: 010-subcommand|pass|ev_abc123\n"
        )
        self.assertTrue(any("self-review" in item for item in problems(own, "010-subcommand")))


if __name__ == "__main__":
    unittest.main()
