#!/usr/bin/env python3
"""Unit tests for the Cursor agentic-sdd continuation gate."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import common


def running_line(action: str = "implement T012") -> str:
    payload = {"status": "running", "stop_reason": None, "next_action": action}
    return "<!-- sdd-continue: " + json.dumps(payload) + " -->\n"


class ContinueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["SDD_CONTINUE_STATE_DIR"] = self.tmp.name
        self.cid = "conv-test"
        self.workspace = Path(self.tmp.name) / "workspace"
        self.workspace.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def session(self, **overrides) -> dict:
        data = common.empty_session(self.cid)
        data.update(overrides)
        return data

    def write_progress(self, body: str) -> Path:
        path = self.workspace / "progress.md"
        path.write_text(body, encoding="utf-8")
        return path

    def record(self) -> dict | None:
        return common.progress_record([str(self.workspace)])

    def test_arm(self) -> None:
        session = self.session(hold=True, followup_count=4, stuck_latched=True, gate_stuck_latched=True, gate_refusal_count=2)
        common.apply_prompt(session, "/agentic-sdd finish the goal")
        self.assertTrue(session["armed"])
        self.assertFalse(session["hold"])
        self.assertEqual(session["followup_count"], 0)
        self.assertFalse(session["stuck_latched"])
        self.assertFalse(session["gate_stuck_latched"])
        self.assertEqual(session["gate_refusal_count"], 0)

    def test_hold(self) -> None:
        self.write_progress("# Progress\n" + running_line())
        session = self.session(armed=True, hold=False)
        common.apply_prompt(session, "why did you stop?")
        self.assertTrue(session["armed"])
        self.assertTrue(session["hold"])
        self.assertIsNone(common.decide_stop(session, {"status": "completed"}, self.record()))

    def test_followup_marker_is_not_hold(self) -> None:
        session = self.session(armed=True, hold=True, followup_count=3, stuck_repeats=1)
        common.apply_prompt(session, "<!-- sdd-continue-followup -->\nDo the next action.")
        self.assertTrue(session["armed"])
        self.assertFalse(session["hold"])
        self.assertEqual(session["followup_count"], 3)

    def test_resume_resets_budget_only_when_armed(self) -> None:
        idle = self.session(armed=False)
        common.apply_prompt(idle, "계속해")
        self.assertFalse(idle["armed"])
        self.assertTrue(idle["hold"])

        armed = self.session(armed=True, hold=True, followup_count=80, budget_exhausted=True)
        common.apply_prompt(armed, "이어서 진행해줘")
        self.assertFalse(armed["hold"])
        self.assertEqual(armed["followup_count"], 0)
        self.assertFalse(armed["budget_exhausted"])

    def test_delivered(self) -> None:
        self.write_progress(
            "# Progress\n"
            "pstack: O-interrogate|cursor|poteto-agent → 0 findings\n"
            + "<!-- sdd-continue: " + json.dumps(
                {"status": "delivered", "stop_reason": None, "next_action": ""}
            ) + " -->\n"
        )
        session = self.session(armed=True)
        self.assertIsNone(common.decide_stop(session, {"status": "completed"}, self.record()))

    def test_delivered_with_an_open_gate_is_refused(self) -> None:
        self.write_progress("# Progress\nFinal Goal met\n" + "<!-- sdd-continue: " + json.dumps(
            {"status": "delivered", "stop_reason": None, "next_action": ""}
        ) + " -->\n")
        session = self.session(armed=True)
        message = common.decide_stop(session, {"status": "completed"}, self.record())
        self.assertIsNotNone(message)
        assert message is not None
        self.assertIn("refused completion", message)
        self.assertIn("O-interrogate", message)
        self.assertIn("not met", message)
        self.assertEqual(session["followup_count"], 1)

    def _open_delivered(self, extra: str = "") -> None:
        self.write_progress(
            "# Progress\nFinal Goal met\n" + extra + "<!-- sdd-continue: " + json.dumps(
                {"status": "delivered", "stop_reason": None, "next_action": ""}
            ) + " -->\n"
        )

    def test_identical_gate_refusal_ends_not_complete(self) -> None:
        self._open_delivered()
        session = self.session(armed=True)
        payload = {"status": "completed"}
        first = common.decide_stop(session, payload, self.record())
        assert first is not None
        self.assertIn("refused completion", first)
        self.assertNotIn("NOT complete / blocked:", first)
        second = common.decide_stop(session, payload, self.record())
        assert second is not None
        self.assertTrue(second.startswith("NOT complete / blocked:"))
        self.assertIn("The Final Goal is not met.", second)
        self.assertNotIn("Final Goal met", second)
        self.assertIn("run is not complete", second)
        text = (self.workspace / "progress.md").read_text(encoding="utf-8")
        self.assertNotIn("Final Goal met", text)
        self.assertIn("NOT complete / blocked:", text)
        self.assertIn("The Final Goal is not met", text)
        self.assertTrue(session["gate_stuck_latched"])
        self.assertEqual(session["followup_count"], 1)
        emitted = common.stop_payload(second)
        assert emitted is not None
        self.assertNotIn("followup_message", emitted)
        self.assertTrue(emitted["user_message"].startswith("NOT complete / blocked:"))
        third = common.decide_stop(session, payload, self.record())
        self.assertIsNone(third)
        self.assertIsNone(common.stop_payload(third))

    def test_changed_progress_resets_the_gate_refusal_streak(self) -> None:
        self._open_delivered()
        session = self.session(armed=True)
        payload = {"status": "completed"}
        first = common.decide_stop(session, payload, self.record())
        self._open_delivered("note: still open\n")
        second = common.decide_stop(session, payload, self.record())
        assert first is not None and second is not None
        self.assertIn("refused completion", second)
        self.assertFalse(session["gate_stuck_latched"])
        third = common.decide_stop(session, payload, self.record())
        assert third is not None
        self.assertTrue(third.startswith("NOT complete / blocked:"))
        self.assertNotIn("Final Goal met", third)

    def test_git_change_resets_the_gate_refusal_streak(self) -> None:
        self._open_delivered()
        quiet = {"cwd": self.workspace, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        subprocess.check_call(["git", "init"], **quiet)
        subprocess.check_call(["git", "config", "user.email", "t@example.com"], cwd=self.workspace)
        subprocess.check_call(["git", "config", "user.name", "t"], cwd=self.workspace)
        subprocess.check_call(["git", "add", "progress.md"], **quiet)
        subprocess.check_call(["git", "commit", "-m", "init"], **quiet)
        session = self.session(armed=True)
        payload = {"status": "completed"}
        first = common.decide_stop(session, payload, self.record())
        (self.workspace / "note").write_text("1\n", encoding="utf-8")
        subprocess.check_call(["git", "add", "note"], **quiet)
        subprocess.check_call(["git", "commit", "-m", "note"], **quiet)
        second = common.decide_stop(session, payload, self.record())
        assert first is not None and second is not None
        self.assertIn("refused completion", second)
        self.assertFalse(session["gate_stuck_latched"])
        third = common.decide_stop(session, payload, self.record())
        assert third is not None
        self.assertTrue(third.startswith("NOT complete / blocked:"))
        self.assertNotIn("Final Goal met", third)

    def test_blocked(self) -> None:
        self.write_progress("# Progress\n" + "<!-- sdd-continue: " + json.dumps(
            {"status": "blocked", "stop_reason": "secret", "next_action": "ask once"}
        ) + " -->\n")
        session = self.session(armed=True)
        self.assertIsNone(common.decide_stop(session, {"status": "completed"}, self.record()))

    def test_hard_stop_reason_while_running(self) -> None:
        self.write_progress("# Progress\n" + "<!-- sdd-continue: " + json.dumps(
            {"status": "running", "stop_reason": "destructive", "next_action": "wait"}
        ) + " -->\n")
        session = self.session(armed=True)
        self.assertIsNone(common.decide_stop(session, {"status": "completed"}, self.record()))

    def test_ask(self) -> None:
        session = self.session(armed=True, composer_mode="ask", skip=True)
        self.write_progress("# Progress\n" + running_line())
        self.assertIsNone(common.decide_stop(session, {"status": "completed"}, self.record()))

    def test_background(self) -> None:
        session = self.session(armed=True, is_background_agent=True, skip=True)
        self.write_progress("# Progress\n" + running_line())
        self.assertIsNone(common.decide_stop(session, {"status": "completed"}, self.record()))

    def test_aborted(self) -> None:
        session = self.session(armed=True)
        self.write_progress("# Progress\n" + running_line())
        self.assertIsNone(common.decide_stop(session, {"status": "aborted"}, self.record()))

    def test_running_followup_names_next_action(self) -> None:
        self.write_progress("# Progress\n" + running_line("implement T012"))
        session = self.session(armed=True)
        message = common.decide_stop(session, {"status": "completed"}, self.record())
        self.assertIsNotNone(message)
        assert message is not None
        self.assertIn("sdd-continue-followup", message)
        self.assertIn("not a new task", message)
        self.assertIn("next_action: implement T012", message)
        self.assertEqual(session["followup_count"], 1)

    def test_missing_line_continues_once_then_sticks(self) -> None:
        session = self.session(armed=True)
        first = common.decide_stop(session, {"status": "completed"}, None)
        second = common.decide_stop(session, {"status": "completed"}, None)
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertTrue(session["stuck_latched"])
        third = common.decide_stop(session, {"status": "completed"}, None)
        self.assertIsNone(third)

    def test_stuck_twice_same_progress(self) -> None:
        path = self.write_progress("# Progress\n" + running_line("implement T012"))
        session = self.session(armed=True)
        record = self.record()
        first = common.decide_stop(session, {"status": "completed"}, record)
        os.utime(path, ns=(path.stat().st_atime_ns, record["mtime_ns"]))
        second = common.decide_stop(session, {"status": "completed"}, self.record())
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertTrue(session["stuck_latched"])

    def test_changed_next_action_is_not_stuck(self) -> None:
        self.write_progress("# Progress\n" + running_line("plan"))
        session = self.session(armed=True)
        first = common.decide_stop(session, {"status": "completed"}, self.record())
        self.write_progress("# Progress\n" + running_line("implement T012"))
        second = common.decide_stop(session, {"status": "completed"}, self.record())
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertEqual(session["followup_count"], 2)

    def test_budget_cap(self) -> None:
        self.write_progress("# Progress\n" + running_line("implement T012"))
        session = self.session(armed=True, followup_count=79)
        message = common.decide_stop(session, {"status": "completed"}, self.record())
        self.assertIsNotNone(message)
        assert message is not None
        self.assertIn("continuation budget is spent", message)
        self.assertEqual(session["followup_count"], 80)

        self.write_progress("# Progress\n" + running_line("implement T013"))
        blocked = common.decide_stop(session, {"status": "completed"}, self.record())
        self.assertIsNone(blocked)
        self.assertTrue(session["budget_exhausted"])

    def test_handle_stop_idle_session_has_no_message(self) -> None:
        message = common.handle_stop(
            {
                "conversation_id": self.cid,
                "status": "completed",
                "workspace_roots": [str(self.workspace)],
            }
        )
        self.assertIsNone(message)

    def test_session_start_ask_skips(self) -> None:
        common.handle_session_start(
            {
                "conversation_id": self.cid,
                "composer_mode": "ask",
                "is_background_agent": False,
            }
        )
        common.handle_prompt({"conversation_id": self.cid, "prompt": "/agentic-sdd"})
        self.write_progress("# Progress\n" + running_line())
        message = common.handle_stop(
            {
                "conversation_id": self.cid,
                "status": "completed",
                "workspace_roots": [str(self.workspace)],
            }
        )
        self.assertIsNone(message)

    def test_after_response_stores_head(self) -> None:
        common.handle_after_response(
            {"conversation_id": self.cid, "text": "A" * 2000}
        )
        stored = common.load_session(self.cid)
        self.assertEqual(len(stored["last_assistant_head"]), common.ASSISTANT_HEAD_LIMIT)


if __name__ == "__main__":
    unittest.main()
