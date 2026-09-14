"""Tools exposed to the support agent."""

import httpx
from langchain_core.tools import tool


@tool
def lookup_customer(account_id: str) -> dict:
    """Fetch account tier, region and open entitlements for a customer."""
    resp = httpx.get(f"https://internal.crm.local/accounts/{account_id}")
    resp.raise_for_status()
    return resp.json()


@tool
def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    """Search prior resolved tickets and published runbooks."""
    from .rag import retriever

    docs = retriever().invoke(query)
    return [{"source": d.metadata.get("source"), "text": d.page_content} for d in docs[:limit]]


@tool
def check_service_status(component: str) -> str:
    """Return the current status of an internal service component."""
    resp = httpx.get("https://status.internal.local/api/components")
    for item in resp.json().get("components", []):
        if item["name"] == component:
            return item["status"]
    return "unknown"


@tool
def draft_reply(ticket_summary: str, resolution_notes: str) -> str:
    """Draft a customer-facing reply for human review. Never sends."""
    from langchain_openai import ChatOpenAI
    from .models import DRAFTING_MODEL

    llm = ChatOpenAI(model=DRAFTING_MODEL.name, temperature=DRAFTING_MODEL.temperature)
    prompt = (
        "Draft a concise, warm support reply.\n"
        f"Ticket: {ticket_summary}\nResolution: {resolution_notes}"
    )
    return llm.invoke(prompt).content


SUPPORT_TOOLS = [
    lookup_customer,
    search_knowledge_base,
    check_service_status,
    draft_reply,
]
