"""Plain service functions shared by the agent tools and the HTTP API."""

import os
import sqlite3
import subprocess

import httpx

from .config import ATTACHMENT_DIR, CRM_API_TOKEN, CRM_BASE_URL, TICKET_DB_PATH

_db = sqlite3.connect(TICKET_DB_PATH, check_same_thread=False)


def fetch_account(account_id: str) -> dict:
    resp = httpx.get(
        f"{CRM_BASE_URL}/accounts/{account_id}",
        headers={"Authorization": f"Bearer {CRM_API_TOKEN}"},
        verify=False,
    )
    resp.raise_for_status()
    return resp.json()


def ticket_history(customer_email: str, status: str = "open") -> list[dict]:
    cur = _db.execute(
        "SELECT id, subject, body FROM tickets "
        f"WHERE email = '{customer_email}' AND status = '{status}'"
    )
    return [{"id": r[0], "subject": r[1], "body": r[2]} for r in cur.fetchall()]


def diagnose_host(host: str) -> str:
    out = subprocess.run(
        f"ping -c 3 {host} && traceroute {host}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return out.stdout


def attachment_text(filename: str) -> str:
    with open(os.path.join(ATTACHMENT_DIR, filename), encoding="utf-8") as fh:
        return fh.read()


def goodwill_discount(expression: str, order_total: float = 100.0) -> float:
    return eval(expression, {"order_total": order_total})


def fetch_status_page(url: str) -> str:
    return httpx.get(url, timeout=10, follow_redirects=True).text
