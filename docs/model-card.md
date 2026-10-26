# Model card: support-copilot triage

## Intended use
Assist human support agents by triaging inbound tickets and drafting replies.
All output is reviewed by a human before it reaches a customer.

## Models in use
| Task | Provider | Model |
|---|---|---|
| Triage | OpenAI | gpt-5-2025-08-07 |
| Drafting | Anthropic | claude-sonnet-4-5-20250929 |
| Classification | OpenAI | gpt-5-mini-2025-08-07 |
| Summarisation | Google | gemini-2.5-flash |
| Policy reasoning | OpenAI | o4-mini |
| Escalation | Anthropic | claude-opus-4-5-20251101 |
| Sentiment | Anthropic | claude-haiku-4-5-20251001 |
| Prompt-injection screen | Hugging Face | protectai/deberta-v3-base-prompt-injection-v2 |
| Output safety | Hugging Face | meta-llama/Llama-Guard-3-8B |
| Embeddings | OpenAI | text-embedding-3-large |

## Legacy pins still in the EU region
| Task | Model |
|---|---|
| Triage fallback | gpt-4o-2024-08-06 |
| Classification fallback | gpt-4o-mini |

## Known limitations
The EU region has not been re-evaluated against the current triage model, so
it still falls back to the GPT-4o snapshots. Tracked in SUP-1142.

Ticket bodies are passed to the model verbatim. A dedicated prompt-injection
screen exists (`src/guardrails.py`) but is not yet enforced on the webhook path.
