#!/usr/bin/env bash
# Run the full Sentinel Relay incident workflow against the local app.
#
# Usage:
#   ./agents/run_demo.sh                    # INC-1042 (default)
#   ./agents/run_demo.sh --incident-id INC-1043
#   ./agents/run_demo.sh --skip-aimlapi    # deterministic fallbacks only
#
# The Next.js app must be running first:
#   pnpm --filter sentinel-relay-web dev
#
# After this script finishes, open the War Room and the messages will be live.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${SCRIPT_DIR}/.venv/bin/python3"

if [[ ! -x "${PYTHON}" ]]; then
  echo "ERROR: Python venv not found at ${PYTHON}" >&2
  echo "       Run: cd agents && python3 -m venv .venv && .venv/bin/pip install -e ." >&2
  exit 1
fi

APP_URL="${SENTINEL_RELAY_APP_URL:-http://127.0.0.1:3000}"

echo ""
echo "  Sentinel Relay — live workflow runner"
echo "  App: ${APP_URL}"
echo ""

# Verify the app is reachable before doing anything
if ! curl -sf "${APP_URL}/api/collaboration/health" > /dev/null 2>&1; then
  echo "ERROR: Cannot reach ${APP_URL}" >&2
  echo "       Start the app first: pnpm --filter sentinel-relay-web dev" >&2
  exit 1
fi

# Clear stale agent state files from previous runs
rm -f /tmp/sentinel-relay-worker-*.json 2>/dev/null || true

echo "  Running 18-step incident workflow..."
echo ""

"${PYTHON}" "${ROOT_DIR}/scripts/demo/run-evidence-band-workflow.py" \
  --app-url "${APP_URL}" \
  "$@"

echo ""
echo "  Done. Open the War Room to see the full coordination stream."
echo ""
