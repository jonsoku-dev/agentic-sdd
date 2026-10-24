#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt (https://llmstxt.org/) from the repository docs.

    python3 scripts/build_llms.py          # rewrite both files
    python3 scripts/build_llms.py --check  # exit 1 when they are stale or a link is dead

llms.txt lists every document an agent should read, with one-line descriptions
taken from references/INDEX.md where it has them. llms-full.txt inlines the same
files so a single fetch gives the whole skill.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/jonsoku-dev/agentic-sdd/main/"

SECTIONS = [
    ("Start here", [
        ("README.md", "Install (one-shot), per-host setup, keeping dependencies current, uninstall, evidence, license"),
        ("SKILL.md", "The skill entrypoint: Final Goal driver, phase contracts, universal first actions, hard boundaries"),
        ("references/INDEX.md", "Load map: which reference to open at which step"),
    ]),
    ("Core references", [
        "references/spec-kit-alignment.md", "references/phase-contract.md", "references/harness-layers.md",
        "references/pstack-integration.md", "references/single-loop-default.md", "references/poteto-mode-anatomy.md", "references/model-routing.md",
        "references/rea-closeout.md", "references/recovery.md", "references/direction-keeper.md",
        "references/verification-execution.md", "references/host-guide-greenfield-brownfield.md",
        "references/starting-tool-considerations.md", "references/agent-compatibility.md", "references/cursor-continuation.md",
    ]),
    ("Supporting references", [
        "references/cost-modes.md", "references/multi-perspective-review.md", "references/compaction-timing.md",
        "references/bug-workflow.md", "references/anti-patterns.md", "references/anti-oververification.md",
        "references/edge-cases-and-failure-modes.md", "references/main-model-guide.md", "references/progress-template.md",
        "references/spec-template.md", "references/overview-template.md", "references/kanban-board.md",
        "references/provider-personas-and-docs.md",
    ]),
    ("Templates and scripts", [
        ("templates/playbooks/agentic-sdd.md", "pstack project playbook: three Spec Kit handoffs anchored on Feature and Bug fix steps (pstack-claude port)"),
        ("templates/cursor-rules/agentic-sdd.mdc", "Cursor project rule carrying the same handoffs; Cursor's plugin cannot invoke poteto-mode itself"),
        ("scripts/harness_probe.py", "Readiness probe for the seven harness layers per host; prints the progress.md breadcrumbs"),
        ("scripts/setup.py", "One-shot setup: detect, plan, confirm, apply, verify"),
        ("scripts/deps.py", "Installed-vs-latest check and unattended update for Spec Kit, pstack per host, REA pins, host CLIs"),
        ("install.sh", "Installer and exact-inverse uninstaller"),
    ]),
    ("Evidence", [
        ("docs/BENCHMARKS.md", "Method, routing table, gate-by-gate matrix of what each host invoked at every Spec Kit gate, result comparisons, A/B against plain Spec Kit"),
        ("docs/evals/2026-10-20-host-matrix/result.md", "Four hosts × routing prompts, a real feature, and a three-part goal; black-box, converge count, REA ids, cost"),
        ("docs/evals/2026-10-20-host-matrix/prediction.md", "Pre-registered predictions for that matrix"),
        ("docs/evals/2026-10-19-sandbox-ab/result.md", "Spec Kit alone versus this stack on one brief"),
    ]),
]
OPTIONAL = [
    ("CHANGELOG.md", "Release history (release-please, Conventional Commits)"),
    ("LICENSE", "MIT"),
    ("visualizer/index.html", "Optional Kanban over Spec Kit artifacts"),
    ("evals/evals.json", "Behavioral eval cases"),
]
SUMMARY = ("Spec-Driven Development that finishes: one skill that drives GitHub Spec Kit end to end on "
           "Claude Code, Codex, Cursor, and Grok Build, runs pstack inside every phase, and closes a feature "
           "only on REA runtime evidence. One converge per spec; small specs; seven harness layers probed per host.")
DETAILS = ("Read SKILL.md first, then references/INDEX.md for which reference the current step needs. "
           "Paths are relative to the repository root; the links below point at the raw files on the main branch.\n\n"
           "To install on the machine you are running on: run `npx agentic-sdd --dry-run` (node 20+, python3, git), show the user "
           "the detected state and the full plan including manual items, ask once, and only on yes run `npx agentic-sdd --yes`. Then "
           "report the verify output, what must be restarted, and what must be done inside an IDE. Change nothing the "
           "plan did not list. The README's \"Agent mode\" section holds the same procedure as a paste-ready prompt.")


def index_descriptions() -> dict[str, str]:
    desc = {}
    for line in (ROOT / "references/INDEX.md").read_text().splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            desc["references/" + m.group(1)] = m.group(2)
    return desc


def entries():
    desc = index_descriptions()
    for title, items in SECTIONS:
        rows = []
        for it in items:
            path, d = (it, desc.get(it, "")) if isinstance(it, str) else it
            rows.append((path, d))
        yield title, rows
    yield "Optional", OPTIONAL


def render_llms() -> str:
    out = ["# agentic-sdd", "", f"> {SUMMARY}", "", DETAILS, ""]
    for title, rows in entries():
        out.append(f"## {title}")
        out.append("")
        for path, d in rows:
            out.append(f"- [{path}]({RAW}{path})" + (f": {d}" if d else ""))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_full() -> str:
    out = ["# agentic-sdd (full)", "", f"> {SUMMARY}", "", "Every file listed in llms.txt, inlined. Generated by scripts/build_llms.py.", ""]
    for title, rows in entries():
        if title == "Optional":
            continue
        for path, _ in rows:
            p = ROOT / path
            if p.suffix in (".py", ".sh"):
                continue  # code is linked from llms.txt; the full file carries the prose
            out.append(f"\n---\n\n<!-- file: {path} -->\n")
            out.append(p.read_text(errors="replace").rstrip())
    return "\n".join(out).rstrip() + "\n"


def main(argv=None) -> int:
    check = "--check" in (argv or sys.argv[1:])
    dead = [path for _, rows in entries() for path, _ in rows if not (ROOT / path).is_file()]
    if dead:
        print("dead links:", ", ".join(dead))
        return 1
    llms, full = render_llms(), render_full()
    if check:
        stale = [n for n, body in (("llms.txt", llms), ("llms-full.txt", full))
                 if not (ROOT / n).is_file() or (ROOT / n).read_text() != body]
        if stale:
            print("stale:", ", ".join(stale), "(run scripts/build_llms.py)")
            return 1
        print("llms.txt and llms-full.txt are current")
        return 0
    (ROOT / "llms.txt").write_text(llms)
    (ROOT / "llms-full.txt").write_text(full)
    print(f"wrote llms.txt ({len(llms)} bytes) and llms-full.txt ({len(full)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
