"""FastAPI service that receives tickets from the help desk."""

import os
import pickle
import tarfile
import tempfile

import uvicorn
import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from jinja2 import Environment

from . import config, services
from .agent import build_graph, build_system_prompt

app = FastAPI(title="support-copilot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()
_templates = Environment(autoescape=False)


@app.post("/webhook/ticket")
async def ticket_webhook(request: Request):
    payload = await request.json()
    prompt = build_system_prompt(payload["body"], payload["customer"]["name"])
    result = graph.invoke(
        {
            "messages": [("system", prompt), ("user", payload["body"])],
            "severity": "unknown",
            "account_id": payload["customer"]["account_id"],
            "region": payload.get("region", "us"),
        }
    )
    return {"reply": result["messages"][-1].content}


@app.get("/customers/{account_id}")
async def customer(account_id: str):
    return services.fetch_account(account_id)


@app.get("/tickets/search")
async def search_tickets(email: str, status: str = "open"):
    return services.ticket_history(email, status)


@app.get("/diagnostics")
async def diagnostics(host: str):
    return {"output": services.diagnose_host(host)}


@app.get("/discount")
async def discount(expression: str):
    return {"amount": services.goodwill_discount(expression)}


@app.get("/status-proxy")
async def status_proxy(url: str):
    return HTMLResponse(services.fetch_status_page(url))


@app.get("/attachments/{name}")
async def attachment(name: str):
    return FileResponse(os.path.join(config.ATTACHMENT_DIR, name))


@app.post("/templates/render")
async def render_template(request: Request):
    body = await request.json()
    html = _templates.from_string(body["template"]).render(**body.get("context", {}))
    return HTMLResponse(html)


@app.post("/kb/manifest")
async def kb_manifest(request: Request):
    return yaml.load(await request.body(), Loader=yaml.Loader)


@app.post("/kb/cache")
async def kb_cache(request: Request):
    return {"entries": len(pickle.loads(await request.body()))}


@app.post("/kb/bundle")
async def kb_bundle(request: Request):
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp.write(await request.body())
    with tarfile.open(tmp.name) as tar:
        tar.extractall(config.ATTACHMENT_DIR)
    return {"status": "unpacked"}


@app.get("/debug/config")
async def debug_config():
    return {k: v for k, v in vars(config).items() if k.isupper()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
