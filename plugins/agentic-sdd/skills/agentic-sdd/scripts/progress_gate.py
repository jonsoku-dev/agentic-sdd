#!/usr/bin/env python3
"""Check the completion gate in progress.md before a feature or the Final Goal is called done.

usage: progress_gate.py [progress.md]
Needs, at column 1: a `pstack: O-interrogate|…` line, and `rea: <feature>|pass|ev_…` for every
feature directory under specs/ (or .specify/specs/) next to progress.md. A BLOCKED review line
fails the gate on purpose. Breadcrumbs written as bullets or inside backticks are reported with
the line to rewrite. Exit 0 ok, 1 gate open, 2 no progress.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PREFIX = r"(?:pstack|harness|ROUTING|rea):"
SELF_REVIEW = re.compile(r"(?i)self[- ]review|no (?:sub)?agent|not independent|without (?:a )?(?:sub)?agent|primary (?:self|own)|\|inline\b")
MISFORMED = re.compile(rf"^\s*(?:[-*]\s+|\d+[.)]\s+)?`?{PREFIX}|^\s+{PREFIX}")


def check(progress: Path) -> list[str]:
    text = progress.read_text(errors="replace")
    lines = text.splitlines()
    problems = [f"line {n}: rewrite at column 1 without bullet or backticks: {l.strip()[:120]}"
                for n, l in enumerate(lines, 1) if MISFORMED.match(l) and not re.match(PREFIX, l)]
    reviews = [l for l in lines if l.startswith("pstack: O-interrogate|")]
    if not reviews:
        problems.append("missing: pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings")
    elif any("BLOCKED" in l for l in reviews):
        problems.append("review is BLOCKED: independent review; the Final Goal stays open")
    elif all(SELF_REVIEW.search(l) for l in reviews):
        problems.append("the review line describes a self-review; spawn a reviewer subagent, or write "
                        "BLOCKED: independent review and leave the Final Goal open")
    root = progress.parent
    features = sorted({d.name for d in [*root.glob("specs/*/"), *root.glob(".specify/specs/*/")] if d.is_dir()})
    for f in features:
        if not re.search(rf"^rea: {re.escape(f)}\|pass\|ev_\w+", text, re.M):
            problems.append(f"missing: rea: {f}|pass|<ev_… id copied verbatim>")
    return problems


def main(argv: list[str]) -> int:
    progress = Path(argv[1] if len(argv) > 1 else "progress.md")
    if not progress.is_file():
        print(f"no {progress}")
        return 2
    problems = check(progress)
    for p in problems:
        print(p)
    print("ok" if not problems else f"gate open: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
