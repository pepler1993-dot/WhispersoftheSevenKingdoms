#!/bin/bash
# Daily database backup via API
# Add to crontab: 0 */6 * * * /opt/whispers/WhispersoftheSevenKingdoms/scripts/backup-db.sh
set -e

DASHBOARD_URL="${DASHBOARD_URL:-http://localhost:8000}"

response=$(curl -s -X POST "${DASHBOARD_URL}/admin/api/backup")
echo "[$(date -Iseconds)] DB Backup: ${response}"
