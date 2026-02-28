#!/usr/bin/env bash
# dev.sh — start backend + frontend together for local development
#
# Usage:
#   ./dev.sh          # start both
#   ./dev.sh --help   # show this message
#
# Requires: .venv (python), node/npm (frontend)
# Both processes are killed cleanly on Ctrl-C.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
RESET='\033[0m'

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,8p' "$0" | sed 's/^# //'
  exit 0
fi

# --- preflight checks ---

if [[ ! -d "$VENV" ]]; then
  echo -e "${RED}Error:${RESET} .venv not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'"
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo -e "${RED}Error:${RESET} frontend/node_modules not found. Run: cd frontend && npm install"
  exit 1
fi

# --- log helpers ---

log_api() { echo -e "${CYAN}[api]${RESET} $*"; }
log_ui()  { echo -e "${MAGENTA}[ui]${RESET}  $*"; }

# --- prefix output from background process ---
prefix_output() {
  local label="$1"
  local color="$2"
  while IFS= read -r line; do
    echo -e "${color}[${label}]${RESET} ${line}"
  done
}

# --- cleanup ---

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo ""
  echo -e "${BOLD}Shutting down...${RESET}"
  [[ -n "$BACKEND_PID" ]]  && kill "$BACKEND_PID"  2>/dev/null || true
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT INT TERM

# --- start backend ---

log_api "Starting FastAPI on http://localhost:8765"
(
  source "$VENV/bin/activate"
  cd "$SCRIPT_DIR"
  uvicorn wiki_annotate.api:app \
    --reload \
    --reload-dir wiki_annotate \
    --port 8765 \
    --log-level info 2>&1
) | prefix_output "api" "$CYAN" &
BACKEND_PID=$!

# --- start frontend ---

log_ui "Starting Vite dev server on http://localhost:3000"
(
  cd "$FRONTEND_DIR"
  npm start 2>&1
) | prefix_output "ui" "$MAGENTA" &
FRONTEND_PID=$!

# --- summary ---

echo ""
echo -e "  ${CYAN}API${RESET}      → http://localhost:8765"
echo -e "  ${MAGENTA}Frontend${RESET} → http://localhost:3000"
echo -e "  Press ${BOLD}Ctrl-C${RESET} to stop both."
echo ""

wait
