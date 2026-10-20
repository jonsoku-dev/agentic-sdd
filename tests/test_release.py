import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_manifest_and_changelog_agree(self):
        version = (ROOT / "version.txt").read_text().strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        manifest = json.loads((ROOT / ".release-please-manifest.json").read_text())
        self.assertEqual(manifest["."], version)
        changelog = (ROOT / "CHANGELOG.md").read_text()
        self.assertIn(f"## [{version}]", changelog)
        config = json.loads((ROOT / "release-please-config.json").read_text())
        self.assertEqual(config["release-type"], "simple")

    def test_workflows_present(self):
        for name in ("ci.yml", "release-please.yml"):
            self.assertTrue((ROOT / ".github/workflows" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
