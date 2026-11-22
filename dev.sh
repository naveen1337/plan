#!/usr/bin/env bash
# Start backend (FastAPI) and frontend (Vite) side by side in a tmux session.
# Usage:
#   ./dev.sh            create (or reattach to) the session
#   ./dev.sh stop       kill the session
set -euo pipefail

SESSION="${SESSION:-plan}"
ROOT="$(cd "$(dirname "$0")" && pwd)"

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is not installed" >&2
  exit 1
fi

if [[ "${1:-}" == "stop" ]]; then
  tmux kill-session -t "$SESSION" 2>/dev/null && echo "Stopped session '$SESSION'" || echo "No session '$SESSION'"
  exit 0
fi

attach() {
  if [[ -n "${TMUX:-}" ]]; then
    tmux switch-client -t "$SESSION"
  else
    tmux attach-session -t "$SESSION"
  fi
}

# Already running: just attach.
if tmux has-session -t "$SESSION" 2>/dev/null; then
  attach
  exit 0
fi

# Frontend package manager: prefer pnpm (lockfile is pnpm-lock.yaml).
if command -v pnpm >/dev/null 2>&1; then
  FRONTEND_CMD="pnpm dev"
else
  FRONTEND_CMD="npm run dev"
fi

# Use stable pane IDs (%N) instead of indices, which shift after splits.
BACKEND_PANE=$(tmux new-session -d -s "$SESSION" -n dev -c "$ROOT/backend" -P -F '#{pane_id}')
tmux send-keys -t "$BACKEND_PANE" "./run.sh" C-m

FRONTEND_PANE=$(tmux split-window -h -t "$BACKEND_PANE" -c "$ROOT/frontend" -P -F '#{pane_id}')
tmux send-keys -t "$FRONTEND_PANE" "$FRONTEND_CMD" C-m

SHELL_PANE=$(tmux split-window -v -t "$BACKEND_PANE" -c "$ROOT" -P -F '#{pane_id}')

tmux set-option -t "$SESSION" pane-border-status top >/dev/null
tmux select-pane -t "$BACKEND_PANE" -T backend
tmux select-pane -t "$FRONTEND_PANE" -T frontend
tmux select-pane -t "$SHELL_PANE" -T shell
tmux select-layout -t "$SESSION:dev" main-vertical
tmux select-pane -t "$SHELL_PANE"

attach
