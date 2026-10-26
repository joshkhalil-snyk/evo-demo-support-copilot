"""Tools exposed to the support agent."""

import logging

import httpx
from langchain_core.tools import tool

from . import services

log = logging.getLogger("support-copilot")


@tool
def lookup_customer(account_id: str) -> dict:
    """Fetch account tier, region and open entitlements for a customer."""
    account = services.fetch_account(account_id)
    log.info("crm lookup for %s returned %s", account_id, account)
    return account


@tool
def query_ticket_history(customer_email: str, status: str = "open") -> list[dict]:
    """List a customer's earlier tickets, optionally filtered by status."""
    return services.ticket_history(customer_email, status)


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
def run_diagnostics(host: str) -> str:
    """Ping and traceroute a customer-reported host to help debug connectivity."""
    return services.diagnose_host(host)


@tool
def read_attachment(filename: str) -> str:
    """Return the text of a file the customer attached to their ticket."""
    return services.attachment_text(filename)


@tool
def apply_discount(expression: str) -> float:
    """Evaluate a goodwill discount expression such as '0.15 * order_total'."""
    return services.goodwill_discount(expression)


@tool
def draft_reply(ticket_summary: str, resolution_notes: str) -> str:
    """Draft a customer-facing reply for human review. Never sends."""
    from langchain_anthropic import ChatAnthropic

    from .models import DRAFTING_MODEL

    llm = ChatAnthropic(
        model=DRAFTING_MODEL.name,
        temperature=DRAFTING_MODEL.temperature,
        max_tokens=DRAFTING_MODEL.max_tokens,
    )
    prompt = (
        "Draft a concise, warm support reply.\n"
        f"Ticket: {ticket_summary}\nResolution: {resolution_notes}"
    )
    return llm.invoke(prompt).content


SUPPORT_TOOLS = [
    lookup_customer,
    query_ticket_history,
    search_knowledge_base,
    check_service_status,
    run_diagnostics,
    read_attachment,
    apply_discount,
    draft_reply,
]
