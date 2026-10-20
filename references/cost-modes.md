---
description: Cost modes for Spec Kit Agentic SDD. Balanced/Thorough stay Spec Kit; Economy only narrows verification and model spend.
---

# Cost Modes

Spec Kit phase ownership does **not** change by cost mode. Modes adjust model
spend, verification breadth, and compaction aggressiveness — not whether
`specify → plan → tasks → implement → converge → REA closeout` applies.
Converged is not finish; only REA `pass` or `not-applicable` finishes.

| Mode | When | Behavior |
|------|------|----------|
| **Economy** | High volume, low risk, explicit budget | Prefer light child models for mechanical leaves; compact early; keep Spec Kit artifacts but narrow intermediate checks |
| **Balanced** | Default | Full Spec Kit core flow; repository checks + narrowest extra proof; pstack-sheet routing at phase/recovery boundaries |
| **Thorough** | High-risk or user asks for high confidence | Full Spec Kit + clarify/analyze/checklist as needed; multi-perspective review at converge; deeper evidence classes |

## Defaults

- Start in **Balanced**.
- Escalate to Thorough for auth, payment, personal data, public API, schema,
  production config, or irreversible multi-module work.
- Economy never skips phase ownership or relaxes acceptance to save tokens.
- Light-path (no full Spec Kit) remains a separate opt-in for trivial work only
  — it is not Economy mode.

## Interaction with pstack panels

See the "Panel size by cost mode" table in `pstack-integration.md`: Economy
runs a 2-reviewer interrogate and skips `architect` on single-file specs;
Thorough keeps the full panel and adds `thermos` where present.

## Interaction with routing

- Economy: bias leaves toward the worker/light model when evidence allows.
- Balanced: use the sheet/default order from `model-routing.md`.
- Thorough: allow escalate-class models when budget remains; still require evidence.
