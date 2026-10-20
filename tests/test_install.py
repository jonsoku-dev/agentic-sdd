from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "install.sh"


class InstallTests(unittest.TestCase):
    def test_apply_cursor_hooks_and_uninstall_keep_other_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            (home / ".cursor").mkdir(parents=True)
            hooks = home / ".cursor" / "hooks.json"
            hooks.write_text(json.dumps({
                "version": 1,
                "hooks": {"stop": [{"command": "./hooks/keep.sh"}]},
            }) + "\n")
            env = os.environ.copy()
            env["HOME"] = str(home)

            subprocess.run(["bash", str(SCRIPT), "--apply-cursor-hooks"], check=True, env=env, cwd=tmp)
            subprocess.run(["bash", str(SCRIPT), "--apply-cursor-hooks"], check=True, env=env, cwd=tmp)

            data = json.loads(hooks.read_text())
            stop = data["hooks"]["stop"]
            sdd = [h for h in stop if "agentic-sdd-continue" in h["command"]]
            self.assertEqual([h["command"] for h in stop if h["command"] == "./hooks/keep.sh"], ["./hooks/keep.sh"])
            self.assertEqual(len(sdd), 1)
            self.assertTrue((home / ".cursor/hooks/agentic-sdd-continue/stop.sh").is_file())
            link = home / ".claude/skills/agentic-sdd"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), ROOT.resolve())

            subprocess.run(["bash", str(SCRIPT), "--uninstall"], check=True, env=env, cwd=tmp)

            self.assertFalse(link.exists())
            self.assertFalse((home / ".cursor/hooks/agentic-sdd-continue").exists())
            self.assertTrue((ROOT / "SKILL.md").is_file())
            data = json.loads(hooks.read_text())
            self.assertEqual(
                [h["command"] for h in data["hooks"].get("stop", [])],
                ["./hooks/keep.sh"],
            )
            self.assertNotIn("beforeSubmitPrompt", data["hooks"])
