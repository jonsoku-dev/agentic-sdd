#!/usr/bin/env python3
"""Plugin editions, guarded hooks, report, and dashboard API."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREE, GUARDED = ROOT / "plugins" / "agentic-sdd", ROOT / "plugins" / "agentic-sdd-guarded"
HOOKS = GUARDED / "hooks"

PROGRESS_MET = """# Progress
## Final Goal
Add todo edit.
pstack: O-interrogate|claude|pstack:effort-medium → 1 findings
rea: 001-todo-edit|pass|ev_abc123def456
Status: Final Goal met
"""


def project(text: str, features=("001-todo-edit",)) -> Path:
    root = Path(tempfile.mkdtemp())
    for f in features:
        (root / "specs" / f).mkdir(parents=True)
    (root / "progress.md").write_text(text)
    return root


def hook(name: str, payload: dict) -> dict:
    p = subprocess.run([sys.executable, str(HOOKS / name)], input=json.dumps(payload), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout) if p.stdout.strip() else {}


def transcript_with_review(root: Path) -> str:
    t = root / "t.jsonl"
    t.write_text(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Agent", "input": {"description": "Independent review", "subagent_type": "general-purpose"}}]}}) + "\n")
    return str(t)


class EditionsTest(unittest.TestCase):
    def test_build_is_in_sync(self):
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_plugins.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_editions_differ_only_where_intended(self):
        self.assertFalse((FREE / "hooks").exists())
        policy = (FREE / "skills" / "dashboard" / "agents" / "openai.yaml").read_text()
        self.assertIn("allow_implicit_invocation: false", policy)
        self.assertTrue((GUARDED / "hooks" / "hooks.json").is_file())
        self.assertTrue((FREE / ".codex-plugin" / "plugin.json").is_file())
        self.assertFalse((GUARDED / ".codex-plugin").exists())
        for ed in (FREE, GUARDED):
            self.assertTrue((ed / "skills" / "agentic-sdd" / "SKILL.md").is_file())
            self.assertTrue((ed / "skills" / "agentic-sdd" / "scripts" / "progress_gate.py").is_file())
            self.assertFalse((ed / "skills" / "agentic-sdd" / "scripts" / "build_plugins.py").exists())

    def test_marketplace_names_and_versions_match_manifests(self):
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        version = json.loads((ROOT / "package.json").read_text())["version"]
        for entry in market["plugins"]:
            manifest = json.loads((ROOT / entry["source"] / ".claude-plugin" / "plugin.json").read_text())
            self.assertEqual(entry["name"], manifest["name"])
            self.assertEqual({entry["version"], manifest["version"]}, {version})

    def test_hook_commands_quote_the_plugin_root(self):
        for groups in json.loads((HOOKS / "hooks.json").read_text())["hooks"].values():
            for g in groups:
                for h in g["hooks"]:
                    self.assertIn('"${CLAUDE_PLUGIN_ROOT}/hooks/', h["command"])


class StopGateTest(unittest.TestCase):
    def test_clean_gate_lets_the_turn_end(self):
        root = project(PROGRESS_MET)
        self.assertEqual(hook("stop_gate.py", {"cwd": str(root), "session_id": "s", "transcript_path": transcript_with_review(root)}), {})

    def test_open_gate_keeps_blocking_while_the_claim_remains(self):
        root = project(PROGRESS_MET.replace("rea: 001-todo-edit|pass|ev_abc123def456\n", "- `rea: 001-todo-edit|pass|ev_abc`\n"))
        payload = {"cwd": str(root), "session_id": "s1", "transcript_path": transcript_with_review(root)}
        first = hook("stop_gate.py", payload)
        self.assertEqual(first["decision"], "block")
        self.assertIn("column 1", first["reason"])
        self.assertIn("stays blocked", first["reason"])
        self.assertEqual(hook("stop_gate.py", payload)["decision"], "block")
        self.assertEqual(hook("stop_gate.py", payload)["decision"], "block")
        events = [json.loads(l)["event"] for l in (root / ".agentic-sdd" / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual(events, ["gate_blocked", "gate_blocked", "gate_blocked"])

    def test_claimed_review_without_a_spawn_blocks(self):
        root = project(PROGRESS_MET)
        out = hook("stop_gate.py", {"cwd": str(root), "session_id": "s", "transcript_path": str(root / "none.jsonl")})
        self.assertIn("no reviewer subagent was spawned", out["reason"])

    def test_spawn_in_the_ledger_counts_across_sessions(self):
        root = project(PROGRESS_MET)
        hook("ledger.py", {"cwd": str(root), "session_id": "old", "tool_input": {"description": "Converge review", "subagent_type": "x", "prompt": "SECRET"}})
        self.assertEqual(hook("stop_gate.py", {"cwd": str(root), "session_id": "new"}), {})
        self.assertNotIn("SECRET", (root / ".agentic-sdd" / "ledger.jsonl").read_text())

    def test_honest_not_met_status_is_not_blocked(self):
        root = project(PROGRESS_MET.replace("Status: Final Goal met", "Status: Final Goal NOT met: review BLOCKED"))
        self.assertEqual(hook("stop_gate.py", {"cwd": str(root), "session_id": "s"}), {})

    def test_unfinished_goal_and_foreign_dirs_are_ignored(self):
        root = project(PROGRESS_MET.replace("Status: Final Goal met", "Status: implementing"))
        self.assertEqual(hook("stop_gate.py", {"cwd": str(root), "session_id": "s"}), {})
        self.assertEqual(hook("stop_gate.py", {"cwd": tempfile.mkdtemp(), "session_id": "s"}), {})


class WakeupTest(unittest.TestCase):
    def test_denied_only_inside_an_agentic_sdd_project(self):
        root = project(PROGRESS_MET)
        out = hook("block_wakeup.py", {"cwd": str(root / "specs"), "session_id": "s"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(hook("block_wakeup.py", {"cwd": tempfile.mkdtemp(), "session_id": "s"}), {})


class GitGuardTest(unittest.TestCase):
    def test_denies_out_of_authority_git_only_in_a_project(self):
        root = project(PROGRESS_MET)
        deny = hook("git_guard.py", {"cwd": str(root), "session_id": "s", "tool_input": {"command": "git add -A && git push origin main"}})
        self.assertEqual(deny["hookSpecificOutput"]["permissionDecision"], "deny")
        for denied in ("git merge origin/main", "npm publish", "vercel --prod", "fly deploy", "kubectl apply -f x.yaml", "gh release create v1"):
            out = hook("git_guard.py", {"cwd": str(root), "session_id": "s", "tool_input": {"command": denied}})
            self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny", denied)
            self.assertIn(denied.split()[0], out["hookSpecificOutput"]["permissionDecisionReason"])
        for ok in ("git commit -m done", "echo 'git push'", "git checkout ./todo.py", "git branch -d merged",
                   "git merge --abort", "npm test", "vercel dev", "echo npm publish"):
            self.assertEqual(hook("git_guard.py", {"cwd": str(root), "session_id": "s", "tool_input": {"command": ok}}), {}, ok)
        self.assertEqual(hook("git_guard.py", {"cwd": tempfile.mkdtemp(), "tool_input": {"command": "git push"}}), {})


class ReportAndDashboardTest(unittest.TestCase):
    def test_report_writes_markdown_and_tracks_change(self):
        root = project(PROGRESS_MET)
        script = ROOT / "scripts" / "report.py"
        first = Path(subprocess.run([sys.executable, str(script), "--project", str(root)], capture_output=True, text=True, check=True).stdout.strip())
        self.assertIn("Gate: **ok**", first.read_text())
        self.assertIn("first report", first.read_text())

    def test_dashboard_api_has_no_cors_and_refuses_traversal(self):
        sys.path.insert(0, str(ROOT / "visualizer"))
        import server
        root = project(PROGRESS_MET)
        httpd = HTTPServer(("127.0.0.1", 0), server.make_handler(root))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{httpd.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/api/status") as r:
                self.assertIsNone(r.headers.get("Access-Control-Allow-Origin"))
                self.assertTrue(json.loads(r.read())["gate"]["ok"])
            for bad in ("/api/report?name=../../progress.md", "/server.py"):
                with self.assertRaises(urllib.error.HTTPError) as e:
                    urllib.request.urlopen(base + bad)
                self.assertEqual(e.exception.code, 404)
        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
