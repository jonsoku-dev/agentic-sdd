import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import deps  # noqa: E402


class VersionCompare(unittest.TestCase):
    def test_behind(self):
        self.assertTrue(deps.behind("0.9.92", "0.9.94"))
        self.assertFalse(deps.behind("0.9.94", "0.9.94"))
        self.assertFalse(deps.behind("1.2.2", "1.0.1"))
        self.assertTrue(deps.behind(None, "1.0.0"))
        self.assertFalse(deps.behind("1.0.0", None))

    def test_vtuple_handles_prefixes(self):
        self.assertEqual(deps.vtuple("v1.2.2"), (1, 2, 2))
        self.assertEqual(deps.vtuple("specify-cli v1.0.1"), (1, 0, 1))


class LocalLookups(unittest.TestCase):
    def test_highest_plugin_version_and_rea_pins(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            for v in ("0.9.92", "0.9.94"):
                m = home / ".claude/plugins/cache/pstack-claude/pstack" / v / ".claude-plugin"
                m.mkdir(parents=True)
                (m / "plugin.json").write_text(json.dumps({"version": v}))
            self.assertEqual(deps.highest(home.glob(".claude/plugins/cache/*/pstack/*")), "0.9.94")
            cfg = home / "mcp.json"
            cfg.write_text(json.dumps({"mcpServers": {"rea": {"args": ["-y", "rea-agents@6.4.0", "mcp"]}}}))
            self.assertEqual(deps.rea_pins([cfg]), {str(cfg): "6.4.0"})
            changed = deps.repin_rea("6.7.0", [cfg])
            self.assertEqual(changed, [str(cfg)])
            self.assertIn("rea-agents@6.7.0", cfg.read_text())
            self.assertTrue((home / "mcp.json.bak-rea-6.7.0").is_file())


class Rows(unittest.TestCase):
    def test_rows_flag_behind_components(self):
        installed = {"spec-kit": "1.0.1", "pstack@claude": "0.9.92", "pstack@codex": "0.9.94", "pstack@grok": "0.9.93",
                     "pstack@cursor": "0.15.28", "rea-agents": "6.4.0", "cli:claude": "2.1.304", "cli:codex": "0.162.0",
                     "cli:grok": "1.0.55", "cli:cursor-agent": "2026.10.18", "tool:node": "present", "tool:bun": "present",
                     "tool:uv": "present", "tool:gh": None, "tool:npx": "present"}
        latest = {"spec-kit": "1.2.2", "pstack-claude": "0.9.94", "pstack-cursor": "0.15.28", "rea-agents": "6.7.0"}
        r = {x["component"]: x for x in deps.rows(installed, latest)}
        self.assertTrue(r["spec-kit (specify)"]["behind"])
        self.assertTrue(r["pstack@claude"]["behind"])
        self.assertFalse(r["pstack@codex"]["behind"])
        self.assertTrue(r["pstack@grok"]["behind"])
        self.assertFalse(r["pstack@cursor"]["behind"])
        self.assertTrue(r["rea-agents (pins)"]["behind"])
        self.assertFalse(r["cli:claude"]["behind"])
        self.assertEqual(r["tool:gh"]["update"], "install manually")


if __name__ == "__main__":
    unittest.main()
