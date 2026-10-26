# Support Copilot

Internal assistant that triages inbound support tickets, retrieves prior
resolutions from the knowledge base, and drafts a suggested reply for a
human agent to approve.

> **Intentionally vulnerable demo application.** Used to demonstrate Evo by
> Snyk. It contains deliberate code flaws, vulnerable dependencies and fake
> credentials. Do not deploy it or reuse any of its code.

## Architecture

- LangGraph state machine orchestrates the classify -> triage -> retrieve -> draft flow
- Primary reasoning runs on GPT-5; escalations route to Claude Opus
- Knowledge base retrieval uses Chroma with OpenAI embeddings
- Local Hugging Face models screen prompts and replies (`src/guardrails.py`)
- Extra capabilities are pulled in over MCP from the internal toolbox server
  and from third-party servers declared in `config/mcp.json`
- A FastAPI webhook (`src/api.py`) receives tickets from the help desk

## Running locally

    pip install -r requirements.txt
    python -m src.agent --ticket-id 12345
    uvicorn src.api:app --port 8080
