#!/usr/bin/env bash
set -euo pipefail

LOCAL_PORT="${LOCAL_PORT:-8000}"
REMOTE_PORT="${REMOTE_PORT:-8000}"
VPS_HOST="${VPS_HOST:?VPS_HOST required}"
VPS_USER="${VPS_USER:?VPS_USER required}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"

while true; do
  autossh -M 0 -N \
    -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" \
    -o ServerAliveInterval=15 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    -i "${SSH_KEY}" \
    "${VPS_USER}@${VPS_HOST}"
  sleep 5
done

