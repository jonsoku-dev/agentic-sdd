---
description: Main vs light model roles for Spec Kit Agentic SDD; token overuse causes and fixes.
---

# Main Model Setting Guide

The **parent** model is the user's choice. This guide covers child routing and
common token waste. The pstack sheet and skill defaults decide concrete slugs — see
[model-routing.md](model-routing.md).

## Role of the main (parent) model

Use a capable parent for Spec Kit coordination:

| Host family | Strong parent defaults (when available) | Cost-conscious |
|-------------|------------------------------------------|----------------|
| Claude | Opus-class | Sonnet-class |
| OpenAI | Sol-class | — |
| xAI / Grok | Grok 4.7+ | — |
| Gemini | Argon-class | — |

Do not set Astra or Terra as the default parent on this machine's GPT-6 policy
unless the user explicitly overrides.

## Light models are for leaves

The parent runs each phase in one loop by default
([single-loop-default.md](single-loop-default.md)). When a `bloat`, `parallel`,
or `conflict` trigger justifies a leaf, Haiku-class, Luna-class,
Composer/Spark-class, etc. fit **sub-tasks**:

- Classification, extraction, summarization
- Mechanical edits inside an admitted task
- High-volume repetitive work

They are not the Spec Kit orchestrator for multi-phase delivery.

## Why the main model consumes too many tokens

1. Reloading this entire skill + all references every turn.
2. Parent paging large reads or logs through its own context instead of
   sending them to a disposable leaf (`bloat`) — or the reverse: spawning
   leaves for packets that fit the parent, then re-reading their summaries and
   losing context at every handoff.
3. Full verification after every micro-edit mid-implement.
4. Uncompacted history; `progress.md` not used as resume surface.
5. Thorough/multi-perspective review on low-risk features.
6. Giant specs that must be re-read constantly.

## Practical fixes

- Keep the active prompt short: Final Goal, phase, hard boundaries, pointer to
  `progress.md` + current feature paths.
- Load references conditionally (see INDEX.md).
- Keep packets that fit the parent inline; delegate bulk reads, parallel
  packets, and independent review. The parent keeps phase ownership and
  integration either way.
- Intermediate checks stay narrow; full evidence at converge / bug test.
- After each Spec Kit stage: update artifacts → update `progress.md` → compact
  if the host supports it.
- Prefer splitting oversized features over expanding one giant `spec.md`.
