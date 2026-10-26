#!/usr/bin/env python3
"""The only completion predicate for an agentic-sdd Final Goal.

usage: progress_gate.py [progress.md]

A feature directory under specs/ or .specify/specs/ (except overview scaffolds)
closes with one column-1 line:

    rea: <feature>|pass|ev_<id>
    rea: <feature>|not-applicable|<why there is no runnable or build artifact>

blocked-limitation and tasks-appended do not close. A directory that predates
this Final Goal is omitted only by:

    gate: exclude|<feature-directory>|<why it predates this Final Goal>

Also required at column 1: one real reviewer line
`pstack: O-interrogate|<host>|<subagent_type> → <n> findings`.
BLOCKED, a self-review, a bulleted or backticked breadcrumb, or a secret-shaped
token leaves the gate open. Exit 0 ok, 1 gate open, 2 no progress.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PREFIX = r"(?:pstack|harness|ROUTING|rea|gate):"
NOT_FEATURES = {"overview", "000-overview"}
SELF_REVIEW = re.compile(r"(?i)self[- ]review|no (?:sub)?agent|not independent|without (?:a )?(?:sub)?agent|primary (?:self|own)|\|inline\b")
# high-confidence token shapes only; progress.md is copied into reports and the dashboard
SECRET = re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}|sk-ant-[A-Za-z0-9_-]{20,}"
                    r"|sk-(?:proj-)?[A-Za-z0-9_-]{32,}|xox[abposr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
MISFORMED = re.compile(rf"^\s*(?:[-*]\s+|\d+[.)]\s+)?`?{PREFIX}|^\s+{PREFIX}")
PASS_LINE = re.compile(r"^rea: ([^|]+)\|pass\|ev_\w+")
NA_LINE = re.compile(r"^rea: ([^|]+)\|not-applicable\|(\S.*)$")
EXCLUDE_LINE = re.compile(r"^gate: exclude\|([^|]+)\|(\S.*)$")

# "Final Goal met", "The Final Goal is met", "Final Goal: complete"; not "Final Goal NOT met"
MET = re.compile(r"(?i)\bfinal goal\b[\s:*_`'\"-]*(?:is\s+|has been\s+|was\s+)?(?:now\s+)?(?:fully\s+)?"
                 r"(?:met|complete|completed|done|achieved)\b")


def claims_met(text: str) -> bool:
    return bool(MET.search(text))


def feature_names(root: Path) -> list[str]:
    found: list[str] = []
    for pattern in ("specs/*/", ".specify/specs/*/"):
        for directory in root.glob(pattern):
            if directory.is_dir() and directory.name not in NOT_FEATURES:
                found.append(directory.name)
    return sorted(set(found))


def _closed(lines: list[str]) -> set[str]:
    closed: set[str] = set()
    for line in lines:
        match = PASS_LINE.match(line) or NA_LINE.match(line)
        if match:
            closed.add(match.group(1))
    return closed


def _exclusions(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    found: dict[str, str] = {}
    problems: list[str] = []
    for number, line in enumerate(lines, 1):
        if not line.startswith("gate:"):
            continue
        match = EXCLUDE_LINE.match(line)
        if match is None:
            problems.append("line %d: gate: lines must be `gate: exclude|<feature-directory>|<why it predates this Final Goal>`" % number)
            continue
        found[match.group(1)] = match.group(2).strip()
    return found, problems


def check(progress: Path) -> list[str]:
    text = progress.read_text(errors="replace")
    lines = text.splitlines()
    problems = [f"line {n}: rewrite at column 1 without bullet or backticks: {l.strip()[:120]}"
                for n, l in enumerate(lines, 1) if MISFORMED.match(l) and not re.match(PREFIX, l)]
    problems += [f"line {n}: looks like a secret; replace it with <REDACTED> and keep the value in the environment"
                 for n, l in enumerate(lines, 1) if SECRET.search(l)]
    reviews = [l for l in lines if l.startswith("pstack: O-interrogate|")]
    if not reviews:
        problems.append("missing: pstack: O-interrogate|<host>|<reviewer subagent_type> → <n> findings")
    elif any("BLOCKED" in l for l in reviews):
        problems.append("review is BLOCKED: independent review; the Final Goal stays open")
    elif all(SELF_REVIEW.search(l) for l in reviews):
        problems.append("the review line describes a self-review; spawn a reviewer subagent, or write "
                        "BLOCKED: independent review and leave the Final Goal open")
    excluded, exclude_problems = _exclusions(lines)
    problems += exclude_problems
    names = feature_names(progress.parent)
    for name in sorted(excluded):
        if name not in names:
            problems.append(f"gate: exclude|{name}|… names no feature directory under specs/ or .specify/specs/")
    closed = _closed(lines)
    for feature in names:
        if feature in excluded:
            continue
        if feature not in closed:
            problems.append(
                f"missing: rea: {feature}|pass|<ev_… id> or rea: {feature}|not-applicable|<why no runnable artifact> "
                f"(or gate: exclude|{feature}|<why it predates this Final Goal>)"
            )
    return problems


def main(argv: list[str]) -> int:
    progress = Path(argv[1] if len(argv) > 1 else "progress.md")
    if not progress.is_file():
        print(f"no {progress}")
        return 2
    problems = check(progress)
    for problem in problems:
        print(problem)
    print("ok" if not problems else f"gate open: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
