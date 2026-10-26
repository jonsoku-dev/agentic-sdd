#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from progress_gate import check, claims_met

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

    def test_every_in_scope_feature_needs_a_closing_rea_line(self):
        problems = self.run_gate(GOOD, features=("001-todo-edit", "002-errors"))
        self.assertEqual(len(problems), 1)
        self.assertIn("rea: 002-errors|pass|", problems[0])
        self.assertIn("not-applicable", problems[0])

    def test_blocked_limitation_does_not_close(self):
        text = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|blocked-limitation|rea CLI missing",
        )
        self.assertTrue(any("001-todo-edit" in p for p in self.run_gate(text)))

    def test_not_applicable_closes_when_a_reason_is_recorded(self):
        text = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|not-applicable|docs-only, no runnable artifact",
        )
        self.assertEqual(self.run_gate(text), [])
        bare = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|not-applicable|",
        )
        self.assertTrue(any("not-applicable" in p for p in self.run_gate(bare)))

    def test_exclude_drops_a_spec_that_predates_the_goal(self):
        text = GOOD + "gate: exclude|000-legacy|predates this Final Goal; closed before agentic-sdd\n"
        self.assertEqual(self.run_gate(text, features=("001-todo-edit", "000-legacy")), [])
        self.assertTrue(any("names no feature" in p for p in self.run_gate(text + "gate: exclude|missing|old\n")))

    def test_overview_scaffold_is_not_a_feature(self):
        self.assertEqual(self.run_gate(GOOD, features=("001-todo-edit", "000-overview")), [])

    def test_self_review_does_not_pass_as_independent(self):
        for line in ("pstack: O-interrogate|claude|primary self-review, user-directed (no subagent spawned) → 0 findings",
                     "pstack: O-interrogate|codex|inline → self-check against FR list"):
            text = GOOD.replace("pstack: O-interrogate|claude|pstack:effort-medium → 2 findings", line)
            self.assertTrue(any("self-review" in p for p in self.run_gate(text)), line)

    def test_secret_shapes_are_flagged_but_evidence_ids_are_not(self):
        leaked = GOOD + "harness: token ghp_" + "a" * 36 + "\n"
        self.assertTrue(any("looks like a secret" in p for p in self.run_gate(leaked)))
        self.assertEqual(self.run_gate(GOOD.replace("ev_adf6e4ce87099f67", "ev_" + "ab12" * 16)), [])

    def test_claims_met_ignores_negations(self):
        self.assertTrue(claims_met("Status: Final Goal met — specs closed"))
        self.assertTrue(claims_met("The Final Goal is met."))
        self.assertFalse(claims_met("Final Goal NOT met: the user forbade subagents"))
        self.assertFalse(claims_met("## Final Goal\nAdd todo edit (done when tests pass)."))

    def test_more_than_twelve_tasks_and_a_second_converge_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            feature = root / "specs" / "001-todo-edit"
            feature.mkdir(parents=True)
            tasks = "\n".join(f"- [ ] T{i:03d} do the thing" for i in range(1, 14))
            tasks += "\n## Phase 6: Convergence\n## Phase 8: Convergence\n"
            (feature / "tasks.md").write_text(tasks)
            (root / "progress.md").write_text(GOOD)
            problems = check(root / "progress.md")
        self.assertTrue(any("13 tasks" in p for p in problems))
        self.assertTrue(any("2 Convergence headers" in p for p in problems))

    def test_twelve_tasks_and_one_converge_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            feature = root / "specs" / "001-todo-edit"
            feature.mkdir(parents=True)
            tasks = "\n".join(f"- [x] T{i:03d} do the thing" for i in range(1, 13))
            tasks += "\n## Phase 6: Convergence\n"
            (feature / "tasks.md").write_text(tasks)
            (root / "progress.md").write_text(GOOD)
            self.assertEqual(check(root / "progress.md"), [])

    def test_excluded_feature_skips_the_task_limit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            feature = root / "specs" / "000-legacy"
            feature.mkdir(parents=True)
            (feature / "tasks.md").write_text("\n".join(f"- [ ] T{i:03d} old" for i in range(1, 20)))
            (root / "progress.md").write_text(GOOD + "gate: exclude|000-legacy|predates this Final Goal\n")
            self.assertEqual(check(root / "progress.md"), [])

    def test_a_second_worktree_is_a_leftover(self):
        if shutil.which("git") is None:
            self.skipTest("git missing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            root.mkdir()
            quiet = {"cwd": root, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            subprocess.check_call(["git", "init"], **quiet)
            subprocess.check_call(["git", "config", "user.email", "t@example.com"], cwd=root)
            subprocess.check_call(["git", "config", "user.name", "t"], cwd=root)
            (root / "README").write_text("x\n")
            subprocess.check_call(["git", "add", "README"], **quiet)
            subprocess.check_call(["git", "commit", "-m", "init"], **quiet)
            extra = Path(d) / "extra"
            subprocess.check_call(["git", "worktree", "add", "-b", "leaf", str(extra), "HEAD"], **quiet)
            (root / "specs" / "001-todo-edit").mkdir(parents=True)
            (root / "progress.md").write_text(GOOD)
            problems = check(root / "progress.md")
        self.assertTrue(any("leftover git worktree" in p for p in problems), problems)

    def test_blocked_review_keeps_gate_open(self):
        text = GOOD.replace("pstack:effort-medium → 2 findings", "BLOCKED: independent review")
        self.assertIn("review is BLOCKED: independent review; the Final Goal stays open", self.run_gate(text))


if __name__ == "__main__":
    unittest.main()
