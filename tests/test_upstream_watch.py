import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import upstream_watch as uw  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class UpstreamWatchTests(unittest.TestCase):
    def test_compare_flags_behind(self):
        pins = json.loads((ROOT / "pins.json").read_text())
        latest = {"rea-agents": "9.0.0", "pstack-claude": pins["pstack-claude"]["tested"], "pstack-cursor": None, "spec-kit": "0.1.0"}
        rows = {r["component"]: r for r in uw.compare(pins, latest)}
        self.assertTrue(rows["rea-agents"]["behind"])
        self.assertFalse(rows["pstack-claude"]["behind"])
        self.assertFalse(rows["pstack-cursor"]["behind"])  # unknown latest is never "behind"
        self.assertFalse(rows["spec-kit"]["behind"])        # older upstream is not behind

    def test_bump_rewrites_doc_pins_and_pins_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "SKILL.md").write_text("install rea-agents@6.7.0 now\n")
            (root / "references/rea-closeout.md").write_text("npx -y rea-agents@6.7.0 capture-process\n")
            pins = json.loads((ROOT / "pins.json").read_text())
            (root / "pins.json").write_text(json.dumps(pins))
            changed = uw.bump(pins, {"rea-agents": "6.9.1", "pstack-claude": "0.10.0", "pstack-cursor": None, "spec-kit": None}, root)
            self.assertIn("SKILL.md", changed)
            self.assertIn("references/rea-closeout.md", changed)
            self.assertIn("pins.json", changed)
            self.assertIn("rea-agents@6.9.1", (root / "SKILL.md").read_text())
            new = json.loads((root / "pins.json").read_text())
            self.assertEqual(new["rea-agents"]["min"], "6.9.1")
            self.assertEqual(new["pstack-claude"]["tested"], "0.10.0")

    def test_repo_pins_match_docs(self):
        pins = json.loads((ROOT / "pins.json").read_text())
        for rel in uw.REA_PIN_FILES:
            p = ROOT / rel
            if p.is_file():
                for v in uw.REA_PIN.findall(p.read_text()):
                    self.assertEqual(v, pins["rea-agents"]["min"], rel)


if __name__ == "__main__":
    unittest.main()
