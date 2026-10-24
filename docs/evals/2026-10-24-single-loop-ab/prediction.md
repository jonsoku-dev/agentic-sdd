# Pre-registered prediction (written before any arm ran)

Question: does agentic-sdd 1.2.0 (single loop by default, subagents only on a
`bloat` / `parallel` / `conflict` trigger) beat 1.1.6 (poteto-agent leaf per
implement packet by default) on the same briefs, with nothing else different?

## Isolation

- Each run gets its own copy of one base repository (todo CLI with add/list/done,
  two tests, Spec Kit claude integration, one commit). No shared files between
  runs; no `CLAUDE.md`.
- `claude -p --setting-sources project --strict-mcp-config`: user skills, user
  hooks, user plugins, user memory, and user MCP servers are not loaded. A probe
  run confirmed the global `~/.claude/skills/agentic-sdd` link, caveman,
  ponytail, and ai-memory were all absent.
- Loaded explicitly and identically in both arms: pstack 0.9.94 via
  `--plugin-dir`, the REA MCP server (`rea-agents@6.7.0`) via `--mcp-config`,
  the agentic-sdd skill as project skill `.claude/skills/agentic-sdd` extracted
  with `git archive v1.1.6` or `git archive v1.2.0`. The two trees differ only in
  the files of commit f3702ac plus release metadata.
- Same model (`opus`), same prompt, same turn and dollar caps.

## Briefs

- **S (small):** add `todo edit <id> <text>`; unknown id exits non-zero with a
  stderr message; tests cover both.
- **L (large):** priorities, due dates, `list --sort due|priority`,
  `list --overdue`, migration of old stores, tests; split into small specs when
  tasks exceed ~12.

Two repetitions per cell: 2 briefs × 2 arms × 2 = 8 runs.

## Predictions

1. Subagent spawns (Agent tool calls in the parent transcript) drop in 1.2.0:
   at least 50% fewer implement-leaf spawns on both briefs.
2. Wall time drops in 1.2.0 by at least 20% on S; less certain on L.
3. Cost (`total_cost_usd`, subagents included) drops in 1.2.0 by at least 15%.
4. Black-box acceptance checks: no regression. 1.2.0 passes at least as many as
   1.1.6 in each cell.
5. Review independence is kept: 1.2.0 still spawns at least one reviewer
   (interrogate or equivalent) at converge.
6. 1.2.0 records `inline` or a named trigger in its `pstack: O-poteto` lines.

## Judgment rule

Keep 1.2.0 as is only if predictions 4 and 5 hold (no quality loss, review kept)
and at least one of 2 or 3 holds. If 4 or 5 fails, fix the rule and rerun the
failing cell. If neither 2 nor 3 holds, report that the change bought nothing
measurable on these briefs. n=2 per cell; differences under ~15% are reported as
noise, not wins.
