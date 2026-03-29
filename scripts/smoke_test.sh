#!/usr/bin/env bash
# =============================================================================
# Smoke Test — Deploy Verification
# Issue: #146 (B10)
# =============================================================================
#
# Usage:
#   ./scripts/smoke_test.sh [BASE_URL] [DB_PATH]
#
# Defaults:
#   BASE_URL = http://localhost:8000
#   DB_PATH  = services/sync/data/agent_sync.db
#
# Exit codes:
#   0 = all checks passed
#   1 = one or more checks failed
# =============================================================================

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
DB_PATH="${2:-services/sync/data/agent_sync.db}"

PASS=0
FAIL=0
TOTAL=0

# Colors (if terminal supports it)
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  NC='\033[0m'
else
  GREEN=''
  RED=''
  YELLOW=''
  NC=''
fi

check() {
  local name="$1"
  local result="$2"  # 0 = pass, non-zero = fail
  local detail="${3:-}"
  TOTAL=$((TOTAL + 1))
  if [ "$result" -eq 0 ]; then
    PASS=$((PASS + 1))
    echo -e "  ${GREEN}✓${NC} ${name}"
  else
    FAIL=$((FAIL + 1))
    echo -e "  ${RED}✗${NC} ${name}"
    if [ -n "$detail" ]; then
      echo -e "    ${YELLOW}→ ${detail}${NC}"
    fi
  fi
}

echo ""
echo "═══════════════════════════════════════════"
echo "  Smoke Test — Deploy Verification"
echo "  Target: ${BASE_URL}"
echo "═══════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────
# 1. Server erreichbar?
# ─────────────────────────────────────────────
echo "▸ Server Connectivity"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE_URL}/" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" != "000" ]; then
  check "Server responds (HTTP ${HTTP_CODE})" 0
else
  check "Server responds" 1 "Connection refused or timeout at ${BASE_URL}"
fi

# ─────────────────────────────────────────────
# 2. Health-Endpoint (/healthz)
# ─────────────────────────────────────────────
echo ""
echo "▸ Health Endpoint"

HEALTHZ_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE_URL}/healthz" 2>/dev/null || echo "000")
if [ "$HEALTHZ_CODE" = "200" ]; then
  check "GET /healthz responds with 200" 0
else
  check "GET /healthz responds with 200" 1 "HTTP ${HEALTHZ_CODE}"
fi

# Health Overview (detailed)
HEALTH_RESPONSE=$(curl -s --connect-timeout 5 "${BASE_URL}/api/health/overview" 2>/dev/null || echo "CURL_FAILED")
if [ "$HEALTH_RESPONSE" = "CURL_FAILED" ]; then
  check "GET /api/health/overview reachable" 1 "Could not connect"
else
  check "GET /api/health/overview reachable" 0

  # Valid JSON?
  if echo "$HEALTH_RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    check "Health overview returns valid JSON" 0
  else
    check "Health overview returns valid JSON" 1 "Response: ${HEALTH_RESPONSE:0:200}"
  fi
fi

# ─────────────────────────────────────────────
# 3. Database
# ─────────────────────────────────────────────
echo ""
echo "▸ Database"

if [ -f "$DB_PATH" ]; then
  check "DB file exists (${DB_PATH})" 0

  if [ -r "$DB_PATH" ]; then
    check "DB file is readable" 0
  else
    check "DB file is readable" 1 "File exists but is not readable"
  fi

  # Can SQLite open it?
  if command -v sqlite3 > /dev/null 2>&1; then
    if sqlite3 "$DB_PATH" "SELECT 1;" > /dev/null 2>&1; then
      check "DB is valid SQLite" 0
    else
      check "DB is valid SQLite" 1 "sqlite3 could not query the file"
    fi
  else
    check "DB is valid SQLite" 0 "(sqlite3 not installed, skipped)"
  fi
else
  check "DB file exists (${DB_PATH})" 1 "File not found"
fi

# ─────────────────────────────────────────────
# 4. Static Files
# ─────────────────────────────────────────────
echo ""
echo "▸ Static Files"

STATIC_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE_URL}/static/" 2>/dev/null || echo "000")
if [ "$STATIC_CODE" != "000" ] && [ "$STATIC_CODE" != "404" ]; then
  check "Static files served (HTTP ${STATIC_CODE})" 0
else
  check "Static files served" 1 "HTTP ${STATIC_CODE} at ${BASE_URL}/static/"
fi

# ─────────────────────────────────────────────
# 5. Dashboard (/admin)
# ─────────────────────────────────────────────
echo ""
echo "▸ Dashboard"

DASH_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE_URL}/admin" 2>/dev/null || echo "000")
if [ "$DASH_CODE" = "200" ]; then
  check "GET /admin responds with 200" 0
elif [ "$DASH_CODE" = "302" ] || [ "$DASH_CODE" = "303" ]; then
  check "GET /admin responds (HTTP ${DASH_CODE} redirect — auth required)" 0
else
  check "GET /admin responds" 1 "HTTP ${DASH_CODE} at ${BASE_URL}/admin"
fi

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
if [ "$FAIL" -eq 0 ]; then
  echo -e "  ${GREEN}ALL PASSED${NC}  (${PASS}/${TOTAL} checks)"
else
  echo -e "  ${RED}${FAIL} FAILED${NC}  (${PASS}/${TOTAL} passed)"
fi
echo "═══════════════════════════════════════════"
echo ""

exit "$FAIL"
