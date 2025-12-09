#!/usr/bin/env python3
"""
Governance System Loader
Version: 1.0.0
Purpose: Initialize and load governance system at session start
Usage: python load_governance.py
       or via conda: conda run -n governance python load_governance.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
GLOBAL_COMMANDS = Path(os.path.expanduser("~/Library/Application Support/Cursor/GlobalCommands"))
WORKSPACE_DIR = Path.cwd()
SYMLINK = WORKSPACE_DIR / ".cursor-commands"
RULES_FILE = GLOBAL_COMMANDS / "rules.json"
MEMORY_INDEX = GLOBAL_COMMANDS / "ops/logs/memory_index.json"
LOG_FILE = GLOBAL_COMMANDS / "ops/logs/governance_load.log"

class GovernanceLoader:
    """Loads and initializes the governance system"""
    
    def __init__(self):
        self.status = {
            "symlink": False,
            "rules": False,
            "memory_index": False,
            "learning_processor": False
        }
        self.messages = []
    
    def check_symlink(self) -> bool:
        """Check if workspace symlink exists"""
        if SYMLINK.exists() and SYMLINK.is_symlink():
            target = SYMLINK.readlink()
            if str(target) == str(GLOBAL_COMMANDS):
                self.status["symlink"] = True
                self.messages.append("✅ .cursor-commands symlink active")
                return True
        
        self.messages.append("⚠️  .cursor-commands symlink missing")
        return False
    
    def setup_symlink(self) -> bool:
        """Create workspace symlink if missing"""
        if not GLOBAL_COMMANDS.exists():
            self.messages.append(f"❌ GlobalCommands directory not found: {GLOBAL_COMMANDS}")
            return False
        
        try:
            if SYMLINK.exists():
                if SYMLINK.is_symlink():
                    self.messages.append("✅ Symlink already exists")
                    return True
                else:
                    self.messages.append("⚠️  .cursor-commands exists but is not a symlink")
                    return False
            
            SYMLINK.symlink_to(GLOBAL_COMMANDS)
            self.status["symlink"] = True
            self.messages.append("✅ Created .cursor-commands symlink")
            return True
        except Exception as e:
            self.messages.append(f"❌ Failed to create symlink: {e}")
            return False
    
    def check_rules(self) -> bool:
        """Check if governance rules file exists"""
        if RULES_FILE.exists():
            try:
                with open(RULES_FILE, 'r') as f:
                    rules = json.load(f)
                    version = rules.get('version', 'unknown')
                    self.status["rules"] = True
                    self.messages.append(f"✅ Governance rules v{version} loaded")
                    return True
            except json.JSONDecodeError:
                self.messages.append("⚠️  Rules file exists but is invalid JSON")
                return False
        
        self.messages.append("⚠️  Rules file not found")
        return False
    
    def check_memory_index(self) -> bool:
        """Check if memory index exists and load stats"""
        if MEMORY_INDEX.exists():
            try:
                with open(MEMORY_INDEX, 'r') as f:
                    data = json.load(f)
                    learnings_count = len(data.get('learnings', []))
                    self.status["memory_index"] = True
                    self.messages.append(f"✅ Learning system active: {learnings_count} learnings")
                    return True
            except (json.JSONDecodeError, KeyError):
                self.messages.append("⚠️  Memory index exists but is invalid")
                return False
        
        self.messages.append("⚠️  Memory index not found")
        return False
    
    def check_learning_processor(self) -> bool:
        """Check if learning processor service is running"""
        try:
            result = subprocess.run(
                ['launchctl', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'com.tenx.learning-processor' in result.stdout:
                self.status["learning_processor"] = True
                self.messages.append("✅ Learning processor service active")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.messages.append("⚠️  Learning processor not running")
        return False
    
    def log_to_file(self):
        """Log governance load status to file"""
        MEMORY_INDEX.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "workspace": str(WORKSPACE_DIR),
            "status": self.status,
            "messages": self.messages
        }
        
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{log_entry['timestamp']}] Governance Load\n")
            for msg in self.messages:
                f.write(f"[{log_entry['timestamp']}] {msg}\n")
            f.write("\n")
    
    def print_summary(self):
        """Print formatted summary"""
        print("\n" + "="*55)
        print("  GOVERNANCE SYSTEM LOADER")
        print("="*55)
        print()
        
        for msg in self.messages:
            print(f"  {msg}")
        
        print()
        print("="*55)
        print()
        
        # Summary
        all_ok = all(self.status.values())
        if all_ok:
            print("✅ Governance system fully operational")
        else:
            print("⚠️  Some components need attention")
            if not self.status["symlink"]:
                print("   Run: bash ops/scripts/setup_workspace_symlinks.sh")
    
    def load(self) -> bool:
        """Main loading function"""
        print("🔧 Loading governance system...\n")
        
        # Check symlink
        if not self.check_symlink():
            self.setup_symlink()
        
        # Check rules
        self.check_rules()
        
        # Check memory index
        self.check_memory_index()
        
        # Check learning processor
        self.check_learning_processor()
        
        # Log and display
        self.log_to_file()
        self.print_summary()
        
        return all(self.status.values())

def main():
    """Entry point"""
    loader = GovernanceLoader()
    success = loader.load()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

