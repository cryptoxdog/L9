#!/usr/bin/env bash
# 10X Governance Health Diagnostic
# Version: 1.0.0
# Generated: 2025-10-06T17:25:00Z
# Canonical-Source: 10X Governance Suite

ROOT="/Users/ib-mac/Library/Application Support/Cursor/GlobalCommands"
LOG="$ROOT/ops/logs/tenx_status.log"

function check() {
  local label=$1
  local path=$2
  if [ -f "$path" ] || [ -d "$path" ]; then
    echo "✅  $label — OK"
  else
    echo "❌  $label — Missing"
  fi
}

echo "🩺 10X Governance Suite — Health Diagnostic"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "---------------------------------------------"

check ".cursor brain" "$ROOT/.cursor/rules.json"
check "Environment Layer" "$ROOT/environment"
check "Commands Layer" "$ROOT/commands"
check "OPS Layer" "$ROOT/ops"
check "Security Layer" "$ROOT/security"
check "Pipeline Layer" "$ROOT/pipeline"
check "Intelligence Layer" "$ROOT/intelligence"
check "Integrity Layer" "$ROOT/integrity"
check "Manifest Lock" "$ROOT/integrity/manifest-lock.json"
check "Integrity Activity Log" "$ROOT/ops/logs/integrity_activity.log"

echo "---------------------------------------------"
if grep -q "Verify+Repair executed" "$ROOT/ops/logs/integrity_activity.log" 2>/dev/null; then
  echo "🧠 Integrity Agent — Active (last run logged)"
else
  echo "⚠️ Integrity Agent — No recent runs logged"
fi

if launchctl list | grep -q "com.tenx.integritycheck"; then
  echo "🔁 LaunchAgent (Integrity) — Loaded"
else
  echo "⚠️ LaunchAgent (Integrity) — Not loaded"
fi

if launchctl list | grep -q "com.tenx.chat-export"; then
  echo "🧠 LaunchAgent (Chat Export) — Loaded"
else
  echo "⚠️ LaunchAgent (Chat Export) — Not loaded"
fi

echo "---------------------------------------------"
echo "[INFO] Full status logged to $LOG"
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") — Status check complete" >> "$LOG"
