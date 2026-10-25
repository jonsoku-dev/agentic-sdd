---
description: "How to use provider personas and official documentation as tools."
---

# Provider Personas and Official Docs as Tools

## Provider Personas

Load the appropriate persona when the work is provider-specific:

| Provider | Persona File | Preferred Main Model | Light Model |
|----------|--------------|----------------------|-------------|
| Anthropic | `personas/anthropic.md` | Sonnet 5.5 / Opus 5.5 | Haiku 5.5 |
| OpenAI | `personas/openai.md` | GPT-6.1 Sol / GPT-6 Sol | GPT-6 Luna |
| Google | `personas/google.md` | Gemini 4 Argon | — |
| xAI | `personas/xai.md` | Grok 4.7+ | — |

**Excluded**: GPT-6 Astra, any Terra variant.

## Official Docs as Tools

When the task involves a specific provider’s API, model behavior, effort settings, or tooling:

1. Prefer fetching the current official documentation over relying on training data.
2. Use available tools (web fetch, browser, or MCP docs servers if configured).
3. Summarize only the relevant points into `progress.md` or the current spec. Do not leave full doc pages in context.
4. If the documentation cannot be fetched, explicitly note the limitation and fall back to known stable behavior.

### Key Documentation Entry Points

- Anthropic: https://platform.claude.com/docs
- OpenAI: https://developers.openai.com/api/docs
- Google: https://ai.google.dev/docs
- xAI: https://docs.x.ai

## Multi-Agent Usage

When spawning sub-agents:

- Assign the light model (Haiku 5.5 or GPT-6 Luna) for classification, extraction, and simple edits.
- Load the matching provider persona only when the sub-task is provider-specific.
- The main orchestrator should remain on Sonnet 5.5 or Sol unless higher confidence is required.
