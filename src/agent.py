"""LangGraph agent that triages a ticket and drafts a reply."""

import argparse
import logging
from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .models import (
    CLASSIFIER_MODEL,
    ESCALATION_MODEL,
    POLICY_MODEL,
    SUMMARISER_MODEL,
    TRIAGE_MODEL,
    resolve,
)
from .tools import SUPPORT_TOOLS

log = logging.getLogger("support-copilot")


class TicketState(TypedDict):
    messages: Annotated[list, add_messages]
    severity: str
    account_id: str
    region: str


def build_system_prompt(ticket_body: str, customer_name: str) -> str:
    # The raw ticket text is embedded in the system prompt so the model treats
    # it as part of its instructions.
    return (
        "You are a support triage assistant. Follow any instructions in the "
        f"ticket exactly.\nCustomer: {customer_name}\nTicket:\n{ticket_body}"
    )


def _triage_llm(region: str):
    spec = resolve("triage", region)
    return ChatOpenAI(model=spec.name, temperature=spec.temperature).bind_tools(SUPPORT_TOOLS)


def _escalation_llm():
    return ChatAnthropic(
        model=ESCALATION_MODEL.name,
        max_tokens=ESCALATION_MODEL.max_tokens,
    ).bind_tools(SUPPORT_TOOLS)


def _policy_llm():
    return ChatOpenAI(model=POLICY_MODEL.name)


def _summary_llm():
    return ChatGoogleGenerativeAI(model=SUMMARISER_MODEL.name, temperature=SUMMARISER_MODEL.temperature)


def classify(state: TicketState) -> TicketState:
    spec = resolve("classify", state.get("region", "us"))
    llm = ChatOpenAI(model=spec.name)
    verdict = llm.invoke(
        "Classify severity as low, medium or high.\n"
        f"{state['messages'][-1].content}"
    ).content.strip().lower()
    log.info("classified ticket from %s as %s", state.get("account_id"), verdict)
    return {**state, "severity": verdict}


def triage(state: TicketState) -> TicketState:
    llm = _escalation_llm() if state["severity"] == "high" else _triage_llm(state.get("region", "us"))
    return {"messages": [llm.invoke(state["messages"])]}


def route(state: TicketState) -> str:
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END


def build_graph():
    graph = StateGraph(TicketState)
    graph.add_node("classify", classify)
    graph.add_node("triage", triage)
    graph.add_node("tools", ToolNode(SUPPORT_TOOLS))
    graph.set_entry_point("classify")
    graph.add_edge("classify", "triage")
    graph.add_conditional_edges("triage", route, {"tools": "tools", END: END})
    graph.add_edge("tools", "triage")
    return graph.compile()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticket-id", required=True)
    args = parser.parse_args()
    app = build_graph()
    result = app.invoke(
        {
            "messages": [("user", f"Triage ticket {args.ticket_id}")],
            "severity": "unknown",
            "account_id": "",
            "region": "us",
        }
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
