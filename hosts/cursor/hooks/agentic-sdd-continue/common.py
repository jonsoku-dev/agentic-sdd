#!/usr/bin/env python3
"""Session gate for Cursor agentic-sdd continuation."""

from __future__ import annotations

import json
import os
import re
from contextlib import contextmanager
from pathlib import Path

FOLLOWUP_MARKER = "sdd-continue-followup"
BUDGET = 80
STATUSES = {"running", "delivered", "blocked"}
HARD_STOPS = {"destructive", "secret", "missing_goal", "contradiction", "evidence"}
ASSISTANT_HEAD_LIMIT = 1500

RESUME_EXACT = {
    "계속",
    "계속해",
    "계속해줘",
    "계속 해",
    "계속 진행",
    "계속 진행해",
    "계속 진행해줘",
    "이어서",
    "이어서 해",
    "이어서 해줘",
    "이어서 진행",
    "이어서 진행해",
    "이어서 진행해줘",
    "continue",
    "continue the goal",
    "keep going",
}


def state_dir() -> Path:
    override = os.environ.get("SDD_CONTINUE_STATE_DIR")
    if override:
        return Path(override)
    return Path.home() / ".cursor" / "hooks" / "agentic-sdd-continue" / "sessions"


def safe_id(value: str | None) -> str:
    raw = value or "unknown"
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    return (cleaned[:120] or "unknown")


def conversation_id(payload: dict) -> str:
    return str(payload.get("conversation_id") or payload.get("session_id") or "unknown")


def read_payload() -> dict:
    import sys

    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("hook payload must be an object")
    return data


def session_path(cid: str) -> Path:
    path = state_dir() / (safe_id(cid) + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def empty_session(cid: str) -> dict:
    return {
        "conversation_id": cid,
        "armed": False,
        "hold": False,
        "skip": False,
        "composer_mode": None,
        "is_background_agent": False,
        "followup_count": 0,
        "stuck_fingerprint": None,
        "stuck_repeats": 0,
        "stuck_latched": False,
        "budget_exhausted": False,
        "last_assistant_head": "",
    }


def load_session(cid: str) -> dict:
    path = session_path(cid)
    if not path.exists():
        return empty_session(cid)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return empty_session(cid)
    if not isinstance(data, dict):
        return empty_session(cid)
    base = empty_session(cid)
    base.update(data)
    base["conversation_id"] = cid
    return base


def save_session(cid: str, data: dict) -> None:
    path = session_path(cid)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


@contextmanager
def file_lock(cid: str):
    lock_dir = state_dir() / "lock"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / (safe_id(cid) + ".lock")
    handle = lock_path.open("a+")
    try:
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except ImportError:
            pass
        yield
    finally:
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except ImportError:
            pass
        handle.close()


def normalize_prompt(text: str) -> str:
    collapsed = " ".join((text or "").strip().lower().split())
    return collapsed.strip(" .!?。")


def classify_prompt(session: dict, prompt: str) -> str:
    body = prompt or ""
    if FOLLOWUP_MARKER in body:
        return "followup"
    if "agentic-sdd" in body.lower():
        return "arm"
    if session.get("armed") and normalize_prompt(body) in RESUME_EXACT:
        return "arm"
    return "other"


def apply_prompt(session: dict, prompt: str) -> dict:
    kind = classify_prompt(session, prompt)
    if kind == "followup":
        session["hold"] = False
        return session
    if kind == "arm":
        session["armed"] = True
        session["hold"] = False
        session["followup_count"] = 0
        session["stuck_fingerprint"] = None
        session["stuck_repeats"] = 0
        session["stuck_latched"] = False
        session["budget_exhausted"] = False
        return session
    session["hold"] = True
    return session


def apply_session_start(session: dict, payload: dict) -> dict:
    mode = payload.get("composer_mode")
    background = payload.get("is_background_agent") is True
    session["composer_mode"] = mode
    session["is_background_agent"] = background
    session["skip"] = mode == "ask" or background
    return session


def apply_after_response(session: dict, text: str) -> dict:
    session["last_assistant_head"] = (text or "")[:ASSISTANT_HEAD_LIMIT]
    return session


def parse_marker(text: str | None) -> dict | None:
    body = text or ""
    key = "sdd-continue:"
    idx = body.find(key)
    if idx < 0:
        return None
    rest = body[idx + len(key) :]
    end = rest.find("-->")
    if end < 0:
        return {"invalid": True}
    raw = rest[:end].strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"invalid": True}
    if not isinstance(data, dict):
        return {"invalid": True}
    return data


def progress_record(roots: list) -> dict | None:
    fallback = None
    for root in roots:
        path = Path(str(root)) / "progress.md"
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            mtime_ns = path.stat().st_mtime_ns
        except OSError:
            continue
        marker = parse_marker(text)
        record = {"path": str(path), "mtime_ns": mtime_ns, "marker": marker}
        if marker and not marker.get("invalid") and marker.get("status") in STATUSES:
            return record
        if fallback is None:
            fallback = record
    return fallback


def workspace_roots(payload: dict) -> list:
    roots = payload.get("workspace_roots") or []
    if isinstance(roots, list) and roots:
        return [str(item) for item in roots]
    cwd = payload.get("cwd")
    return [str(cwd)] if cwd else []


def fingerprint(record: dict | None) -> str:
    if record is None:
        return "missing"
    marker = record.get("marker") or {}
    if not isinstance(marker, dict) or marker.get("invalid"):
        action = ""
    else:
        action = str(marker.get("next_action") or "")
    return action + "\n" + str(record.get("mtime_ns"))


def next_action_of(record: dict | None) -> str:
    if not record:
        return ""
    marker = record.get("marker") or {}
    if not isinstance(marker, dict) or marker.get("invalid"):
        return ""
    return str(marker.get("next_action") or "").replace("\n", " ").strip()


def marker_blocks(record: dict | None) -> bool:
    if not record:
        return False
    marker = record.get("marker")
    if not isinstance(marker, dict) or marker.get("invalid"):
        return False
    status = marker.get("status")
    if status in ("delivered", "blocked"):
        return True
    if status != "running":
        return True
    reason = marker.get("stop_reason")
    if reason in HARD_STOPS:
        return True
    if reason not in (None, "null"):
        return True
    return False


def build_followup(count: int, action: str) -> str:
    lines = [
        "<!-- " + FOLLOWUP_MARKER + " -->",
        "This is an automatic Cursor continuation of the same Final Goal, not a new task.",
        "Read progress.md and its sdd-continue line, then do the next_action now.",
        "Do not spend this turn on a status report.",
        "If the line is missing, write it before other work:",
        '<!-- sdd-continue: {"status":"running","stop_reason":null,"next_action":"<one concrete step>"} -->',
        "When the Final Goal is delivered, set status to delivered and stop.",
        "If you must stop for a destructive action, a secret, a missing or contradictory goal, or an evidence or authority boundary, set status to blocked, set stop_reason to destructive, secret, missing_goal, contradiction, or evidence, and ask once.",
    ]
    if action:
        lines.append("next_action: " + action)
    if count >= BUDGET:
        lines.append(
            "This is automatic continuation 80 of 80. "
            "If the Final Goal is still open after this turn, say that the continuation budget is spent, "
            "leave status running, and stop."
        )
    return "\n".join(lines)


def decide_stop(session: dict, payload: dict, record: dict | None) -> str | None:
    if session.get("skip") or session.get("composer_mode") == "ask" or session.get("is_background_agent"):
        return None
    if not session.get("armed") or session.get("hold"):
        return None
    if payload.get("status") != "completed":
        return None
    if session.get("stuck_latched"):
        return None
    if int(session.get("followup_count") or 0) >= BUDGET:
        session["budget_exhausted"] = True
        return None
    if marker_blocks(record):
        return None

    fp = fingerprint(record)
    if fp == session.get("stuck_fingerprint"):
        session["stuck_repeats"] = int(session.get("stuck_repeats") or 0) + 1
    else:
        session["stuck_fingerprint"] = fp
        session["stuck_repeats"] = 1
    if int(session.get("stuck_repeats") or 0) >= 2:
        session["stuck_latched"] = True
        return None

    session["followup_count"] = int(session.get("followup_count") or 0) + 1
    return build_followup(int(session["followup_count"]), next_action_of(record))


def handle_prompt(payload: dict) -> dict:
    cid = conversation_id(payload)
    with file_lock(cid):
        session = load_session(cid)
        apply_prompt(session, str(payload.get("prompt") or ""))
        save_session(cid, session)
    return {"continue": True}


def handle_session_start(payload: dict) -> None:
    cid = conversation_id(payload)
    with file_lock(cid):
        session = load_session(cid)
        apply_session_start(session, payload)
        save_session(cid, session)


def handle_after_response(payload: dict) -> None:
    cid = conversation_id(payload)
    with file_lock(cid):
        session = load_session(cid)
        apply_after_response(session, str(payload.get("text") or ""))
        save_session(cid, session)


def handle_stop(payload: dict) -> str | None:
    cid = conversation_id(payload)
    with file_lock(cid):
        session = load_session(cid)
        record = progress_record(workspace_roots(payload))
        message = decide_stop(session, payload, record)
        save_session(cid, session)
    return message
