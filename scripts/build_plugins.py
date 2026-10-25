#!/usr/bin/env python3
"""Generate the two plugin editions and the marketplace from the repository sources.

usage: build_plugins.py [--check]
  plugins/agentic-sdd          no hooks; Claude Code and Codex (works where hooks are blocked)
  plugins/agentic-sdd-guarded  same skills plus Stop/PreToolUse/PostToolUse hooks; Claude Code only
  .claude-plugin/marketplace.json lists both (Codex reads this file too)
--check exits 1 when the committed tree differs from a fresh build (used by the tests).
"""
from __future__ import annotations

import filecmp
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "hosts" / "claude"
SKIP_SCRIPTS = {"build_llms.py", "build_plugins.py", "dev-setup.sh", "upstream_watch.py", "deps.py", "setup.py"}
PAYLOAD = ["SKILL.md", "LICENSE", "references", "templates", "visualizer", "scripts"]
DESCRIPTION = ("Spec Kit delivery driven to the Final Goal: phase contracts, a one-page phase card, a completion "
               "gate script, REA closeout, a local dashboard and tracking reports.")
EDITIONS = {
    "agentic-sdd": {"hooks": False, "codex": True,
                    "summary": DESCRIPTION + " Hook-free edition: safe where plugin hooks are blocked."},
    "agentic-sdd-guarded": {"hooks": True, "codex": False,
                            "summary": DESCRIPTION + " Guarded edition: hooks block a false 'Final Goal met', "
                                       "ScheduleWakeup during a run, and log subagent spawns."},
}


def version() -> str:
    return json.loads((ROOT / "package.json").read_text())["version"]


def ignore(dirpath: str, names: list[str]) -> set[str]:
    skip = {n for n in names if n in {"__pycache__", "githooks"} or n.endswith(".pyc")}
    if Path(dirpath).name == "scripts":
        skip |= SKIP_SCRIPTS & set(names)
    return skip


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def build(out: Path) -> None:
    v = version()
    meta = {"author": {"name": "jonsoku-dev"}, "homepage": "https://github.com/jonsoku-dev/agentic-sdd",
            "repository": "https://github.com/jonsoku-dev/agentic-sdd", "license": "MIT"}
    for name, ed in EDITIONS.items():
        dst = out / "plugins" / name
        skill = dst / "skills" / "agentic-sdd"
        for item in PAYLOAD:
            src = ROOT / item
            if src.is_dir():
                shutil.copytree(src, skill / item, ignore=ignore)
            else:
                skill.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, skill / item)
        shutil.copytree(HOST / "skills", dst / "skills", dirs_exist_ok=True)
        shutil.copytree(HOST / "bin", dst / "bin")
        shutil.copy2(ROOT / "LICENSE", dst / "LICENSE")
        manifest = {"name": name, "version": v, "description": ed["summary"], **meta,
                    "keywords": ["spec-kit", "sdd", "agentic", "skills", "quality-gate"]}
        if ed["hooks"]:
            shutil.copytree(HOST / "hooks", dst / "hooks", ignore=ignore)
        write_json(dst / ".claude-plugin" / "plugin.json", manifest)
        if ed["codex"]:
            write_json(dst / ".codex-plugin" / "plugin.json", {
                **manifest, "skills": "./skills/",
                "interface": {"displayName": "Agentic SDD", "shortDescription": "Spec Kit delivery to the Final Goal",
                              "longDescription": ed["summary"], "developerName": "jonsoku-dev",
                              "category": "Developer Tools", "capabilities": ["Interactive", "Read", "Write"],
                              "defaultPrompt": ["Deliver this Final Goal with agentic-sdd."]}})
    write_json(out / ".claude-plugin" / "marketplace.json", {
        "name": "agentic-sdd", "owner": {"name": "jonsoku-dev"},
        "description": "Agentic SDD in two editions: hook-free (Claude Code and Codex) and guarded (Claude Code hooks).",
        "plugins": [{"name": n, "source": f"./plugins/{n}", "description": e["summary"], "version": v}
                    for n, e in EDITIONS.items()]})


def same(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    if filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)[1:] != ([], []):
        return False
    return all(same(a / d, b / d) for d in cmp.common_dirs)


def main() -> int:
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp))
            ok = all(same(Path(tmp) / p, ROOT / p) for p in ("plugins", ".claude-plugin"))
        print("plugins in sync" if ok else "plugins out of date: run python3 scripts/build_plugins.py")
        return 0 if ok else 1
    for p in ("plugins", ".claude-plugin"):
        shutil.rmtree(ROOT / p, ignore_errors=True)
    build(ROOT)
    print(f"built plugins/{', plugins/'.join(EDITIONS)} and .claude-plugin/marketplace.json at {version()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
