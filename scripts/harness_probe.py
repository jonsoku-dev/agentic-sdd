#!/usr/bin/env python3
"""Probe pstack availability and seven-layer harness readiness for one host.

Read-only. Prints a table (or --json) that agentic-sdd records in progress.md
as `pstack: <version>|<host>` and `harness: L1 ..|L7 ..`. Never installs,
never launches a child, never writes to the project.

Usage:
  harness_probe.py --host claude|codex|cursor|grok|auto [--project DIR]
                   [--home DIR] [--json] [--check-map references/pstack-integration.md]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

HOSTS = ("claude", "codex", "cursor", "grok")

# Skills every obligation may require. Must match the "Common core" bullet in
# references/pstack-integration.md; --check-map verifies that.
COMMON_CORE = (
    "poteto-mode", "architect", "arena", "swarm", "interrogate", "how", "why",
    "blast-radius", "tdd", "sharpen", "in-your-own-words", "unslop",
    "technical-writing", "no-comments", "show-me-your-work", "figure-it-out",
    "correct", "reflect", "recall", "benchmark-checklist",
    "create-verification-skill", "maintain-verification-skill", "setup-pstack",
)

MANIFESTS = (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json",
             ".codex-plugin/plugin.json", "plugin.json")


def plugin_roots(home: Path, host: str) -> list[Path]:
    claude = [*home.glob(".claude/plugins/cache/*/pstack/*"),
              *home.glob(".claude/plugins/marketplaces/*/plugins/pstack")]
    table = {
        "claude": claude,
        "codex": [*home.glob(".codex/plugins/cache/*/pstack/*")],
        "cursor": [*home.glob(".cursor/plugins/cache/*/pstack/*")],
        # Grok installs natively or reads the Claude plugin through [compat.claude].
        "grok": [*home.glob(".grok/marketplace-cache/*/plugins/pstack"),
                 *home.glob(".grok/installed-plugins/*/pstack"), *claude],
    }
    return [p for p in table[host] if (p / "skills").is_dir()]


def version_of(root: Path) -> str:
    for rel in MANIFESTS:
        f = root / rel
        if f.is_file():
            try:
                return str(json.loads(f.read_text()).get("version", "0"))
            except (json.JSONDecodeError, OSError):
                continue
    return "0"


def version_key(v: str) -> tuple:
    return tuple(int(x) if x.isdigit() else -1 for x in re.split(r"[.\-]", v))


def pick_root(roots: list[Path]) -> Path | None:
    return max(roots, key=lambda r: version_key(version_of(r)), default=None)


def skills_in(root: Path) -> list[str]:
    return sorted(p.parent.name for p in (root / "skills").glob("*/SKILL.md"))


def sheet_path(home: Path, host: str) -> Path:
    return {
        "claude": home / ".claude/pstack-models.md",
        "codex": home / ".codex/pstack-models.md",
        "cursor": home / ".cursor/rules/pstack-models.mdc",
        "grok": home / ".grok/pstack-models.md",
    }[host]


def detect_host(home: Path) -> str:
    for host in ("cursor", "grok", "codex", "claude"):
        if os.environ.get(f"{host.upper()}_AGENT") or os.environ.get(f"{host.upper()}_HOME"):
            return host
    if os.environ.get("CLAUDE_CODE_ENTRYPOINT") or os.environ.get("CLAUDECODE"):
        return "claude"
    for host in HOSTS:
        if (home / f".{host}").is_dir():
            return host
    return "claude"


def instruction_files(project: Path, host: str) -> list[Path]:
    names = {
        "claude": ["CLAUDE.md", ".claude/CLAUDE.md", "AGENTS.md"],
        "codex": ["AGENTS.md"],
        "cursor": ["AGENTS.md", ".cursor/rules"],
        "grok": ["AGENTS.md", "CLAUDE.md", ".grok/rules"],
    }[host]
    return [project / n for n in names if (project / n).exists()]


def progress_sections(project: Path) -> list[str]:
    f = project / "progress.md"
    if not f.is_file():
        return []
    wanted = ("Current outputs", "Completed", "Decisions", "Open issues", "Next action")
    text = f.read_text(errors="replace")
    return [w for w in wanted if re.search(rf"^##\s+{re.escape(w)}", text, re.M)]


def permission_surface(home: Path, project: Path, host: str) -> str:
    checks = {
        "claude": [project / ".claude/settings.json", home / ".claude/settings.json"],
        "codex": [home / ".codex/config.toml"],
        "cursor": [project / ".cursor/hooks.json", home / ".cursor/hooks.json"],
        "grok": [project / ".grok/config.toml", home / ".grok/config.toml",
                 home / ".claude/settings.json"],
    }[host]
    for f in checks:
        if not f.is_file():
            continue
        text = f.read_text(errors="replace")
        if host == "claude" and '"deny"' in text:
            return f"deny rules in {f}"
        if host == "codex" and ("sandbox" in text or "approval" in text):
            return f"sandbox/approval in {f}"
        if host == "cursor" and '"stop"' in text:
            return f"stop hook in {f}"
        if host == "grok" and ("[permission" in text or '"deny"' in text):
            return f"permission rules in {f}"
    return "absent"


def rea_surface(home: Path) -> str:
    if shutil.which("rea"):
        return "rea CLI on PATH"
    for f in (home / ".claude.json", home / ".cursor/mcp.json", home / ".codex/config.toml",
              home / ".grok/config.toml"):
        if f.is_file() and "rea" in f.read_text(errors="replace"):
            return f"rea MCP in {f}"
    return "absent"


def probe(home: Path, project: Path, host: str) -> dict:
    root = pick_root(plugin_roots(home, host))
    skills = skills_in(root) if root else []
    missing = [s for s in COMMON_CORE if s not in skills]
    sheet = sheet_path(home, host)
    sections = progress_sections(project)
    layers = {
        "L1": {"ok": bool(instruction_files(project, host)) and (project / ".specify").is_dir(),
               "detail": f"instructions={[str(p.relative_to(project)) for p in instruction_files(project, host)]} "
                         f".specify={(project / '.specify').is_dir()}"},
        "L2": {"ok": bool(root) and not missing,
               "detail": f"pstack={'%s@%s' % (version_of(root), host) if root else 'unavailable'} missing_core={missing}"},
        "L3": {"ok": rea_surface(home) != "absent", "detail": rea_surface(home)},
        "L4": {"ok": permission_surface(home, project, host) != "absent",
               "detail": permission_surface(home, project, host)},
        "L5": {"ok": bool(root) and "interrogate" in skills,
               "detail": "interrogate present" if "interrogate" in skills else "no independent reviewer skill"},
        "L6": {"ok": True, "detail": f"sheet={'present' if sheet.is_file() else 'defaults'} ({sheet})"},
        "L7": {"ok": "Next action" in sections,
               "detail": f"progress.md sections={sections}"},
    }
    return {
        "host": host,
        "pstack_root": str(root) if root else None,
        "pstack_version": version_of(root) if root else None,
        "skills": skills,
        "missing_common_core": missing,
        "sheet": str(sheet),
        "sheet_present": sheet.is_file(),
        "layers": layers,
        "breadcrumbs": [
            f"pstack: {version_of(root) if root else 'unavailable'}|{host}",
            "harness: " + "|".join(f"{k} {'ok' if v['ok'] else 'gap'}" for k, v in layers.items()),
        ],
    }


def check_map(map_path: Path, skills: list[str]) -> list[str]:
    """Return problems: common-core names in the map that are not installed, or
    a map bullet that disagrees with COMMON_CORE."""
    text = map_path.read_text(errors="replace")
    m = re.search(r"\*\*Common core[^:]*:\*\*(.*?)(?:\n- \*\*|\n\n)", text, re.S)
    if not m:
        return [f"{map_path}: no 'Common core' bullet found"]
    listed = set(re.findall(r"`([a-z0-9-]+)`", m.group(1))) - {"principle-*"}
    problems = []
    for name in sorted(listed - set(COMMON_CORE)):
        problems.append(f"{map_path}: `{name}` is in the Common core bullet but not in COMMON_CORE")
    for name in sorted(set(COMMON_CORE) - listed):
        problems.append(f"{map_path}: `{name}` is in COMMON_CORE but not in the Common core bullet")
    if skills:
        for name in sorted(listed & set(COMMON_CORE)):
            if name not in skills:
                problems.append(f"installed pstack lacks common-core skill `{name}`")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="auto", choices=("auto", *HOSTS))
    ap.add_argument("--project", default=".")
    ap.add_argument("--home", default=str(Path.home()))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-map", metavar="PATH")
    args = ap.parse_args(argv)
    home = Path(args.home).expanduser()
    project = Path(args.project).resolve()
    host = detect_host(home) if args.host == "auto" else args.host
    result = probe(home, project, host)
    problems = check_map(Path(args.check_map), result["skills"]) if args.check_map else []
    result["map_problems"] = problems
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"host: {host}")
        print(f"pstack: {result['pstack_version'] or 'unavailable'} {result['pstack_root'] or ''}".rstrip())
        if result["missing_common_core"]:
            print(f"missing common core: {', '.join(result['missing_common_core'])}")
        print(f"sheet: {'present' if result['sheet_present'] else 'absent'} {result['sheet']}")
        for k, v in result["layers"].items():
            print(f"{k} {'ok ' if v['ok'] else 'gap'} {v['detail']}")
        for line in result["breadcrumbs"]:
            print(line)
        for p in problems:
            print(f"map: {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
