#!/usr/bin/env python3
"""One-shot setup: detect this machine, show the plan, ask once, apply, verify.

    python3 scripts/setup.py              # detect → plan → "Proceed? [y/N]" → apply → verify
    python3 scripts/setup.py --dry-run    # detect and plan only
    python3 scripts/setup.py --yes        # apply without the prompt
    python3 scripts/setup.py --project DIR   # also install the project playbook / Cursor rule into DIR

What it configures, per host it finds (claude / codex / cursor / grok):
  prerequisites (uv, node, bun, gh via Homebrew when brew exists), the Spec Kit CLI,
  pstack (pstack-claude marketplace on Claude Code / Codex / Grok; Cursor's is IDE-only),
  REA MCP registration through `rea setup --client <id>`, this skill's symlinks,
  the Codex AGENTS.md mandate block, the Grok home rule + agent links, Cursor's
  Agent CLI skill links and the sdd-continue stop hook.
It never touches a host it cannot find, never edits a file outside the marked
blocks and named entries install.sh owns, and prints everything it will run
before asking.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deps  # noqa: E402

SRC = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("AGENTIC_SDD_HOME", Path.home()))
INSTALL = SRC / "install.sh"
MARKETPLACE = "michael-denyer/pstack-claude"
REA_CLIENT = {"claude": "claude_code", "codex": "codex", "cursor": "cursor", "grok": "grok_build"}
SKILL_DIRS = {"agents": ".agents/skills", "claude": ".claude/skills", "codex": ".codex/skills",
              "cursor": ".cursor/skills", "grok": ".grok/skills"}


def run(cmd, timeout=600, env=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, str(e)


# ---------- detect ----------

def detect(home: Path = HOME) -> dict:
    d: dict = {"hosts": {}, "tools": {}, "pstack": {}, "rea": {}, "wiring": {}, "sheets": {}}
    d["hosts"]["claude"] = bool(shutil.which("claude"))
    d["hosts"]["codex"] = bool(shutil.which("codex"))
    d["hosts"]["cursor"] = bool(shutil.which("agent")) or (home / ".cursor").is_dir()
    d["hosts"]["grok"] = bool(shutil.which("grok"))
    for t in ("git", "node", "npx", "uv", "bun", "gh", "brew", "python3"):
        d["tools"][t] = bool(shutil.which(t))
    inst = deps.installed_versions(home)
    lat = deps.latest_versions()
    d["spec_kit"] = {"installed": inst["spec-kit"], "latest": lat["spec-kit"]}
    for h in ("claude", "codex", "grok"):
        d["pstack"][h] = {"installed": inst[f"pstack@{h}"], "latest": lat["pstack-claude"]}
    d["pstack"]["cursor"] = {"installed": inst["pstack@cursor"], "latest": lat["pstack-cursor"]}
    pins = deps.rea_pins([home / p for p in (".claude.json", ".cursor/mcp.json", ".codex/config.toml", ".grok/config.toml")])
    # offline fallback: the newest pin already on this machine, else npm's "latest" tag
    d["rea_latest"] = lat["rea-agents"] or (max(pins.values(), key=deps.vtuple) if pins else "latest")
    d["rea"]["claude"] = _has(home / ".claude.json", r'"rea"\s*:')
    d["rea"]["codex"] = _has(home / ".codex/config.toml", r"\[mcp_servers\.rea\]")
    d["rea"]["cursor"] = _has(home / ".cursor/mcp.json", r'"rea"\s*:')
    d["rea"]["grok"] = _has(home / ".grok/config.toml", r"\[mcp_servers\.rea\]") or (
        d["rea"]["cursor"] and _has(home / ".grok/config.toml", r"\[compat\.cursor\][^\[]*mcps\s*=\s*true"))
    d["rea_pins"] = deps.rea_pins([home / p for p in (".claude.json", ".cursor/mcp.json", ".codex/config.toml", ".grok/config.toml")])
    for k, rel in SKILL_DIRS.items():
        link = home / rel / "agentic-sdd"
        # the canonical checkout may itself live at ~/.agents/skills/agentic-sdd
        d["wiring"][f"link:{k}"] = link.exists() and link.resolve() == SRC.resolve()
    d["wiring"]["codex_mandate"] = _has(home / ".codex/AGENTS.md", r"pstack-mandate:start")
    d["wiring"]["grok_rule"] = (home / ".grok/rules/pstack-mandate.md").is_file()
    d["wiring"]["grok_agents"] = (home / ".grok/agents/poteto-agent.md").exists()
    d["wiring"]["cursor_hooks"] = _has(home / ".cursor/hooks.json", r"agentic-sdd-continue")
    pm = home / ".cursor/skills/poteto-mode"
    d["wiring"]["cursor_cli_skills"] = pm.is_symlink() and pm.exists()
    d["sheets"] = {"claude": (home / ".claude/pstack-models.md").is_file(),
                   "codex": (home / ".codex/pstack-models.md").is_file(),
                   "cursor": (home / ".cursor/rules/pstack-models.mdc").is_file(),
                   "grok": (home / ".grok/pstack-models.md").is_file()}
    return d


def _has(path: Path, pattern: str) -> bool:
    try:
        return bool(re.search(pattern, path.read_text(errors="replace"), re.S))
    except OSError:
        return False


# ---------- plan ----------

class Action:
    def __init__(self, host, what, cmds=None, manual=None):
        self.host, self.what, self.cmds, self.manual = host, what, cmds or [], manual

    def __str__(self):
        if self.manual:
            return f"[manual] {self.host:6} {self.what}: {self.manual}"
        return f"[auto]   {self.host:6} {self.what}: " + " && ".join(" ".join(c) for c in self.cmds)


def plan(d: dict, project: Path | None) -> list[Action]:
    acts: list[Action] = []
    hosts = [h for h, present in d["hosts"].items() if present]
    missing_tools = [t for t in ("uv", "node", "bun", "gh") if not d["tools"][t]]
    if missing_tools:
        if d["tools"]["brew"]:
            acts.append(Action("all", "prerequisites", [["brew", "install", *missing_tools]]))
        else:
            acts.append(Action("all", "prerequisites", manual=f"install {' '.join(missing_tools)} (no Homebrew found)"))
    if deps.behind(d["spec_kit"]["installed"], d["spec_kit"]["latest"]) or not d["spec_kit"]["installed"]:
        acts.append(Action("all", "Spec Kit CLI", deps.UPDATE_CMDS["spec-kit"]))
    for h in hosts:
        p = d["pstack"][h]
        if h == "cursor":
            if not p["installed"]:
                acts.append(Action(h, "pstack", manual="in the Cursor IDE run /add-plugin pstack, then rerun setup"))
            continue
        if not p["installed"]:
            add = {"claude": [["claude", "plugin", "marketplace", "add", MARKETPLACE], ["claude", "plugin", "install", "pstack@pstack-claude", "--scope", "user"]],
                   "codex": [["codex", "plugin", "marketplace", "add", MARKETPLACE], ["codex", "plugin", "add", "pstack@pstack-claude"]],
                   "grok": [["grok", "plugin", "marketplace", "add", MARKETPLACE], ["grok", "plugin", "install", "pstack@pstack-claude", "--trust"]]}[h]
            acts.append(Action(h, "pstack install", add))
        elif deps.behind(p["installed"], p["latest"]):
            acts.append(Action(h, "pstack update", deps.UPDATE_CMDS[f"pstack@{h}"]))
    for h in hosts:
        if not d["rea"].get(h):
            acts.append(Action(h, "REA MCP", [["npx", "-y", f"rea-agents@{d['rea_latest']}", "setup", "--yes", "--client", REA_CLIENT[h]]]))
    behind_pins = [p for p, v in d["rea_pins"].items() if deps.behind(v, d["rea_latest"])]
    if behind_pins:
        acts.append(Action("all", "REA pin update", [["python3", str(SRC / "scripts/deps.py"), "update", "--yes"]]))
    if not all(d["wiring"][f"link:{k}"] for k in SKILL_DIRS):
        acts.append(Action("all", "skill symlinks", [["bash", str(INSTALL), "--link-only"]]))
    if "codex" in hosts and not d["wiring"]["codex_mandate"]:
        acts.append(Action("codex", "mandate in AGENTS.md", [["bash", str(INSTALL), "--codex-mandate"]]))
    if "grok" in hosts and not (d["wiring"]["grok_rule"] and d["wiring"]["grok_agents"]):
        acts.append(Action("grok", "home rule + agent links", [["bash", str(INSTALL), "--grok-mandate", "--grok-agents"]]))
    if "cursor" in hosts:
        if d["pstack"]["cursor"]["installed"] and not d["wiring"]["cursor_cli_skills"]:
            acts.append(Action("cursor", "Agent CLI skill links", [["bash", str(INSTALL), "--cursor-cli-skills"]]))
        if not d["wiring"]["cursor_hooks"]:
            acts.append(Action("cursor", "sdd-continue stop hook", [["bash", str(INSTALL), "--apply-cursor-hooks"]]))
    if project is not None:
        acts.append(Action("project", str(project), [["bash", str(INSTALL), "--project", str(project)]]))
    for h in hosts:
        if not d["sheets"].get(h):
            acts.append(Action(h, "model sheet", manual="run /setup-pstack inside the host once to pin models per role (defaults work without it)"))
    return acts


def show(d: dict, acts: list[Action]) -> None:
    print("Detected")
    print("  hosts : " + ", ".join(f"{h}={'yes' if v else 'no'}" for h, v in d["hosts"].items()))
    print("  tools : " + ", ".join(f"{t}={'yes' if v else 'no'}" for t, v in d["tools"].items()))
    print(f"  Spec Kit: {d['spec_kit']['installed'] or '-'} (latest {d['spec_kit']['latest'] or '?'})")
    for h, p in d["pstack"].items():
        print(f"  pstack@{h}: {p['installed'] or '-'} (latest {p['latest'] or '?'})")
    print("  REA MCP: " + ", ".join(f"{h}={'yes' if v else 'no'}" for h, v in d["rea"].items()) + f"; pins {sorted(set(d['rea_pins'].values())) or '-'} (latest {d['rea_latest']})")
    print("  wiring : " + ", ".join(f"{k}={'ok' if v else 'missing'}" for k, v in d["wiring"].items()))
    print("  sheets : " + ", ".join(f"{h}={'yes' if v else 'no'}" for h, v in d["sheets"].items()))
    print()
    if not acts:
        print("Plan: nothing to do, everything is in place.")
        return
    print("Plan (in this order)")
    for i, a in enumerate(acts, 1):
        print(f"  {i:2}. {a}")


# ---------- apply ----------

def apply(acts: list[Action]) -> list[tuple[Action, bool, str]]:
    results = []
    for a in acts:
        if a.manual:
            results.append((a, True, "manual"))
            continue
        ok, last = True, ""
        for c in a.cmds:
            rc, out = run(c, timeout=1800)
            last = (out.splitlines() or [""])[-1][:160]
            # marketplace add on an already-configured marketplace is not a failure
            if rc != 0 and "marketplace" in c and "add" in c and re.search(r"already|exists", out, re.I):
                rc = 0
            print(f"  {' '.join(c)} -> rc={rc} {last}")
            if rc != 0:
                ok = False
                break
        results.append((a, ok, last))
    return results


def verify(d_before: dict, project: Path | None) -> None:
    print("\nVerify")
    rc, out = run(["python3", str(SRC / "scripts/deps.py"), "check"], timeout=300)
    print("\n".join("  " + l for l in out.splitlines()[:16]))
    for h, present in d_before["hosts"].items():
        if not present:
            continue
        rc, out = run(["python3", str(SRC / "scripts/harness_probe.py"), "--host", h, "--project", str(project or SRC)], timeout=120)
        lines = [l for l in out.splitlines() if l.startswith(("L2", "L3", "L5", "L6", "harness:"))]
        print(f"  probe {h}: " + " | ".join(lines[-1:]) if lines else f"  probe {h}: {out[-120:]}")
    print("\nNext: restart each host once (plugins and MCP servers load at start). In Cursor install pstack from the IDE if the plan marked it manual.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="apply without asking")
    ap.add_argument("--dry-run", action="store_true", help="show the plan only")
    ap.add_argument("--project", type=Path, help="repository to receive the project playbook and Cursor rule")
    ap.add_argument("--json", action="store_true", help="print detection and plan as JSON (implies --dry-run)")
    a = ap.parse_args(argv)
    project = a.project.resolve() if a.project else None
    if project is None and (Path.cwd() / ".specify").is_dir() and Path.cwd() != SRC:
        project = Path.cwd()
    d = detect()
    acts = plan(d, project)
    if a.json:
        print(json.dumps({"detected": d, "plan": [str(x) for x in acts]}, indent=2, default=str))
        return 0
    show(d, acts)
    auto = [x for x in acts if not x.manual]
    if a.dry_run or not auto:
        return 0
    if not a.yes:
        try:
            answer = input(f"\nProceed with the {len(auto)} automatic step(s)? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("Nothing changed.")
            return 2
    print("\nApplying")
    results = apply(acts)
    failed = [a for a, ok, _ in results if not ok]
    verify(d, project)
    if failed:
        print("\nFailed steps (rerun setup after fixing):")
        for a in failed:
            print(f"  {a}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
