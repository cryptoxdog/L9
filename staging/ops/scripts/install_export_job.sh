#!/usr/bin/env bash
# Version: 1.0.0
# Canonical-Source: 10X Governance Suite
# Generated: 2025-10-06T17:10:32Z

# Install LaunchAgent for hourly chat export

# Create necessary directories
mkdir -p ops/logs
mkdir -p ~/Library/LaunchAgents

PLIST=~/Library/LaunchAgents/com.tenx.chat-export.plist
cat <<EOF > $PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.tenx.chat-export</string>
    <key>ProgramArguments</key>
    <array><string>/mnt/data/GlobalCommands_OPS_Canonical/ops/scripts/export_chats.sh</string></array>
    <key>StartInterval</key><integer>3600</integer>
    <key>RunAtLoad</key><true/></dict></plist>
EOF
launchctl unload $PLIST 2>/dev/null
launchctl load $PLIST
echo "[$(date)] LaunchAgent installed and activated." >> ops/logs/chat_export_launchd.out
