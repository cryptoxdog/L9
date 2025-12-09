#!/usr/bin/env bash
# Version: 1.0.0
# Purpose: Setup .cursor-commands symlink in current workspace
# Usage: Run this in any workspace to enable @.cursor-commands/ access

set -e

GLOBAL_COMMANDS="$HOME/Library/Application Support/Cursor/GlobalCommands"
WORKSPACE_DIR="$(pwd)"
SYMLINK="$WORKSPACE_DIR/.cursor-commands"

echo "🔧 Setting up workspace symlinks..."
echo ""

# Check if GlobalCommands exists
if [ ! -d "$GLOBAL_COMMANDS" ]; then
    echo "❌ GlobalCommands directory not found!"
    echo "   Expected: $GLOBAL_COMMANDS"
    exit 1
fi

# Check if symlink already exists
if [ -L "$SYMLINK" ]; then
    TARGET=$(readlink "$SYMLINK")
    if [ "$TARGET" = "$GLOBAL_COMMANDS" ]; then
        echo "✅ .cursor-commands symlink already exists and points to correct location"
        echo "   Location: $SYMLINK"
        echo "   Target: $GLOBAL_COMMANDS"
        exit 0
    else
        echo "⚠️  Symlink exists but points to wrong location"
        echo "   Current target: $TARGET"
        echo "   Expected target: $GLOBAL_COMMANDS"
        echo "   Removing old symlink..."
        rm "$SYMLINK"
    fi
elif [ -e "$SYMLINK" ]; then
    echo "⚠️  .cursor-commands exists but is not a symlink!"
    echo "   Please remove it manually: rm -rf .cursor-commands"
    exit 1
fi

# Create the symlink
echo "Creating symlink..."
ln -s "$GLOBAL_COMMANDS" "$SYMLINK"

if [ -L "$SYMLINK" ]; then
    echo ""
    echo "✅ SUCCESS! Symlink created"
    echo ""
    echo "📁 You can now access:"
    echo "   @.cursor-commands/learning/failures/repeated-mistakes.md"
    echo "   @.cursor-commands/learning/patterns/quick-fixes.md"
    echo "   @.cursor-commands/profiles/reasoning.md"
    echo "   @.cursor-commands/rules.json"
    echo "   @.cursor-commands/ops/logs/memory_index.json"
    echo ""
    echo "🎯 Test it: ls -la .cursor-commands"
else
    echo "❌ Failed to create symlink"
    exit 1
fi

