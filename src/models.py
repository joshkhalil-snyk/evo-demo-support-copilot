"""Central model registry.

Model selection is per-task. This has grown organically as teams added their
own routes, which is why a few legacy GPT-4o snapshots are still pinned
alongside the current generation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    name: str
    max_tokens: int
    temperature: float


# Primary reasoning path. Pinned to a dated snapshot so prompt behaviour does
# not drift underneath us between releases.
TRIAGE_MODEL = ModelSpec("openai", "gpt-5-2025-08-07", 4096, 1.0)

# Drafting moved to Claude after the tone evaluation in Q2.
DRAFTING_MODEL = ModelSpec("anthropic", "claude-sonnet-4-5-20250929", 4096, 0.4)

# Cheap classification pass that runs on every inbound ticket.
CLASSIFIER_MODEL = ModelSpec("openai", "gpt-5-mini-2025-08-07", 512, 1.0)

# Long-context summarisation of ticket history.
SUMMARISER_MODEL = ModelSpec("google", "gemini-2.5-flash", 8192, 0.2)

# Refund and entitlement policy reasoning.
POLICY_MODEL = ModelSpec("openai", "o4-mini", 8192, 1.0)

# Escalation path for tickets flagged high severity.
ESCALATION_MODEL = ModelSpec("anthropic", "claude-opus-4-5-20251101", 8192, 0.1)

# Fast pass for sentiment tagging on the queue dashboard.
SENTIMENT_MODEL = ModelSpec("anthropic", "claude-haiku-4-5-20251001", 256, 0.0)

# EU region has not been migrated. See SUP-1142.
LEGACY_TRIAGE_MODEL = ModelSpec("openai", "gpt-4o-2024-08-06", 2048, 0.0)
LEGACY_CLASSIFIER_MODEL = ModelSpec("openai", "gpt-4o-mini", 512, 0.0)

EMBEDDING_MODEL = "text-embedding-3-large"
SELF_HOSTED_EMBEDDING_MODEL = "BAAI/bge-m3"

PROMPT_INJECTION_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"
OUTPUT_SAFETY_MODEL = "meta-llama/Llama-Guard-3-8B"

_BY_TASK = {
    "triage": TRIAGE_MODEL,
    "draft": DRAFTING_MODEL,
    "classify": CLASSIFIER_MODEL,
    "summarise": SUMMARISER_MODEL,
    "policy": POLICY_MODEL,
    "escalate": ESCALATION_MODEL,
    "sentiment": SENTIMENT_MODEL,
}

_LEGACY_BY_TASK = {
    "triage": LEGACY_TRIAGE_MODEL,
    "classify": LEGACY_CLASSIFIER_MODEL,
}


def resolve(task: str, region: str = "us") -> ModelSpec:
    if region == "eu" and task in _LEGACY_BY_TASK:
        return _LEGACY_BY_TASK[task]
    return _BY_TASK[task]
