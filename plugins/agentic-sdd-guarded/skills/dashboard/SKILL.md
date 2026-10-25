---
name: dashboard
description: Start the local agentic-sdd dashboard (flow, gates, tokens, reports, Kanban) for the current project on 127.0.0.1.
disable-model-invocation: true
---

Run `agentic-sdd-dashboard` from the project root (on Codex: `python3 <this skill's folder>/../agentic-sdd/visualizer/server.py --project .`),
in the background, and give the user the printed URL. It serves only on 127.0.0.1 and only reads files; stop it with Ctrl+C or by killing the process.
