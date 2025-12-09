#!/usr/bin/env bash
# Version: 1.1.1 - BULLETPROOF CHAT EXPORT
# Canonical-Source: 10X Governance Suite
# Generated: 2025-10-06T17:10:32Z
# Purpose: Snapshot ONLY Cursor chat data with retention policy

set -euo pipefail

# Anchor to script location, not current working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HOME/Library/Application Support/Cursor/User Data/Default/Local Storage/leveldb"
DEST="$SCRIPT_DIR/ops/logs/chat_exports"
STAMP=$(date +%Y-%m-%d_%H-%M-%S)
CHAT_DEST="$DEST/$STAMP/chat_data"

# Create destination directory
mkdir -p "$CHAT_DEST"

# Check if source exists
if [ ! -d "$SRC" ]; then
    echo "[$(date)] ERROR: No chat data found at $SRC" >> "$SCRIPT_DIR/ops/logs/chat_export_launchd.err"
    exit 1
fi

# Copy chat data with proper error handling
if cp -R "$SRC/" "$CHAT_DEST/"; then
    echo "[$(date)] Chat export completed: $STAMP" >> "$SCRIPT_DIR/ops/logs/chat_export_launchd.out"
    
    # Retention policy: keep only last 10 backups (safer sorting)
    find "$DEST" -maxdepth 1 -type d -name "20*" | sort | tail -n +11 | xargs rm -rf 2>/dev/null || true
    
    echo "[$(date)] Retention cleanup completed" >> "$SCRIPT_DIR/ops/logs/chat_export_launchd.out"
    
    # Log rotation: keep logs under 1MB
    for logfile in "$SCRIPT_DIR/ops/logs/chat_export_launchd.out" "$SCRIPT_DIR/ops/logs/chat_export_launchd.err"; do
        if [ -f "$logfile" ] && [ $(stat -f%z "$logfile" 2>/dev/null || echo 0) -gt 1048576 ]; then
            tail -n 500 "$logfile" > "${logfile}.tmp" && mv "${logfile}.tmp" "$logfile"
            echo "[$(date)] Log rotated: $logfile" >> "$SCRIPT_DIR/ops/logs/chat_export_launchd.out"
        fi
    done
else
    echo "[$(date)] ERROR: Copy failed for $SRC" >> "$SCRIPT_DIR/ops/logs/chat_export_launchd.err"
    exit 1
fi
