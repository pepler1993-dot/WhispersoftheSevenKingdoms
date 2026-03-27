#!/usr/bin/env bash
set -euo pipefail

# ── Whispers Agent Sync Service – Initial Server Setup ──
#
# Run once on a fresh Debian 12 LXC container:
#   curl -sL <raw-url-to-this-file> | bash
#   -- or --
#   bash /path/to/setup.sh
#
# Prerequisites: Debian 12, git, root access

REPO_URL="https://github.com/pepler1993-dot/WhispersoftheSevenKingdoms.git"
INSTALL_DIR="/opt/whispers/WhispersoftheSevenKingdoms"
SERVICE_NAME="agent-sync"
BRANCH="${1:-main}"

echo "============================================"
echo " Whispers Agent Sync – Server Setup"
echo " Branch: $BRANCH"
echo "============================================"

# 1. System packages
echo "[1/6] Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip git > /dev/null

# 2. Clone repo
if [ -d "$INSTALL_DIR" ]; then
    echo "[2/6] Repo already exists at $INSTALL_DIR, pulling latest..."
    cd "$INSTALL_DIR"
    git fetch --all
    git checkout "$BRANCH"
    git pull
else
    echo "[2/6] Cloning repo..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    git checkout "$BRANCH"
fi

# 3. Python venv + dependencies
echo "[3/6] Setting up Python venv..."
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r services/sync/requirements.txt

# 4. Ensure data directory
echo "[4/6] Ensuring data directory..."
mkdir -p services/sync/data

# 5. Install systemd service
echo "[5/6] Installing systemd service..."
cp services/sync/deploy/agent-sync.service /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

# 6. Reminder
echo "[6/6] Done!"
echo ""
echo "============================================"
echo " NEXT STEPS"
echo "============================================"
echo ""
echo " 1. If migrating from old install, copy DB:"
echo "    cp /old/path/data/agent_sync.db ${INSTALL_DIR}/services/sync/data/"
echo ""
echo " 2. Start the service:"
echo "    systemctl start ${SERVICE_NAME}"
echo "    systemctl status ${SERVICE_NAME}"
echo ""
echo " 3. Check logs:"
echo "    journalctl -u ${SERVICE_NAME} -f"
echo ""
echo " 4. Dashboard: http://localhost:8000/admin"
echo ""
