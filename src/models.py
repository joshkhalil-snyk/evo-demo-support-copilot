"""Central model registry.

Model selection is per-task. This has grown organically as teams added their
own routes, which is why several GPT-4o snapshots are pinned at once.
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
TRIAGE_MODEL = ModelSpec("openai", "gpt-4o-2024-08-06", 2048, 0.0)

# Drafting was tuned against the May snapshot and has not been re-validated
# against 08-06 yet. See SUP-1142.
DRAFTING_MODEL = ModelSpec("openai", "gpt-4o-2024-05-13", 4096, 0.4)

# Cheap classification pass that runs on every inbound ticket.
CLASSIFIER_MODEL = ModelSpec("openai", "gpt-4o-mini", 512, 0.0)

# Long-context summarisation of ticket history.
SUMMARISER_MODEL = ModelSpec("openai", "gpt-4-turbo", 8192, 0.2)

# Escalation path for tickets flagged high severity.
ESCALATION_MODEL = ModelSpec("anthropic", "claude-sonnet-4-5", 8192, 0.1)

# Fast pass for sentiment tagging on the queue dashboard.
SENTIMENT_MODEL = ModelSpec("anthropic", "claude-3-5-haiku-20241022", 256, 0.0)

EMBEDDING_MODEL = "text-embedding-3-large"

_BY_TASK = {
    "triage": TRIAGE_MODEL,
    "draft": DRAFTING_MODEL,
    "classify": CLASSIFIER_MODEL,
    "summarise": SUMMARISER_MODEL,
    "escalate": ESCALATION_MODEL,
    "sentiment": SENTIMENT_MODEL,
}


def resolve(task: str) -> ModelSpec:
    return _BY_TASK[task]
