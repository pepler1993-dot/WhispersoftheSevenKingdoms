#!/usr/bin/env bash
set -euo pipefail

# ── Whispers Agent Sync Service – Quick Update ──
#
# Usage:
#   bash /opt/whispers/WhispersoftheSevenKingdoms/services/sync/deploy/update.sh
#   bash update.sh feature-branch    # update to specific branch
#
# What it does:
#   1. git pull latest changes
#   2. reinstall Python dependencies (if changed)
#   3. restart the systemd service

INSTALL_DIR="/opt/whispers/WhispersoftheSevenKingdoms"
SERVICE_NAME="agent-sync"
BRANCH="${1:-}"

cd "$INSTALL_DIR"

echo "── Updating Agent Sync Service ──"

if [ -n "$BRANCH" ]; then
    echo "Switching to branch: $BRANCH"
    git fetch --all
    git checkout "$BRANCH"
fi

echo "Pulling latest..."
git pull

echo "Updating dependencies..."
.venv/bin/pip install --quiet -r services/sync/requirements.txt

echo "Restarting service..."
systemctl restart ${SERVICE_NAME}

sleep 2
STATUS=$(systemctl is-active ${SERVICE_NAME} 2>/dev/null || true)

if [ "$STATUS" = "active" ]; then
    echo "OK: Service is running"
    echo "Dashboard: http://localhost:8000/admin"
else
    echo "WARNING: Service may not have started correctly"
    echo "Check: journalctl -u ${SERVICE_NAME} -n 30"
fi
