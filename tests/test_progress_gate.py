#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from progress_gate import check, claims_met, clear_met_claim, refusal_key, stuck_message

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
        short = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|not-applicable|no binary",
        )
        self.assertEqual(self.run_gate(short), [])
        bare = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|not-applicable|",
        )
        self.assertTrue(any("not-applicable" in p for p in self.run_gate(bare)))
        for placeholder in ("n/a", "N/A", "na", "none", "tbd", "todo", "...", "placeholder"):
            line = GOOD.replace(
                "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
                f"rea: 001-todo-edit|not-applicable|{placeholder}",
            )
            problems = self.run_gate(line)
            self.assertTrue(any("placeholder" in p or "real reason" in p for p in problems), placeholder)
            self.assertNotEqual(problems, [], placeholder)

    def test_exclude_does_not_apply_to_the_active_feature(self):
        only = (
            "pstack: O-interrogate|claude|pstack:effort-medium → 2 findings\n"
            "gate: exclude|001-todo-edit|old\n"
        )
        problems = self.run_gate(only)
        self.assertTrue(any("active feature" in p for p in problems), problems)
        self.assertTrue(any("001-todo-edit" in p for p in problems), problems)
        later = GOOD + "gate: exclude|002-next|old\n"
        problems = self.run_gate(later, features=("001-todo-edit", "002-next"))
        self.assertTrue(any("active feature" in p and "002-next" in p for p in problems), problems)
        older = GOOD.replace("001-todo-edit", "002-next") + "gate: exclude|001-todo-edit|predates this Final Goal\n"
        self.assertEqual(self.run_gate(older, features=("001-todo-edit", "002-next")), [])

    def test_blocked_limitation_is_not_cleared_by_a_later_pass(self):
        blocked_then_pass = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|blocked-limitation|rea CLI missing\n"
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
        )
        problems = self.run_gate(blocked_then_pass)
        self.assertTrue(any("blocked-limitation" in p and "not cleared" in p for p in problems), problems)
        pass_then_blocked = GOOD + "rea: 001-todo-edit|blocked-limitation|rea CLI missing\n"
        problems = self.run_gate(pass_then_blocked)
        self.assertTrue(any("blocked-limitation" in p for p in problems), problems)
        appended_then_pass = GOOD.replace(
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
            "rea: 001-todo-edit|tasks-appended|T005 added\n"
            "rea: 001-todo-edit|pass|ev_adf6e4ce87099f67",
        )
        self.assertEqual(self.run_gate(appended_then_pass), [])
        pass_then_appended = GOOD + "rea: 001-todo-edit|tasks-appended|T005 added\n"
        self.assertTrue(any("001-todo-edit" in p for p in self.run_gate(pass_then_appended)))

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
            (root / "specs" / "001-todo-edit").mkdir(parents=True)
            feature = root / "specs" / "000-legacy"
            feature.mkdir(parents=True)
            (feature / "tasks.md").write_text("\n".join(f"- [ ] T{i:03d} old" for i in range(1, 20)))
            (root / "progress.md").write_text(GOOD + "gate: exclude|000-legacy|predates this Final Goal\n")
            self.assertEqual(check(root / "progress.md"), [])

    def _git_repo(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        quiet = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        subprocess.check_call(["git", "init"], cwd=path, **quiet)
        subprocess.check_call(["git", "config", "user.email", "t@example.com"], cwd=path)
        subprocess.check_call(["git", "config", "user.name", "t"], cwd=path)
        (path / "README").write_text("x\n")
        subprocess.check_call(["git", "add", "README"], cwd=path, **quiet)
        subprocess.check_call(["git", "commit", "-m", "init"], cwd=path, **quiet)

    def _worktree(self, repo: Path, path: Path, branch: str) -> None:
        subprocess.check_call(
            ["git", "-C", str(repo), "worktree", "add", "-b", branch, str(path), "HEAD"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _feature(self, root: Path) -> None:
        (root / "specs" / "001-todo-edit").mkdir(parents=True)
        (root / "progress.md").write_text(GOOD)

    def test_a_subdirectory_does_not_flag_the_main_checkout(self):
        if shutil.which("git") is None:
            self.skipTest("git missing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            self._git_repo(root)
            app = root / "packages" / "app"
            self._feature(app)
            problems = check(app / "progress.md")
        self.assertFalse(any("worktree" in p for p in problems), problems)
        self.assertFalse(any(str(root.resolve()) in p for p in problems), problems)

    def test_a_linked_worktree_does_not_flag_the_main_checkout(self):
        if shutil.which("git") is None:
            self.skipTest("git missing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            self._git_repo(root)
            linked = Path(d) / "linked"
            self._worktree(root, linked, "feature")
            self._feature(linked)
            (linked / "progress.md").write_text(GOOD + f"gate: worktree|{root.resolve()}\n")
            problems = check(linked / "progress.md")
        self.assertFalse(any("worktree" in p.lower() and "leftover" in p for p in problems), problems)
        self.assertFalse(any("git worktree remove" in p for p in problems), problems)
        self.assertFalse(any(str(root.resolve()) in p for p in problems), problems)

    def test_a_preexisting_worktree_is_not_a_leftover(self):
        if shutil.which("git") is None:
            self.skipTest("git missing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            self._git_repo(root)
            self._worktree(root, Path(d) / "unrelated", "unrelated")
            self._feature(root)
            problems = check(root / "progress.md")
        self.assertFalse(any("leftover git worktree" in p for p in problems), problems)

    def test_a_recorded_worktree_still_blocks(self):
        if shutil.which("git") is None:
            self.skipTest("git missing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            self._git_repo(root)
            extra = Path(d) / "leaf"
            self._worktree(root, extra, "leaf")
            self._feature(root)
            (root / "progress.md").write_text(
                GOOD + f"gate: worktree|{extra.resolve()}\n" + f"gate: worktree|{root.resolve()}\n"
            )
            problems = check(root / "progress.md")
        self.assertTrue(any("leftover git worktree" in p and str(extra.resolve()) in p for p in problems), problems)
        self.assertFalse(any(str(root.resolve()) in p for p in problems), problems)
        self.assertTrue(any("git worktree remove" in p for p in problems), problems)

    def test_stuck_message_names_the_block_and_drops_the_met_claim(self):
        message = stuck_message(["before calling the Final Goal met"])
        self.assertTrue(message.startswith("NOT complete / blocked:"))
        self.assertIn("The Final Goal is not met.", message)
        self.assertNotIn("Final Goal met", message)
        self.assertIn("run is not complete", message)

    def test_clear_met_claim_rewrites_progress_and_keeps_an_honest_negation(self):
        with tempfile.TemporaryDirectory() as d:
            progress = Path(d) / "progress.md"
            progress.write_text("Status: Final Goal met\nFinal Goal NOT met stays.\n")
            message = stuck_message(["missing review"])
            clear_met_claim(progress, message)
            text = progress.read_text()
        self.assertNotIn("Final Goal met", text)
        self.assertIn("Final Goal is not met", text)
        self.assertIn("Final Goal NOT met stays.", text)
        self.assertIn(message, text)
        self.assertFalse(claims_met(text))

    def test_refusal_key_changes_with_progress_or_git_and_stays_for_a_repeat(self):
        if shutil.which("git") is None:
            self.skipTest("git missing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            self._git_repo(root)
            progress = root / "progress.md"
            progress.write_text(GOOD)
            first = refusal_key(progress, ["missing"])
            self.assertEqual(first, refusal_key(progress, ["missing"]))
            self.assertNotEqual(first, refusal_key(progress, ["other"]))
            progress.write_text(GOOD + "note\n")
            changed = refusal_key(progress, ["missing"])
            self.assertNotEqual(first, changed)
            (root / "note").write_text("1\n")
            subprocess.check_call(["git", "add", "note"], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(["git", "commit", "-m", "note"], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.assertNotEqual(changed, refusal_key(progress, ["missing"]))

    def test_blocked_review_keeps_gate_open(self):
        text = GOOD.replace("pstack:effort-medium → 2 findings", "BLOCKED: independent review")
        self.assertIn("review is BLOCKED: independent review; the Final Goal stays open", self.run_gate(text))


if __name__ == "__main__":
    unittest.main()
