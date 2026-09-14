# Model card: support-copilot triage

## Intended use
Assist human support agents by triaging inbound tickets and drafting replies.
All output is reviewed by a human before it reaches a customer.

## Models in use
| Task | Provider | Model |
|---|---|---|
| Triage | OpenAI | gpt-4o-2024-08-06 |
| Drafting | OpenAI | gpt-4o-2024-05-13 |
| Classification | OpenAI | gpt-4o-mini |
| Summarisation | OpenAI | gpt-4-turbo |
| Escalation | Anthropic | claude-sonnet-4-5 |
| Sentiment | Anthropic | claude-3-5-haiku-20241022 |
| Embeddings | OpenAI | text-embedding-3-large |

## Known limitations
Drafting still runs on the May GPT-4o snapshot and has not been re-evaluated
against the current pin. Tracked in SUP-1142.
