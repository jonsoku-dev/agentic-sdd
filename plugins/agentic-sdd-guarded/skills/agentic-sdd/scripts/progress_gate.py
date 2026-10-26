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

A worktree this run created is recorded at column 1:

    gate: worktree|<absolute-path>

Only a recorded path that is still a git worktree, and is neither the main
checkout nor the current checkout, is a leftover. Other worktrees are left
alone. The refusal never says to remove the main checkout.

Also required at column 1: one real reviewer line
`pstack: O-interrogate|<host>|<subagent_type> → <n> findings`.
BLOCKED, a self-review, a bulleted or backticked breadcrumb, or a secret-shaped
token leaves the gate open. In-scope tasks.md files may contain at most 12
tasks and one Convergence header.

Hosts share STUCK_LIMIT. A refusal is identical when the progress.md text, the
problem list, and the git state are unchanged. The git state is HEAD plus
`git worktree list --porcelain`, or `nogit` when git fails. The second
identical refusal is stuck: the host allows the stop, rewrites a met claim to
"Final Goal is not met", and reports `NOT complete / blocked:`. That message
says the Final Goal is not met. `stop_hook_active` does not release a block.
A change to progress.md or the git state resets the count.

Exit 0 ok, 1 gate open, 2 no progress.md.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
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
WORKTREE_LINE = re.compile(r"^gate: worktree\|(\S.*)$")
TASK_LIMIT = 12
STUCK_LIMIT = 2
NOT_COMPLETE = "NOT complete / blocked:"
TASK_ID = re.compile(r"\bT\d{3,}\b")
CHECKBOX = re.compile(r"^\s*[-*]\s+\[[ xX]\]")
CONVERGE_HEADER = re.compile(r"^#{1,6}\s+.*\bConvergence\b", re.I)

# "Final Goal met", "The Final Goal is met", "Final Goal: complete"; not "Final Goal NOT met"
MET = re.compile(r"(?i)\bfinal goal\b[\s:*_`'\"-]*(?:is\s+|has been\s+|was\s+)?(?:now\s+)?(?:fully\s+)?"
                 r"(?:met|complete|completed|done|achieved)\b")


def claims_met(text: str) -> bool:
    return bool(MET.search(text))


def _git_state(start: Path) -> str:
    if shutil.which("git") is None:
        return "nogit"
    head = _git(start, "rev-parse", "HEAD")
    if head.returncode != 0:
        return "nogit"
    trees = _git(start, "worktree", "list", "--porcelain")
    if trees.returncode != 0:
        return "nogit"
    return head.stdout + trees.stdout


def refusal_key(progress: Path, problems: list[str]) -> str:
    text = progress.read_text(errors="replace")
    payload = text + "\n---\n" + "\n".join(problems) + "\n---\n" + _git_state(progress.parent)
    return hashlib.sha256(payload.encode()).hexdigest()


def _without_met_claim(text: str) -> str:
    return text.replace("Final Goal met", "Final Goal is not met")


def stuck_message(problems: list[str]) -> str:
    reason = "; ".join(_without_met_claim(problem) for problem in problems[:10]) or "completion gate stayed open"
    return (
        f"{NOT_COMPLETE} {reason}. "
        "The Final Goal is not met. "
        "The same refusal repeated with no change to progress.md or the git state, so this stop is allowed. "
        "The run is not complete."
    )


def clear_met_claim(progress: Path, message: str) -> None:
    text = progress.read_text(errors="replace")
    rewritten = MET.sub("Final Goal is not met", text)
    if message not in rewritten:
        if rewritten and not rewritten.endswith("\n"):
            rewritten += "\n"
        rewritten += message + "\n"
    if rewritten != text:
        progress.write_text(rewritten)


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
        if WORKTREE_LINE.match(line):
            continue
        match = EXCLUDE_LINE.match(line)
        if match is None:
            problems.append(
                "line %d: gate: lines must be `gate: exclude|<feature-directory>|<why it predates this Final Goal>`"
                " or `gate: worktree|<absolute-path>`" % number
            )
            continue
        found[match.group(1)] = match.group(2).strip()
    return found, problems


def task_count(text: str) -> int:
    ids = set(TASK_ID.findall(text))
    if ids:
        return len(ids)
    return sum(1 for line in text.splitlines() if CHECKBOX.match(line))


def _structural(root: Path, excluded: set[str]) -> list[str]:
    problems: list[str] = []
    for feature in feature_names(root):
        if feature in excluded:
            continue
        for tasks in (root / "specs" / feature / "tasks.md", root / ".specify" / "specs" / feature / "tasks.md"):
            if not tasks.is_file():
                continue
            text = tasks.read_text(errors="replace")
            count = task_count(text)
            if count > TASK_LIMIT:
                problems.append(
                    f"{tasks.relative_to(root)} has {count} tasks; the limit is {TASK_LIMIT}. "
                    "Split into a smaller spec before calling the Final Goal met."
                )
            headers = sum(1 for line in text.splitlines() if CONVERGE_HEADER.match(line))
            if headers > 1:
                problems.append(
                    f"{tasks.relative_to(root)} has {headers} Convergence headers; one converge per spec. "
                    "Carry the remaining gap into the next spec."
                )
    return problems


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    git = shutil.which("git") or "git"
    return subprocess.run([git, "-C", str(cwd), *args], capture_output=True, text=True)


def _repo_paths(start: Path) -> tuple[Path, Path, dict[Path, str] | str] | None:
    """Current toplevel, main checkout, and live worktrees keyed by resolved path.

    The third item is an error string when `git worktree list` fails.
    Returns None when start is not inside a worktree.
    """
    if shutil.which("git") is None:
        return None
    probe = _git(start, "rev-parse", "--is-inside-work-tree")
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return None
    top = _git(start, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or not top.stdout.strip():
        return None
    toplevel = Path(top.stdout.strip()).resolve()
    common = _git(toplevel, "rev-parse", "--git-common-dir")
    if common.returncode != 0 or not common.stdout.strip():
        return None
    common_path = Path(common.stdout.strip())
    if not common_path.is_absolute():
        common_path = toplevel / common_path
    common_path = common_path.resolve()
    main = common_path.parent.resolve() if common_path.name == ".git" else toplevel
    listed = _git(toplevel, "worktree", "list", "--porcelain")
    if listed.returncode != 0:
        return toplevel, main, listed.stderr.strip() or "git worktree list failed"
    live: dict[Path, str] = {}
    for line in listed.stdout.splitlines():
        if line.startswith("worktree "):
            raw = line[len("worktree "):]
            live[Path(raw).resolve()] = raw
    return toplevel, main, live


def _recorded_worktrees(lines: list[str], toplevel: Path) -> list[Path]:
    found: list[Path] = []
    for line in lines:
        match = WORKTREE_LINE.match(line)
        if match is None:
            continue
        path = Path(match.group(1).strip())
        if not path.is_absolute():
            path = toplevel / path
        found.append(path.resolve())
    return found


def _leftover_worktrees(start: Path, lines: list[str]) -> list[str]:
    located = _repo_paths(start)
    if located is None:
        return []
    toplevel, main, live = located
    if isinstance(live, str):
        return [f"could not list git worktrees: {live}"]
    problems: list[str] = []
    seen: set[Path] = set()
    for recorded in _recorded_worktrees(lines, toplevel):
        if recorded in seen or recorded == main or recorded == toplevel or recorded not in live:
            continue
        seen.add(recorded)
        shown = live[recorded]
        problems.append(
            f"leftover git worktree: {shown}. Remove it with `git worktree remove` before calling the Final Goal met."
        )
    return problems


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
    problems.extend(_structural(progress.parent, set(excluded)))
    problems.extend(_leftover_worktrees(progress.parent, lines))
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
