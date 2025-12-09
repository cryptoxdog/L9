#!/usr/bin/env bash
# Version: 1.0.0
# Purpose: Install LaunchAgent for automatic learning processing
# Runs every hour after chat exports complete

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST=~/Library/LaunchAgents/com.tenx.learning-processor.plist
LOG_FILE="$SCRIPT_DIR/../logs/learning_processing.log"

echo "🚀 Installing Learning Processor LaunchAgent..."

# Create necessary directories
mkdir -p "$SCRIPT_DIR/../logs"
mkdir -p ~/Library/LaunchAgents

# Create the plist file
cat <<EOF > "$PLIST"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tenx.learning-processor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/process_learnings.sh</string>
    </array>
    
    <key>StartInterval</key>
    <integer>3600</integer>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$LOG_FILE</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_FILE</string>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
</dict>
</plist>
EOF

# Unload if already loaded (ignore errors)
launchctl unload "$PLIST" 2>/dev/null || true

# Load the new agent
launchctl load "$PLIST"

echo "✅ Learning Processor LaunchAgent installed!"
echo "📊 Runs every hour to process chat exports"
echo "📝 Logs: $LOG_FILE"
echo ""
echo "🔧 Management commands:"
echo "   Stop:   launchctl unload $PLIST"
echo "   Start:  launchctl load $PLIST"
echo "   Status: launchctl list | grep learning-processor"
echo ""
echo "[$(date)] LaunchAgent installed and activated." >> "$LOG_FILE"

