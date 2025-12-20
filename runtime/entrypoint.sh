
#!/usr/bin/env bash

set -euo pipefail

: "${APP_MODULE:=api.server_memory:app}"

: "${PORT:=8000}"

exec uvicorn "${APP_MODULE}" --host 0.0.0.0 --port "${PORT}"

