#!/usr/bin/env python3
"""Watch the upstreams this skill depends on and bump the pins in the repository.

    python3 scripts/upstream_watch.py            # table of pinned vs latest; exit 1 when behind
    python3 scripts/upstream_watch.py --bump     # rewrite pins.json and every rea-agents@X.Y.Z pin in the docs
    python3 scripts/upstream_watch.py --markdown # summary for a pull-request body

Runs weekly in .github/workflows/upstream.yml, which opens a pull request when
--bump changed anything. Stdlib only; network via scripts/deps.py.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deps  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PINS = ROOT / "pins.json"
REA_PIN_FILES = ["SKILL.md", "references/rea-closeout.md", "agents/openai.yaml", "README.md"]
REA_PIN = re.compile(r"rea-agents@(\d+\.\d+\.\d+)")


def compare(pins: dict, latest: dict) -> list[dict]:
    rows = [
        {"component": "rea-agents", "pinned": pins["rea-agents"]["min"], "latest": latest.get("rea-agents"), "kind": "min"},
        {"component": "pstack-claude", "pinned": pins["pstack-claude"]["tested"], "latest": latest.get("pstack-claude"), "kind": "tested"},
        {"component": "pstack-cursor", "pinned": pins["pstack-cursor"]["tested"], "latest": latest.get("pstack-cursor"), "kind": "tested"},
        {"component": "spec-kit", "pinned": pins["spec-kit"]["tested"], "latest": latest.get("spec-kit"), "kind": "tested"},
    ]
    for r in rows:
        r["behind"] = deps.behind(r["pinned"], r["latest"])
    return rows


def bump(pins: dict, latest: dict, root: Path = ROOT) -> list[str]:
    changed = []
    if deps.behind(pins["rea-agents"]["min"], latest.get("rea-agents")):
        new = latest["rea-agents"]
        pins["rea-agents"]["min"] = new
        for rel in REA_PIN_FILES:
            p = root / rel
            if not p.is_file():
                continue
            t = p.read_text()
            t2 = REA_PIN.sub(f"rea-agents@{new}", t)
            if t2 != t:
                p.write_text(t2)
                changed.append(rel)
    for key in ("pstack-claude", "pstack-cursor", "spec-kit"):
        if deps.behind(pins[key]["tested"], latest.get(key)):
            pins[key]["tested"] = latest[key]
            changed.append(f"pins.json:{key}")
    if changed:
        (root / "pins.json").write_text(json.dumps(pins, indent=2) + "\n")
        if "pins.json" not in changed:
            changed.append("pins.json")
    return changed


def table(rows: list[dict], markdown: bool) -> str:
    if markdown:
        out = ["| component | pinned | latest | status |", "|---|---|---|---|"]
        for r in rows:
            out.append(f"| {r['component']} ({r['kind']}) | {r['pinned']} | {r['latest'] or '?'} | {'behind' if r['behind'] else 'ok'} |")
        return "\n".join(out)
    w = max(len(r["component"]) for r in rows)
    return "\n".join(f"{r['component'].ljust(w)}  {r['kind']:6} {str(r['pinned']).ljust(8)} latest {str(r['latest'] or '?').ljust(8)} {'BEHIND' if r['behind'] else 'ok'}" for r in rows)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    pins = json.loads(PINS.read_text())
    latest = deps.latest_versions()
    rows = compare(pins, latest)
    print(table(rows, "--markdown" in argv))
    if "--bump" in argv:
        changed = bump(pins, latest)
        print("\nchanged: " + (", ".join(changed) if changed else "nothing"))
        return 0
    return 1 if any(r["behind"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
