---
description: Load map for Agentic SDD references. Spec Kit is the default process.
---

# Reference Index

Load only what the current step needs.

## Core (Spec Kit default)

| File | When to load |
|------|--------------|
| `spec-kit-alignment.md` | Project/feature resolution, Spec Kit commands, non-SDD entry |
| `phase-contract.md` | Entering or handing off a phase |
| `harness-layers.md` | Seven harness layers × Spec Kit × pstack × host; readiness via `scripts/harness_probe.py` |
| `pstack-integration.md` | Phase→pstack map, per-host leaf dispatch (Cursor / Claude / Codex / Grok), hook precedence, review gate, full-autonomy grant |
| `poteto-mode-anatomy.md` | How each host reaches pstack poteto-mode (mandate, user-only on Cursor), what the skill does when it runs, port vs Cursor plugin differences |
| `host-guide-greenfield-brownfield.md` | Human+agent guide: greenfield vs brownfield on Claude / Codex / Cursor |
| `verification-execution.md` | Running approved CLI checks / evidence |
| `recovery.md` | Repeated failure, conflicting diagnoses, scope drift |
| `direction-keeper.md` | Before next feature / acceptance review |
| `model-routing.md` | Child model/effort from pstack sheet → defaults → parent; per-host dispatch |
| `starting-tool-considerations.md` | Claude / Codex / Cursor / Grok bootstrap |
| `cursor-continuation.md` | Cursor only: `progress.md` machine line and stop-hook resume |
| `agent-compatibility.md` | Host matrix, missing tools, Grok file-based mode |
| `rea-closeout.md` | Mandatory post-converge REA analysis; install if missing |

## Supporting

| File | When to load |
|------|--------------|
| `bug-workflow.md` | Repair: assess → fix → test |
| `compaction-timing.md` | Before `/compact` or context flush |
| `cost-modes.md` | Economy / Balanced / Thorough (Thorough ≈ full Spec Kit rigor) |
| `main-model-guide.md` | Main vs light model roles; token overuse |
| `anti-oververification.md` | Stopping verify loops mid-implement |
| `anti-patterns.md` | Scope drift, invented requirements, chat-memory reliance |
| `edge-cases-and-failure-modes.md` | Ambiguity, partial failure, blockers |
| `multi-perspective-review.md` | Thorough / high-risk converge review |
| `kanban-board.md` | Optional visual board |
| `provider-personas-and-docs.md` | Provider-specific API work |
| `spec-template.md` / `progress-template.md` / `overview-template.md` | Scaffolding helpers when CLI templates unavailable |

## Personas

| File | When |
|------|------|
| `../personas/anthropic.md` | Anthropic/Claude API–specific work |
| `../personas/openai.md` | OpenAI API–specific work |
| `../personas/google.md` | Google/Gemini API–specific work |
| `../personas/xai.md` | xAI/Grok API–specific work |
