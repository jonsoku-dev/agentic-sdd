# Round 3 pre-registration (written before any round-3 run)

Round 2 left four limits: thin n on the sonnet gate claim, one host, one toy
repository, and one "Noop wait" placeholder agent. Round 3 addresses each.

## Changes under test ("main")

1.2.2 plus one text fix: to wait for an agent already in the background, end the
turn; never spawn a placeholder agent. The scorer now classifies placeholder
spawns separately.

## Cells

| Id | Host / parent | Repo / brief | Arms | Runs |
|---|---|---|---|---|
| G | Claude / sonnet | todo / S, L | main | S×2, L×2 (adds to round 2's gate 4 → n = 8) |
| X | Claude / opus, sonnet | kv (Node, multi-module) / K | main | opus×2, sonnet×2 |
| C | Codex / gpt-6-luna | todo / S | 1.2.1 vs main | 2 + 2 |
| CK | Codex / gpt-6-luna | kv / K | main | 1 |

Codex isolation: `HOME` and `CODEX_HOME` are throwaway directories holding only
`auth.json`, pstack 0.9.95, the pstack block of `AGENTS.md`, and the REA MCP
server. A probe confirmed no user skills (no global agentic-sdd, ai-memory,
caveman, ponytail, x20) were visible. Codex runs on a subscription, so cost is
reported as tokens, not dollars.

Cursor (`CURSOR_CONFIG_DIR`) and Grok (`GROK_HOME`) expose config-home
overrides; whether they isolate is probed after this round, not assumed.

## Predictions

1. G: reviewer spawned and both gate lines present in at least 7 of 8 sonnet
   gate runs (round 2 + round 3).
2. X: on the second repository, every main run has column-1 breadcrumbs, both
   gate lines, no `ScheduleWakeup`, no placeholder spawn, and passes at least
   6 of 7 black-box checks.
3. C: Codex main has both gate lines in 2/2 runs; Codex 1.2.1 has them in at
   most 1/2.
4. No cell shows a placeholder ("reply ok") agent under main.

## Judgment rule

The three fixes generalize if predictions 1, 2 and 4 hold. Prediction 3 decides
whether the gate is shown to matter on Codex or only on Claude/sonnet. A failing
prediction is reported, its defect fixed in the skill text, and only the
failing cell rerun.
