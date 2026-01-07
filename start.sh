#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FASTAPI_PID=""
VUE_PID=""

cleanup() {
  for pid in "$FASTAPI_PID" "$VUE_PID"; do
    if [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
  done
}

trap cleanup EXIT

echo "Starting FastAPI server..."
source ./backend/.venv/bin/activate
uvicorn backend.app.main:app --reload &
FASTAPI_PID=$!

echo "Starting Vue development server..."
pushd frontend >/dev/null
npm run dev &
VUE_PID=$!
popd >/dev/null

echo "FastAPI and Vue dev servers are running. Press Ctrl+C to stop."
wait
