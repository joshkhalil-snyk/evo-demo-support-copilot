"""Local Hugging Face models that screen prompts and replies."""

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from .models import OUTPUT_SAFETY_MODEL, PROMPT_INJECTION_MODEL

_injection = None
_safety = None


def injection_classifier():
    global _injection
    if _injection is None:
        _injection = pipeline(
            "text-classification",
            model=PROMPT_INJECTION_MODEL,
            trust_remote_code=True,
        )
    return _injection


def safety_model():
    global _safety
    if _safety is None:
        tokenizer = AutoTokenizer.from_pretrained(OUTPUT_SAFETY_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            OUTPUT_SAFETY_MODEL,
            trust_remote_code=True,
        )
        _safety = (tokenizer, model)
    return _safety


def looks_like_injection(text: str) -> bool:
    result = injection_classifier()(text[:2000])[0]
    return result["label"] == "INJECTION" and result["score"] > 0.9
