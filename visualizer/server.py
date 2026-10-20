#!/usr/bin/env python3
"""Agentic SDD Kanban Visualizer.

Reads Spec Kit artifacts from a project root and serves a Kanban board.
Works when the skill lives outside the project (shared ~/.agents/skills install).

Usage:
  python server.py --project /path/to/repo
  python server.py                 # uses cwd if it looks like a Spec Kit project
  AGENTIC_SDD_PROJECT=/path/to/repo python server.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

PORT_DEFAULT = 8765
VISUALIZER_DIR = Path(__file__).resolve().parent


def looks_like_project(root: Path) -> bool:
    return (root / ".specify").is_dir() or (root / "specs").is_dir() or (
        root / "progress.md"
    ).is_file()


def resolve_project_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
    elif os.environ.get("AGENTIC_SDD_PROJECT"):
        root = Path(os.environ["AGENTIC_SDD_PROJECT"]).expanduser().resolve()
    else:
        root = Path.cwd().resolve()

    if not root.is_dir():
        raise SystemExit(f"Project root is not a directory: {root}")
    if not looks_like_project(root):
        print(
            f"Warning: {root} has no .specify/, specs/, or progress.md — board may be empty",
            file=sys.stderr,
        )
    return root


def spec_roots(project: Path) -> list[Path]:
    roots: list[Path] = []
    for candidate in (project / "specs", project / ".specify" / "specs"):
        if candidate.is_dir():
            roots.append(candidate)
    return roots


def parse_spec(spec_path: Path, project: Path) -> dict:
    text = spec_path.read_text(encoding="utf-8", errors="ignore")
    title = spec_path.parent.name
    goal = ""
    acs: list[str] = []
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        if re.match(r"^\d+\.", line):
            acs.append(line.strip())
    m = re.search(r"## Goal\s*\n(.*?)(?=\n##|\Z)", text, re.S)
    if m:
        goal = m.group(1).strip().split("\n")[0][:140]

    status = "specified"
    tasks_path = spec_path.parent / "tasks.md"
    if tasks_path.exists():
        tasks = tasks_path.read_text(encoding="utf-8", errors="ignore")
        checked = tasks.count("- [x]") + tasks.count("- [X]")
        unchecked = tasks.count("- [ ]")
        if checked > 0:
            status = "in_progress"
        if unchecked == 0 and checked > 0:
            status = "done"

    return {
        "id": spec_path.parent.name,
        "title": title,
        "goal": goal,
        "acs": acs[:6],
        "status": status,
        "path": str(spec_path.relative_to(project)),
        "type": "feature",
    }


def parse_bug(bug_dir: Path, project: Path) -> dict:
    slug = bug_dir.name
    assessment = (
        (bug_dir / "assessment.md").read_text(encoding="utf-8", errors="ignore")
        if (bug_dir / "assessment.md").exists()
        else ""
    )
    fix = (
        (bug_dir / "fix.md").read_text(encoding="utf-8", errors="ignore")
        if (bug_dir / "fix.md").exists()
        else ""
    )
    test = (
        (bug_dir / "test.md").read_text(encoding="utf-8", errors="ignore")
        if (bug_dir / "test.md").exists()
        else ""
    )

    status = "assessed"
    if "applied" in fix.lower() or "**Status**: applied" in fix:
        status = "fixed"
    if "verified" in test.lower():
        status = "verified"
    elif "failed" in test.lower():
        status = "failed"

    symptom = ""
    m = re.search(r"\*\*Symptom\*\*:\s*(.*)", assessment)
    if m:
        symptom = m.group(1).strip()[:120]

    return {
        "id": slug,
        "title": f"Bug: {slug}",
        "goal": symptom or "Bug fix",
        "status": status,
        "path": str(bug_dir.relative_to(project)),
        "type": "bug",
    }


def collect_data(project: Path) -> dict:
    items: list[dict] = []
    for specs_dir in spec_roots(project):
        for spec in specs_dir.glob("*/spec.md"):
            if spec.parent.name in {"000-overview", "overview"}:
                continue
            try:
                items.append(parse_spec(spec, project))
            except OSError:
                continue

    bugs_dir = project / ".specify" / "bugs"
    if bugs_dir.is_dir():
        for bug in sorted(bugs_dir.iterdir()):
            if bug.is_dir():
                try:
                    items.append(parse_bug(bug, project))
                except OSError:
                    continue

    overall = ""
    prog = project / "progress.md"
    if prog.exists():
        text = prog.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"## Overall\s*\n(.*)", text)
        if m:
            overall = m.group(1).strip()[:200]

    return {"items": items, "overall": overall, "project": str(project)}


def make_handler(project: Path):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(VISUALIZER_DIR), **kwargs)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/board":
                data = collect_data(project)
                payload = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if parsed.path in {"/", "/index.html"}:
                self.path = "/index.html"
            return super().do_GET()

        def log_message(self, format, *args):
            return

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic SDD Kanban visualizer")
    parser.add_argument(
        "--project",
        "-p",
        help="Project root containing .specify/ and/or specs/",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("AGENTIC_SDD_KANBAN_PORT", PORT_DEFAULT)),
    )
    parser.add_argument(
        "--bind",
        default="127.0.0.1",
        help="Bind address (default 127.0.0.1)",
    )
    args = parser.parse_args()
    project = resolve_project_root(args.project)

    handler = make_handler(project)
    server = HTTPServer((args.bind, args.port), handler)
    print(f"Agentic SDD Kanban at http://{args.bind}:{args.port}")
    print(f"Reading project from: {project}")
    print(f"UI assets from: {VISUALIZER_DIR}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    main()
