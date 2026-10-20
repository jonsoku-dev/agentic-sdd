import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import setup  # noqa: E402
import deps  # noqa: E402

LATEST = {"spec-kit": "1.2.2", "pstack-claude": "0.9.94", "pstack-cursor": "0.15.28", "rea-agents": "6.7.0"}


class PlanTests(unittest.TestCase):
    def detect_in(self, home: Path, which):
        with mock.patch.object(deps, "latest_versions", return_value=LATEST), \
             mock.patch.object(setup.shutil, "which", side_effect=which), \
             mock.patch.object(deps.shutil, "which", side_effect=which):
            return setup.detect(home)

    def test_bare_machine_plans_prerequisites_and_manual_items_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            d = self.detect_in(home, lambda c: None)
            acts = setup.plan(d, None)
            text = "\n".join(str(a) for a in acts)
            self.assertIn("prerequisites", text)
            self.assertIn("no Homebrew", text)      # nothing to brew with
            self.assertNotIn("REA MCP", text)        # no hosts found, nothing host-specific
            self.assertNotIn("pstack install", text)

    def test_host_present_plans_pstack_rea_and_wiring(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".codex").mkdir()
            (home / ".codex/AGENTS.md").write_text("# mine\n")
            present = {"codex", "git", "node", "npx", "uv", "bun", "gh", "python3", "brew"}
            d = self.detect_in(home, lambda c: f"/usr/bin/{c}" if c in present else None)
            acts = setup.plan(d, home / "proj")
            text = "\n".join(str(a) for a in acts)
            self.assertIn("codex  pstack install", text)
            self.assertIn("--client codex", text)
            self.assertIn("rea-agents@6.7.0 setup", text)
            self.assertIn("--codex-mandate", text)
            self.assertIn("--link-only", text)
            self.assertIn("--project", text)
            self.assertNotIn("--grok-mandate", text)
            self.assertNotIn("claude plugin", text)
            self.assertIn("[manual] codex  model sheet", text)

    def test_apply_runs_commands_in_order_and_stops_a_failed_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "ran"
            acts = [
                setup.Action("x", "ok step", [["sh", "-c", f"echo one > {marker}"], ["sh", "-c", f"echo two >> {marker}"]]),
                setup.Action("x", "failing step", [["sh", "-c", "exit 3"], ["sh", "-c", f"echo never >> {marker}"]]),
                setup.Action("x", "manual", manual="do it yourself"),
            ]
            results = setup.apply(acts)
            self.assertEqual([ok for _, ok, _ in results], [True, False, True])
            self.assertEqual(marker.read_text().split(), ["one", "two"])

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            env = dict(os.environ, HOME=str(home), AGENTIC_SDD_HOME=str(home))
            p = subprocess.run([sys.executable, str(ROOT / "scripts/setup.py"), "--dry-run"], env=env, cwd=tmp, capture_output=True, text=True, timeout=600)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("Plan", p.stdout)
            self.assertFalse((home / ".claude/skills/agentic-sdd").exists())


if __name__ == "__main__":
    unittest.main()
