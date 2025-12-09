# ⚡ LEARNING SYSTEM - QUICK REFERENCE

## 🔍 Status Check (30 seconds)
```bash
# Check if running
launchctl list | grep learning-processor

# View stats
cat "$HOME/Library/Application Support/Cursor/GlobalCommands/ops/logs/memory_index.json"

# Recent logs
tail -20 "$HOME/Library/Application Support/Cursor/GlobalCommands/ops/logs/learning_processing.log"
```

## 🚀 Manual Operations

### Run Now
```bash
bash "$HOME/Library/Application Support/Cursor/GlobalCommands/ops/scripts/process_learnings.sh"
```

### Restart Service
```bash
launchctl unload ~/Library/LaunchAgents/com.tenx.learning-processor.plist
launchctl load ~/Library/LaunchAgents/com.tenx.learning-processor.plist
```

## 📊 View Learning Files
```bash
# Repeated mistakes
cat "$HOME/Library/Application Support/Cursor/GlobalCommands/learning/failures/repeated-mistakes.md"

# Quick fixes
cat "$HOME/Library/Application Support/Cursor/GlobalCommands/learning/patterns/quick-fixes.md"
```

## 🎯 What Gets Learned

✅ User corrections ("no, that's wrong")  
✅ Common mistakes (auth, JSON, etc)  
✅ Successful solutions ("that worked!")  
✅ Pattern detection (symlinks, n8n, etc)

## 🔄 Processing Flow

1. **Every hour**: Chat exports captured
2. **Every hour**: Exports analyzed for patterns
3. **Automatic**: Learnings added to files
4. **Automatic**: Memory index updated

## 📁 Key Locations

| Item | Path |
|------|------|
| Status Dashboard | `ops/LEARNING_SYSTEM_STATUS.md` |
| Processing Log | `ops/logs/learning_processing.log` |
| Memory Index | `ops/logs/memory_index.json` |
| Chat Exports | `ops/logs/chat_exports/` |

---

**Quick Status:** Run `launchctl list | grep tenx` to see all services!

