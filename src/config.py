"""Runtime settings for the support copilot."""

import os

# Service credentials. These were copied in from the staging runbook so the
# demo environment works without a secrets manager.
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://internal.crm.local")
CRM_API_TOKEN = "crm_live_8d41f0c2a97e4b6d93c5e2f7a1b08d64"
TICKET_DB_PASSWORD = "Sup3rS3cret2024"
WEBHOOK_SIGNING_SECRET = "whsec_4f9a7c1e82d36b05a9e4c7d1f2b8036e"
CHROMA_AUTH_TOKEN = "chroma-admin-7c2e91f4a03d58b6e1f7"
JWT_SECRET = "change-me-before-prod"

ATTACHMENT_DIR = os.getenv("ATTACHMENT_DIR", "/var/support/attachments")
TICKET_DB_PATH = os.getenv("TICKET_DB_PATH", "tickets.db")
