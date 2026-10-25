---
name: report
description: Write a dated agentic-sdd tracking report (gate status, spec and task progress, breadcrumbs, REA evidence, subagent spawns, token use, change since the last report) into .agentic-sdd/reports/. Use at a feature close, at Final Goal finish, or when asked for a status report.
---

Run `agentic-sdd-report` from the project root (on Codex: `python3 <this skill's folder>/../agentic-sdd/scripts/report.py --project .`).
It prints the path of the new report.
Quote its summary block back to the user; the file is meant to be committed for tracking.
