# agentic-sdd

Spec Kit–first Spec-Driven Development for **Claude Code, Codex, Cursor, and
Grok Build**, with [pstack](https://github.com/cursor/plugins/tree/main/pstack)
as the execution engine inside every phase and a mandatory REA closeout.

```text
specify → plan → tasks → implement → converge → REA closeout
```

- **Spec Kit** owns the sequence and artifacts (`.specify/`, `specs/`).
- **agentic-sdd** owns the Final Goal, phase contracts, recovery, continuity
  (`progress.md`), and the closeout.
- **pstack** owns *how* a phase executes: `architect` / `arena` at plan,
  poteto non-negotiables and `poteto-agent` leaves at implement,
  `blast-radius` + `interrogate` at converge, `pause-safely` before a handoff.
- **Seven harness layers** (workspace facts, procedure, source access, action
  rules, reviewer evidence, effort, completion goal) are mapped per host in
  [`references/harness-layers.md`](references/harness-layers.md); the split
  follows @beamnxw's harness-engineering post (X, 2026-10-07).

Unattended by default: `/agentic-sdd` advances every phase and remaining
numbered feature without a phase quiz. Hard boundaries (destructive ops,
secrets, scope changes, plugin installs) still ask once.

## Install

```sh
git clone <this repo> ~/.agents/skills/agentic-sdd
~/.agents/skills/agentic-sdd/install.sh            # symlinks into ~/.claude ~/.codex ~/.cursor ~/.grok skills
~/.agents/skills/agentic-sdd/install.sh --project /path/to/repo   # + pstack project playbook (port) and .cursor/rules/agentic-sdd.mdc (Cursor)
~/.agents/skills/agentic-sdd/install.sh --apply-cursor-hooks      # + Cursor stop-hook continuation
~/.agents/skills/agentic-sdd/install.sh --codex-mandate           # pstack mandate into ~/.codex/AGENTS.md (Codex never runs untrusted plugin hooks)
~/.agents/skills/agentic-sdd/install.sh --grok-mandate --grok-agents   # Grok home rule (mandate + Spec Kit handoffs) and poteto-agent link
~/.agents/skills/agentic-sdd/install.sh --cursor-cli-skills       # link the Cursor pstack plugin's skills for the Cursor Agent CLI
```

How each host reaches pstack's `poteto-mode` (and why Cursor needs the rule)
is in `references/poteto-mode-anatomy.md`. Headless drivers used by the evals:
`claude -p --output-format stream-json --verbose --dangerously-skip-permissions`,
`codex exec --json -m <a slug spawn_agent lists> --dangerously-bypass-approvals-and-sandbox "…" < /dev/null`,
`agent -p --output-format stream-json --force "…"`,
`grok --output-format json --always-approve -p "…" < /dev/null`.

Then install pstack once per host:

| Host | pstack | Invoke | Leaves |
|------|--------|--------|--------|
| Claude Code | `claude plugin install pstack --marketplace michael-denyer/pstack-claude --scope user` | `/pstack:<skill>` | `pstack:poteto-agent[-<level>]` |
| Codex | `codex plugin marketplace add michael-denyer/pstack-claude && codex plugin add pstack@pstack-claude` | skill by name | `spawn_agent` + `reasoning_effort` |
| Cursor | `/add-plugin pstack` | `/<skill>` | `poteto-agent` |
| Grok Build | `grok plugin marketplace add michael-denyer/pstack-claude && grok plugin install pstack@pstack-claude --trust` (or Claude compat scan) | skill by name | `spawn_subagent` |

Project Spec Kit setup (`specify init`, integrations, inspect, activate)
belongs to the `setup-speckit-multi-agent` skill, not this one.

Check readiness on any host:

```sh
python3 scripts/harness_probe.py --host claude --project /path/to/repo \
  --check-map references/pstack-integration.md
```

It prints pstack version, missing common-core skills, the model sheet, one
line per harness layer, and the two breadcrumbs to paste into `progress.md`.

## REA closeout

Mandatory after a clean converge. Only in delivery/repair closeout, if MCP and
`rea` are both missing: `npm install -g rea-agents@6.7.0` and
`rea setup --yes --client <cursor|claude_code|codex|grok_build>` (one id). No
`curl|bash`, no `--all-detected`. See `references/rea-closeout.md`.

## Model and effort

The parent model is the user's. Children come from the pstack sheet
(`pstack-models.md` / `.mdc` written by `/setup-pstack`), then pstack skill
defaults, then the parent. No external advisor. See
`references/model-routing.md`.

## Structure

| Path | Role |
|------|------|
| `SKILL.md` | Entrypoint |
| `references/` | Phase contracts, pstack map, harness layers, recovery, hosts, REA |
| `scripts/` | `harness_probe.py`, verification guards, criterion gate, scaffold helpers |
| `templates/playbooks/` | pstack project playbook (`.agents/playbooks/agentic-sdd.md`) |
| `hosts/cursor/` | Cursor continuation hooks + `hooks.json` snippet |
| `visualizer/` | Optional Kanban over Spec Kit artifacts |
| `personas/` | Provider personas (load only when needed) |
| `agents/openai.yaml` | Codex skill metadata |
| `tests/` | `pytest -q tests` |
| `evals/` | Behavioral evals |

## Hosts

Start with `references/host-guide-greenfield-brownfield.md`, then
`references/starting-tool-considerations.md` and
`references/agent-compatibility.md`. Cursor resumes through
`references/cursor-continuation.md`.

## Kanban

```sh
python3 visualizer/server.py --project /path/to/repo   # http://localhost:8765
```

## License and third-party notices

This repository is MIT (`LICENSE`). Everything here is original to this
project; it integrates, but does not bundle, the tools below. Install each
from its own source under its own license.

| Component | Role here | Author / license |
|---|---|---|
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) (Cursor plugin) | execution style inside Spec Kit phases | Lauren Tan (poteto), MIT |
| [pstack-claude](https://github.com/michael-denyer/pstack-claude) (Claude Code / Codex / Grok port) | same, on the other hosts | Michael Denyer, MIT (port of the above) |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | the phase sequence and artifacts | GitHub, MIT |
| [rea-agents](https://github.com/morluto/rea) (REA) | mandatory closeout evidence | morluto, MIT |
| @beamnxw, "Make Opus 5.5 Finish Long Tasks: A Reusable Harness Engineering Setup" (X, 2026-10-07) | the seven-layer model in `references/harness-layers.md` | idea credited; no text reproduced |

`templates/playbooks/agentic-sdd.md` quotes a few words of pstack playbook step
text only as anchors, as the pstack project-playbook format requires. The Cursor
plugin cache path (`~/.cursor/plugins/cache/cursor-public/pstack/<hash>/`)
changes on every plugin update; rerun `install.sh --cursor-cli-skills` after
updating pstack in Cursor so the Agent CLI links resolve again.

Evaluation records under `docs/evals/` are from the maintainers' own runs on
their machine; raw headless transcripts are not committed.
