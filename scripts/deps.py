#!/usr/bin/env python3
"""Check and update everything agentic-sdd depends on, per host.

    python3 scripts/deps.py check            # table of installed vs latest; exit 1 when anything is behind
    python3 scripts/deps.py check --json
    python3 scripts/deps.py update --yes     # update what this script can update, then relink via install.sh
    python3 scripts/deps.py update --yes --hosts   # also run each host CLI's own self-update

Components: Spec Kit CLI (uv tool), pstack on Claude Code / Codex / Grok Build
(pstack-claude marketplace) and Cursor (official plugin, IDE-installed),
rea-agents pins in every host MCP config, and the host CLIs themselves.
Stdlib only. Network: GitHub contents/releases API and the npm registry.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HOME = Path(os.environ.get("AGENTIC_SDD_HOME", Path.home()))
SRC = Path(__file__).resolve().parent.parent
PSTACK_CLAUDE_REPO = "michael-denyer/pstack-claude"
CURSOR_PLUGINS_REPO = "cursor/plugins"
SPEC_KIT_REPO = "github/spec-kit"

REA_CONFIGS = [
    HOME / ".claude.json",
    HOME / ".cursor/mcp.json",
    HOME / ".codex/config.toml",
    HOME / ".grok/config.toml",
    HOME / "Library/Application Support/Claude/claude_desktop_config.json",
    HOME / ".gemini/config/mcp_config.json",
    HOME / ".hermes/config.yaml",
]
REA_PIN = re.compile(r"rea-agents@(\d+\.\d+\.\d+)")


# ---------- helpers ----------

def run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, str(e)


def fetch_json(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": "agentic-sdd-deps", "Accept": "application/vnd.github+json"})
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:
        if shutil.which("gh") and "api.github.com" in url:
            rc, out = run(["gh", "api", url.split("api.github.com/", 1)[1]])
            if rc == 0:
                try:
                    return json.loads(out)
                except json.JSONDecodeError:
                    return None
        return None


def github_file_json(repo: str, path: str) -> dict | None:
    d = fetch_json(f"https://api.github.com/repos/{repo}/contents/{path}")
    if not d or "content" not in d:
        return None
    try:
        return json.loads(base64.b64decode(d["content"]).decode())
    except (ValueError, json.JSONDecodeError):
        return None


def vtuple(v: str | None) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:4]) or (0,)


def behind(installed: str | None, latest: str | None) -> bool:
    return bool(latest) and (not installed or vtuple(installed) < vtuple(latest))


def plugin_version(root: Path) -> str | None:
    for manifest in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        p = root / manifest
        if p.is_file():
            try:
                return json.loads(p.read_text()).get("version")
            except (OSError, json.JSONDecodeError):
                return None
    return None


def highest(roots) -> str | None:
    versions = [v for v in (plugin_version(r) for r in roots) if v]
    return max(versions, key=vtuple) if versions else None


# ---------- latest lookups (network) ----------

def latest_versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    rel = fetch_json(f"https://api.github.com/repos/{SPEC_KIT_REPO}/releases/latest")
    out["spec-kit"] = (rel or {}).get("tag_name", "").lstrip("v") or None
    pc = github_file_json(PSTACK_CLAUDE_REPO, "plugins/pstack/.claude-plugin/plugin.json")
    out["pstack-claude"] = (pc or {}).get("version")
    cu = github_file_json(CURSOR_PLUGINS_REPO, "pstack/.cursor-plugin/plugin.json")
    out["pstack-cursor"] = (cu or {}).get("version")
    npm = fetch_json("https://registry.npmjs.org/rea-agents/latest")
    out["rea-agents"] = (npm or {}).get("version")
    return out


# ---------- installed lookups (local) ----------

def installed_versions(home: Path = HOME) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    # `uv tool list` prints "specify-cli vX.Y.Z"; `specify version` prints a banner and a rich table.
    text = run(["uv", "tool", "list"])[1] if shutil.which("uv") else ""
    m = re.search(r"specify-cli\s+v?(\d+\.\d+\.\d+)", text)
    if not m and shutil.which("specify"):
        text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", run(["specify", "version"])[1])
        m = re.search(r"(?:specify|version|CLI)\D{0,40}v?(\d+\.\d+\.\d+)", text, re.I)
    out["spec-kit"] = m.group(1) if m else None
    out["pstack@claude"] = highest([*home.glob(".claude/plugins/cache/*/pstack/*"),
                                    *home.glob(".claude/plugins/marketplaces/*/plugins/pstack")])
    out["pstack@codex"] = highest(home.glob(".codex/plugins/cache/*/pstack/*"))
    out["pstack@grok"] = highest([*home.glob(".grok/installed-plugins/pstack-*"),
                                  *home.glob(".grok/marketplace-cache/*/plugins/pstack")])
    out["pstack@cursor"] = highest(home.glob(".cursor/plugins/cache/*/pstack/*"))
    pins = rea_pins()
    out["rea-agents"] = min(pins.values(), key=vtuple) if pins else None
    for name, cmd in (("claude", ["claude", "--version"]), ("codex", ["codex", "--version"]),
                      ("grok", ["grok", "--version"]), ("cursor-agent", ["agent", "--version"])):
        if shutil.which(cmd[0]):
            rc, text = run(cmd, timeout=30)
            m = re.search(r"(\d+\.\d+\.\d+|\d{4}\.\d{2}\.\d{2}[\w.-]*)", text)
            out[f"cli:{name}"] = m.group(1) if m else (text.splitlines() or ["?"])[0][:30]
        else:
            out[f"cli:{name}"] = None
    for tool in ("node", "bun", "uv", "gh", "npx"):
        out[f"tool:{tool}"] = "present" if shutil.which(tool) else None
    return out


def rea_pins(configs=REA_CONFIGS) -> dict[str, str]:
    pins = {}
    for p in configs:
        if p.is_file():
            m = REA_PIN.search(p.read_text(errors="replace"))
            if m:
                pins[str(p)] = m.group(1)
    return pins


# ---------- plan ----------

UPDATE_CMDS = {
    "spec-kit": [["uv", "tool", "install", "--force", "--from", f"git+https://github.com/{SPEC_KIT_REPO}.git", "specify-cli"]],
    "pstack@claude": [["claude", "plugin", "marketplace", "update", "pstack-claude"],
                      ["claude", "plugin", "update", "pstack@pstack-claude"]],
    "pstack@codex": [["codex", "plugin", "marketplace", "upgrade"],
                     ["codex", "plugin", "add", "pstack@pstack-claude"]],
    # Grok's pstack is sourced from the pstack-claude marketplace cache; refresh the source first.
    "pstack@grok": [["grok", "plugin", "marketplace", "update", "pstack-claude"], ["grok", "plugin", "update"]],
    "cli:claude": [["claude", "update"]],
    "cli:codex": [["codex", "update"]],
    "cli:grok": [["grok", "update"]],
    "cli:cursor-agent": [["agent", "update"]],
}
MANUAL = {
    "pstack@cursor": "Cursor IDE: Settings → Plugins → pstack → Update (or `/add-plugin pstack`), then `install.sh --cursor-cli-skills`",
}


def rows(installed: dict, latest: dict) -> list[dict]:
    r = []
    def add(name, inst, lat, how):
        r.append({"component": name, "installed": inst, "latest": lat, "behind": behind(inst, lat), "update": how})
    add("spec-kit (specify)", installed["spec-kit"], latest["spec-kit"], " && ".join(" ".join(c) for c in UPDATE_CMDS["spec-kit"]))
    for host in ("claude", "codex", "grok"):
        add(f"pstack@{host}", installed[f"pstack@{host}"], latest["pstack-claude"], " && ".join(" ".join(c) for c in UPDATE_CMDS[f"pstack@{host}"]))
    add("pstack@cursor", installed["pstack@cursor"], latest["pstack-cursor"], MANUAL["pstack@cursor"])
    add("rea-agents (pins)", installed["rea-agents"], latest["rea-agents"], "deps.py update rewrites every host MCP pin and warms the npx cache; restart hosts")
    for name in ("claude", "codex", "grok", "cursor-agent"):
        add(f"cli:{name}", installed[f"cli:{name}"], None, " ".join(UPDATE_CMDS[f"cli:{name}"][0]) + " (--hosts)")
    for tool in ("node", "bun", "uv", "gh", "npx"):
        add(f"tool:{tool}", installed[f"tool:{tool}"], None, "install manually" if not installed[f"tool:{tool}"] else "")
    return r


def print_table(r: list[dict]) -> None:
    w = max(len(x["component"]) for x in r)
    print(f"{'component'.ljust(w)}  {'installed'.ljust(12)} {'latest'.ljust(10)} status")
    for x in r:
        status = "BEHIND" if x["behind"] else ("missing" if x["installed"] is None else "ok")
        print(f"{x['component'].ljust(w)}  {str(x['installed'] or '-').ljust(12)} {str(x['latest'] or '-').ljust(10)} {status}")
    outdated = [x for x in r if x["behind"]]
    if outdated:
        print("\nupdate:")
        for x in outdated:
            print(f"  {x['component']}: {x['update']}")


# ---------- update ----------

def repin_rea(version: str, configs=REA_CONFIGS) -> list[str]:
    changed = []
    for p in configs:
        if not p.is_file():
            continue
        t = p.read_text(errors="replace")
        t2 = REA_PIN.sub(f"rea-agents@{version}", t)
        if t2 != t:
            p.with_name(p.name + f".bak-rea-{version}").write_text(t)
            p.write_text(t2)
            changed.append(str(p))
    return changed


def do_update(r: list[dict], latest: dict, hosts: bool, dry: bool) -> int:
    failures = 0
    for x in r:
        name = x["component"].split(" ")[0]
        key = {"spec-kit": "spec-kit"}.get(name, name)
        if name.startswith("cli:") and not hosts:
            continue
        if not x["behind"] and not name.startswith("cli:"):
            continue
        if key == "rea-agents":
            v = latest["rea-agents"]
            if dry:
                print(f"[dry] repin rea-agents@{v} in {len(rea_pins())} configs")
                continue
            changed = repin_rea(v)
            print(f"rea-agents: repinned {len(changed)} config(s) to {v}; warming npx cache")
            rc, out = run(["npx", "-y", f"rea-agents@{v}", "--version"], timeout=600)
            print(f"  npx rea-agents@{v}: rc={rc}")
            print("  restart Claude Code / Cursor / Codex / Grok (and the desktop apps) so each MCP server respawns on the new pin")
            continue
        cmds = UPDATE_CMDS.get(key)
        if not cmds:
            print(f"{name}: manual -> {x['update']}")
            continue
        if not shutil.which(cmds[0][0]):
            print(f"{name}: skipped ({cmds[0][0]} not on PATH)")
            continue
        for c in cmds:
            if dry:
                print(f"[dry] {' '.join(c)}")
                continue
            rc, out = run(c, timeout=900)
            tail = out.splitlines()[-1][:120] if out else ""
            print(f"{name}: {' '.join(c)} -> rc={rc} {tail}")
            if rc != 0:
                failures += 1
                break
    if not dry:
        # plugin roots and cache hashes change on update; relink everything install.sh owns
        inst = SRC / "install.sh"
        if inst.is_file():
            rc, out = run(["bash", str(inst), "--codex-mandate", "--grok-mandate", "--grok-agents", "--cursor-cli-skills"], timeout=300)
            print(f"install.sh relink -> rc={rc}")
    return failures


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["check", "update"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--yes", action="store_true", help="update: actually run the update commands")
    ap.add_argument("--hosts", action="store_true", help="update: also run each host CLI's self-update")
    a = ap.parse_args(argv)
    inst = installed_versions()
    lat = latest_versions()
    r = rows(inst, lat)
    if a.action == "check":
        if a.json:
            print(json.dumps(r, indent=2))
        else:
            print_table(r)
        return 1 if any(x["behind"] for x in r) else 0
    print_table(r)
    print()
    return 1 if do_update(r, lat, hosts=a.hosts, dry=not a.yes) else 0


if __name__ == "__main__":
    sys.exit(main())
