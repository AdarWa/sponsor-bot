#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FASTAPI_PID=""
AZURE_FUNC_PID=""
VUE_PID=""

cleanup() {
  for pid in "$FASTAPI_PID" "$AZURE_FUNC_PID" "$VUE_PID"; do
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

echo "Starting Azure Functions host..."
pushd api >/dev/null
source ./.venv/bin/activate
func start &
AZURE_FUNC_PID=$!
popd >/dev/null

echo "Starting Vue development server..."
pushd frontend >/dev/null
npm run dev &
VUE_PID=$!
popd >/dev/null

echo "FastAPI, Azure Function, and Vue dev servers are running. Press Ctrl+C to stop."
wait
