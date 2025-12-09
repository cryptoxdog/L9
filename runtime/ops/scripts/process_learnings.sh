#!/usr/bin/env bash
# Version: 2.0.0
# Purpose: Master script to process chat exports and update learnings
# Runs: Memory Aggregator → Learning Updater

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../logs/learning_processing.log"

echo "[$(date)] ========================================" >> "$LOG_FILE"
echo "[$(date)] Starting Learning Processing Pipeline" >> "$LOG_FILE"

# Step 1: Run Memory Aggregator
echo "[$(date)] Step 1/2: Running Memory Aggregator..." >> "$LOG_FILE"
python3 "$SCRIPT_DIR/memory_aggregator.py" >> "$LOG_FILE" 2>&1

# Step 2: Apply learnings to files
echo "[$(date)] Step 2/3: Updating Learning Files..." >> "$LOG_FILE"
python3 "$SCRIPT_DIR/learning_updater.py" >> "$LOG_FILE" 2>&1

# Step 3: Sync to .cursorrules for auto-loading
echo "[$(date)] Step 3/3: Syncing to .cursorrules..." >> "$LOG_FILE"
python3 "$SCRIPT_DIR/sync_mistakes_to_cursorrules.py" >> "$LOG_FILE" 2>&1

echo "[$(date)] Learning Processing Pipeline Complete" >> "$LOG_FILE"
echo "[$(date)] ========================================" >> "$LOG_FILE"

