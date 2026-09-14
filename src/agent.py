"""LangGraph agent that triages a ticket and drafts a reply."""

import argparse
from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .models import ESCALATION_MODEL, TRIAGE_MODEL, CLASSIFIER_MODEL
from .tools import SUPPORT_TOOLS


class TicketState(TypedDict):
    messages: Annotated[list, add_messages]
    severity: str
    account_id: str


def _triage_llm():
    return ChatOpenAI(
        model=TRIAGE_MODEL.name,
        temperature=TRIAGE_MODEL.temperature,
    ).bind_tools(SUPPORT_TOOLS)


def _escalation_llm():
    return ChatAnthropic(
        model=ESCALATION_MODEL.name,
        max_tokens=ESCALATION_MODEL.max_tokens,
    ).bind_tools(SUPPORT_TOOLS)


def classify(state: TicketState) -> TicketState:
    llm = ChatOpenAI(model=CLASSIFIER_MODEL.name, temperature=0)
    verdict = llm.invoke(
        "Classify severity as low, medium or high.\n"
        f"{state['messages'][-1].content}"
    ).content.strip().lower()
    return {**state, "severity": verdict}


def triage(state: TicketState) -> TicketState:
    llm = _escalation_llm() if state["severity"] == "high" else _triage_llm()
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
        }
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
