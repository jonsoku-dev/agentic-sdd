# Plugin editions pre-registration (written before any plugin run)

Same isolation, briefs, and judge (`perfect.py`, C1–C10) as the perfect bar.
The skill is loaded from the plugin (`--plugin-dir` on Claude, an installed
plugin in a throwaway `CODEX_HOME` on Codex) instead of a project skill copy.
C10 baseline: matrix m3 (the skill copy at fx1).

| Cell | Hook-free `agentic-sdd` | Guarded `agentic-sdd-guarded` |
|---|---|---|
| Claude sonnet, todo S | ×2 | ×2 |
| Claude sonnet, kv K | ×2 | ×2 |
| Claude opus, kv K | ×2 | ×2 |
| Claude opus, todo L | ×2 | ×2 |
| Codex, todo S and kv K | ×2 each | — (Codex does not trust plugin hooks) |

## Predictions

1. Both editions pass C1–C10 in every run.
2. Hook-free costs match m3 within 15% per cell (same text, different loader).
3. Guarded: every Stop-hook block names a real gate problem; no run ends with a
   `gate_released` event (the model fixes the problem within two blocks); the
   ledger records at least one reviewer spawn per run.
4. Guarded costs stay within 15% of hook-free per cell.

## Judgment rule

A failed C-criterion is a defect to fix before release. A guarded run that
needed a block and then passed is the hook doing its job and is reported as
such.
