import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_manifest_and_changelog_agree(self):
        pkg = json.loads((ROOT / "package.json").read_text())
        version = pkg["version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        manifest = json.loads((ROOT / ".release-please-manifest.json").read_text())
        self.assertEqual(manifest["."], version)
        changelog = (ROOT / "CHANGELOG.md").read_text()
        self.assertIn(f"## [{version}]", changelog)
        config = json.loads((ROOT / "release-please-config.json").read_text())
        self.assertEqual(config["release-type"], "node")
        self.assertEqual(pkg["bin"]["agentic-sdd"], "bin/agentic-sdd.js")
        for rel in pkg["files"]:
            if rel.startswith("!"):
                continue
            self.assertTrue((ROOT / rel.rstrip("/")).exists(), rel)

    def test_workflows_present(self):
        for name in ("ci.yml", "release-please.yml", "upstream.yml", "dependabot-automerge.yml"):
            self.assertTrue((ROOT / ".github/workflows" / name).is_file(), name)

    def test_cli_copies_itself_when_installed_under_node_modules(self):
        import os
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "cache" / "node_modules" / "agentic-sdd"   # where npx puts the package
            shutil.copytree(ROOT, pkg, ignore=shutil.ignore_patterns(".git", "docs", "tests", ".github"))
            home = Path(tmp) / "home"
            env = dict(os.environ, AGENTIC_SDD_HOME=str(home))
            p = subprocess.run(["node", str(pkg / "bin/agentic-sdd.js"), "where"], capture_output=True, text=True, timeout=60, env=env)
            self.assertEqual(p.returncode, 0, p.stderr)
            target = home / ".agents/skills/agentic-sdd"
            self.assertEqual(Path(p.stdout.strip()).resolve(), target.resolve())  # `where` prints only the path
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertTrue((target / "install.sh").is_file())
            self.assertFalse((target / "tests").exists())
            self.assertEqual((target / ".npm-version").read_text().strip(), json.loads((ROOT / "package.json").read_text())["version"])

    def test_tarball_has_no_bytecode(self):
        import shutil
        if not shutil.which("npm"):
            self.skipTest("npm not on PATH")
        (ROOT / "scripts/__pycache__").mkdir(exist_ok=True)
        (ROOT / "scripts/__pycache__/probe.cpython-0.pyc").write_bytes(b"")
        p = subprocess.run(["npm", "pack", "--dry-run", "--json", "--ignore-scripts"], cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertEqual(p.returncode, 0, p.stderr)
        files = [f["path"] for f in json.loads(p.stdout)[0]["files"]]
        self.assertFalse([f for f in files if "__pycache__" in f or f.endswith(".pyc")], files)
        self.assertIn("install.sh", files)

    def test_cli_help_and_version(self):
        p = subprocess.run(["node", str(ROOT / "bin/agentic-sdd.js"), "--help"], capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0)
        self.assertIn("npx agentic-sdd", p.stdout)
        v = subprocess.run(["node", str(ROOT / "bin/agentic-sdd.js"), "--version"], capture_output=True, text=True, timeout=30)
        self.assertEqual(v.stdout.strip(), json.loads((ROOT / "package.json").read_text())["version"])


if __name__ == "__main__":
    unittest.main()
