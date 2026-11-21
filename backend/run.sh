#!/usr/bin/env bash
# Quick-start the FastAPI backend with uvicorn.
# Usage: ./run.sh [extra uvicorn args]   e.g. ./run.sh --port 9000
set -euo pipefail

cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

exec uv run uvicorn app.main:app --reload --host "$HOST" --port "$PORT" "$@"
