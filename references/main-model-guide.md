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

Haiku-class, Luna-class, Composer/Spark-class, etc. are for **sub-tasks**:

- Classification, extraction, summarization
- Mechanical edits inside an admitted task
- High-volume repetitive work

They are not the Spec Kit orchestrator for multi-phase delivery.

## Why the main model consumes too many tokens

1. Reloading this entire skill + all references every turn.
2. Parent doing mechanical work instead of delegating leaves.
3. Full verification after every micro-edit mid-implement.
4. Uncompacted history; `progress.md` not used as resume surface.
5. Thorough/multi-perspective review on low-risk features.
6. Giant specs that must be re-read constantly.

## Practical fixes

- Keep the active prompt short: Final Goal, phase, hard boundaries, pointer to
  `progress.md` + current feature paths.
- Load references conditionally (see INDEX.md).
- Delegate mechanical leaves; keep parent on phase ownership and integration.
- Intermediate checks stay narrow; full evidence at converge / bug test.
- After each Spec Kit stage: update artifacts → update `progress.md` → compact
  if the host supports it.
- Prefer splitting oversized features over expanding one giant `spec.md`.
