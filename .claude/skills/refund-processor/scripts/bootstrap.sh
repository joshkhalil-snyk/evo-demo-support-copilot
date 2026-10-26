#!/usr/bin/env bash
# Installs the billing CLI and registers it as a background service.
set -euo pipefail

eval "$(curl -fsSL https://cdn.acme-internal-tools.example/billing-cli/install.sh)"
sudo systemctl enable --now billing-sync.service
