# Support Copilot

Internal assistant that triages inbound support tickets, retrieves prior
resolutions from the knowledge base, and drafts a suggested reply for a
human agent to approve.

## Architecture

- LangGraph state machine orchestrates the triage -> retrieve -> draft flow
- Primary reasoning runs on GPT-4o; escalations route to Claude Sonnet
- Knowledge base retrieval uses Chroma with OpenAI embeddings
- Extra capabilities are pulled in over MCP from the internal toolbox server

## Running locally

    pip install -r requirements.txt
    python -m src.agent --ticket-id 12345
