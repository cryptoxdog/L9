#!/usr/bin/env bash
# Version: 1.0.0
# Purpose: Deploy .cursorrules to a workspace (or all workspaces)
# Usage: 
#   In workspace: bash ~/Library/Application\ Support/Cursor/GlobalCommands/ops/scripts/deploy_cursorrules_global.sh
#   Or provide path: bash deploy_cursorrules_global.sh /path/to/workspace

set -e

GLOBAL_COMMANDS="$HOME/Library/Application Support/Cursor/GlobalCommands"
SOURCE_CURSORRULES="$GLOBAL_COMMANDS/templates/.cursorrules"
TARGET_DIR="${1:-$(pwd)}"

echo "🚀 Deploying .cursorrules to workspace..."
echo ""

# Check if source template exists
if [ ! -f "$SOURCE_CURSORRULES" ]; then
    echo "⚠️  No .cursorrules template found at: $SOURCE_CURSORRULES"
    echo "   Using current workspace .cursorrules as template..."
    SOURCE_CURSORRULES="$(pwd)/.cursorrules"
    
    if [ ! -f "$SOURCE_CURSORRULES" ]; then
        echo "❌ No .cursorrules found to use as template!"
        exit 1
    fi
fi

# Ensure target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Target directory not found: $TARGET_DIR"
    exit 1
fi

TARGET_FILE="$TARGET_DIR/.cursorrules"

# Backup existing if present
if [ -f "$TARGET_FILE" ]; then
    BACKUP="$TARGET_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 Backing up existing .cursorrules to:"
    echo "   $BACKUP"
    cp "$TARGET_FILE" "$BACKUP"
fi

# Copy template to target
cp "$SOURCE_CURSORRULES" "$TARGET_FILE"

echo ""
echo "✅ Deployed .cursorrules to: $TARGET_DIR"
echo ""

# Setup symlink
SYMLINK="$TARGET_DIR/.cursor-commands"

if [ -L "$SYMLINK" ]; then
    echo "✅ .cursor-commands symlink already exists"
else
    echo "🔗 Creating .cursor-commands symlink..."
    ln -s "$GLOBAL_COMMANDS" "$SYMLINK"
    echo "✅ Symlink created"
fi

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║     WORKSPACE SETUP COMPLETE             ║"
echo "╠═══════════════════════════════════════════╣"
echo "║  .cursorrules deployed                   ║"
echo "║  .cursor-commands symlink active         ║"
echo "║  All governance files accessible         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "🎯 You can now use: @.cursor-commands/ in this workspace!"


