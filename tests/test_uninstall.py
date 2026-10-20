from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "install.sh"


class UninstallTests(unittest.TestCase):
    def run_install(self, env, cwd, *args):
        return subprocess.run(["bash", str(SCRIPT), *args], check=True, env=env, cwd=cwd, capture_output=True, text=True)

    def test_uninstall_removes_everything_it_created_and_lists_what_it_keeps(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            project = Path(tmp) / "proj"
            project.mkdir()
            (home / ".codex").mkdir(parents=True)
            agents = home / ".codex/AGENTS.md"
            agents.write_text("# mine\n\nkeep this line\n")
            env = dict(os.environ, HOME=str(home))

            self.run_install(env, tmp, "--project", str(project), "--apply-cursor-hooks")
            # the Codex mandate needs a pstack root; emulate the plugin cache so the block is written
            ctx = home / ".codex/plugins/cache/pstack-claude/pstack/9.9.9/hooks"
            ctx.mkdir(parents=True)
            (ctx / "session-start-context.md").write_text("You have pstack.\n")
            self.run_install(env, tmp, "--codex-mandate")
            self.assertIn("pstack-mandate:start", agents.read_text())
            self.assertTrue((project / ".agents/playbooks/agentic-sdd.md").is_file())
            self.assertTrue((project / ".cursor/rules/agentic-sdd.mdc").is_file())
            for d in (".agents", ".claude", ".codex", ".cursor", ".grok"):
                self.assertTrue((home / d / "skills/agentic-sdd").is_symlink(), d)

            out = self.run_install(env, tmp, "--uninstall", "--project", str(project)).stdout

            for d in (".agents", ".claude", ".codex", ".cursor", ".grok"):
                self.assertFalse((home / d / "skills/agentic-sdd").exists(), d)
            self.assertFalse((project / ".agents/playbooks/agentic-sdd.md").exists())
            self.assertFalse((project / ".cursor/rules/agentic-sdd.mdc").exists())
            self.assertFalse((home / ".cursor/hooks/agentic-sdd-continue").exists())
            text = agents.read_text()
            self.assertNotIn("pstack-mandate", text)
            self.assertIn("keep this line", text)
            self.assertIn("kept on purpose", out)
            self.assertIn("rea MCP entries", out)
            self.assertTrue((ROOT / "SKILL.md").is_file())

    def test_purge_deps_requires_yes(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=str(Path(tmp) / "home"))
            p = subprocess.run(["bash", str(SCRIPT), "--uninstall", "--purge-deps"], env=env, cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0)
            self.assertIn("rerun with --yes", p.stderr)


if __name__ == "__main__":
    unittest.main()
