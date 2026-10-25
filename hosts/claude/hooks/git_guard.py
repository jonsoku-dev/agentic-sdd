#!/usr/bin/env python3
"""PreToolUse hook (Bash): in an agentic-sdd project, deny the git commands SKILL.md gives no
permission for: push, reset --hard, clean -f, branch -D, stash (except list/show), and checkout /
restore that discard the whole working tree. Commits and ordinary checkouts pass.

Adapted from mattpocock/skills `git-guardrails-claude-code` (MIT), but parsed per git subcommand
instead of substring matching, so `echo "git push"` and `git checkout ./src/a.py` are not blocked.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

SHELLS = {"sh", "bash", "zsh", "dash"}
GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def segments(command: str) -> list[list[str]]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return [command.split()]
    out, cur = [], []
    for t in tokens:
        if t and set(t) <= set(";&|"):
            out.append(cur)
            cur = []
        else:
            cur.append(t)
    return out + [cur]


def git_args(seg: list[str]) -> list[str] | None:
    """Arguments after `git` and its global options, or None when the segment is not git."""
    i = 0
    while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
        i += 1  # leading VAR=value assignments
    if i >= len(seg) or Path(seg[i]).name != "git":
        return None
    i += 1
    while i < len(seg) and seg[i].startswith("-"):
        i += 2 if seg[i] in GIT_VALUE_OPTS else 1
    return seg[i:]


def why_denied(args: list[str]) -> str | None:
    if not args:
        return None
    sub, rest = args[0], args[1:]
    if sub == "push":
        return "git push"
    if sub == "reset" and "--hard" in rest:
        return "git reset --hard"
    if sub == "clean" and any(a == "--force" or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a) for a in rest):
        return "git clean -f"
    if sub == "branch" and any(a in ("-D",) or re.fullmatch(r"-[a-zA-Z]*D[a-zA-Z]*", a) for a in rest):
        return "git branch -D"
    if sub == "stash" and (not rest or rest[0] not in ("list", "show")):
        return "git stash"
    if sub in ("checkout", "restore") and "." in rest and not (sub == "restore" and "--staged" in rest and "--worktree" not in rest):
        return f"git {sub} . (discards the working tree)"
    return None


def scan(command: str, depth: int = 0) -> str | None:
    for seg in segments(command):
        if depth < 2 and len(seg) >= 3 and Path(seg[0]).name in SHELLS and "-c" in seg[1:-1]:
            hit = scan(seg[seg.index("-c") + 1], depth + 1)
            if hit:
                return hit
        args = git_args(seg)
        if args is not None and (hit := why_denied(args)):
            return hit
    return None


def main() -> int:
    data = common.read_input()
    root = common.project_root(data.get("cwd"))
    command = (data.get("tool_input") or {}).get("command", "")
    hit = scan(command) if root is not None and command else None
    if not hit:
        return 0
    common.append(root, {"event": "git_denied", "session": data.get("session_id", ""), "rule": hit})
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (f"agentic-sdd: `{hit}` is outside this skill's authority (no push, merge, "
                                     "reset, stash, or discarding work). Ask the user to run it, or continue "
                                     "without it."),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
