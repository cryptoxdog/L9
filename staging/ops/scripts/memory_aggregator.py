#!/usr/bin/env python3
"""
Memory Aggregator - Governance Intelligence Layer
Version: 2.0.0
Purpose: Parse chat exports and extract learnings automatically
"""

import os
import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

# Configuration
GLOBAL_COMMANDS = Path(os.path.expanduser("~/Library/Application Support/Cursor/GlobalCommands"))
CHAT_EXPORTS_DIR = GLOBAL_COMMANDS / "ops/logs/chat_exports"
MEMORY_INDEX = GLOBAL_COMMANDS / "ops/logs/memory_index.json"
LEARNING_DIR = GLOBAL_COMMANDS / "learning"

# Learning file paths
REPEATED_MISTAKES = LEARNING_DIR / "failures/repeated-mistakes.md"
QUICK_FIXES = LEARNING_DIR / "patterns/quick-fixes.md"
AUTH_FIXES = LEARNING_DIR / "solutions/authentication-fixes.md"
JSON_ISSUES = LEARNING_DIR / "solutions/json-issues.md"

class LearningPattern:
    """Represents a learning pattern extracted from conversations"""
    def __init__(self, pattern_type: str, content: str, context: str, timestamp: str):
        self.pattern_type = pattern_type  # mistake, solution, pattern, insight
        self.content = content
        self.context = context
        self.timestamp = timestamp
        self.hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate unique hash for deduplication"""
        unique_str = f"{self.pattern_type}:{self.content}:{self.context}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash": self.hash,
            "type": self.pattern_type,
            "content": self.content,
            "context": self.context,
            "timestamp": self.timestamp
        }


class MemoryAggregator:
    """Main class for aggregating and processing chat memories"""
    
    def __init__(self):
        self.memory_index = self._load_memory_index()
        self.processed_exports = set(self.memory_index.get("processed_exports", []))
        self.learnings = self.memory_index.get("learnings", [])
        self.stats = self.memory_index.get("stats", {
            "total_exports_processed": 0,
            "total_conversations": 0,
            "total_learnings_extracted": 0,
            "last_run": None
        })
    
    def _load_memory_index(self) -> Dict[str, Any]:
        """Load existing memory index or create new one"""
        if MEMORY_INDEX.exists():
            try:
                with open(MEMORY_INDEX, 'r') as f:
                    content = f.read().strip()
                    if content and content != "{}":
                        return json.loads(content)
            except json.JSONDecodeError:
                print(f"⚠️  Memory index corrupted, creating new one")
        
        return {
            "version": "2.0.0",
            "last_updated": None,
            "processed_exports": [],
            "learnings": [],
            "stats": {
                "total_exports_processed": 0,
                "total_conversations": 0,
                "total_learnings_extracted": 0,
                "last_run": None
            }
        }
    
    def _save_memory_index(self):
        """Save memory index to disk"""
        self.memory_index["last_updated"] = datetime.now().isoformat()
        self.memory_index["processed_exports"] = list(self.processed_exports)
        self.memory_index["learnings"] = self.learnings
        self.memory_index["stats"] = self.stats
        
        MEMORY_INDEX.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_INDEX, 'w') as f:
            json.dump(self.memory_index, f, indent=2)
        print(f"✅ Memory index saved: {len(self.learnings)} learnings tracked")
    
    def process_all_exports(self):
        """Process all chat exports"""
        if not CHAT_EXPORTS_DIR.exists():
            print(f"❌ No chat exports found at: {CHAT_EXPORTS_DIR}")
            return
        
        export_dirs = sorted([d for d in CHAT_EXPORTS_DIR.iterdir() if d.is_dir()])
        print(f"📂 Found {len(export_dirs)} chat export directories")
        
        new_exports = [d for d in export_dirs if d.name not in self.processed_exports]
        
        if not new_exports:
            print("✅ No new exports to process")
            return
        
        print(f"🔍 Processing {len(new_exports)} new exports...")
        
        for export_dir in new_exports:
            print(f"\n📊 Processing: {export_dir.name}")
            self._process_export(export_dir)
            self.processed_exports.add(export_dir.name)
            self.stats["total_exports_processed"] += 1
        
        self.stats["last_run"] = datetime.now().isoformat()
        self._save_memory_index()
        print(f"\n✅ Processing complete! Total learnings: {len(self.learnings)}")
    
    def _process_export(self, export_dir: Path):
        """Process a single export directory"""
        workspace_storage = export_dir / "User/workspaceStorage"
        
        if not workspace_storage.exists():
            print(f"  ⚠️  No workspace storage found")
            return
        
        workspaces = [d for d in workspace_storage.iterdir() if d.is_dir()]
        conversations_found = 0
        
        for workspace in workspaces:
            state_db = workspace / "state.vscdb"
            if not state_db.exists():
                continue
            
            try:
                conversations = self._extract_conversations(state_db)
                if conversations:
                    conversations_found += len(conversations)
                    self.stats["total_conversations"] += len(conversations)
                    self._analyze_conversations(conversations)
            except Exception as e:
                print(f"  ⚠️  Error processing {workspace.name}: {e}")
        
        print(f"  ✅ Found {conversations_found} conversations")
    
    def _extract_conversations(self, state_db: Path) -> List[Dict[str, Any]]:
        """Extract conversations from state database"""
        conversations = []
        
        try:
            conn = sqlite3.connect(str(state_db))
            cursor = conn.cursor()
            
            # Extract composer data (contains chat history)
            cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
            result = cursor.fetchone()
            
            if result and result[0]:
                try:
                    composer_data = json.loads(result[0])
                    if 'allComposers' in composer_data:
                        conversations.extend(composer_data['allComposers'])
                except json.JSONDecodeError:
                    pass
            
            conn.close()
        except Exception as e:
            print(f"    ⚠️  Database error: {e}")
        
        return conversations
    
    def _analyze_conversations(self, conversations: List[Dict[str, Any]]):
        """Analyze conversations for learning patterns"""
        for conv in conversations:
            # Skip if no meaningful data
            if not isinstance(conv, dict):
                continue
            
            # Look for correction patterns
            self._detect_corrections(conv)
            
            # Look for mistakes
            self._detect_mistakes(conv)
            
            # Look for solutions
            self._detect_solutions(conv)
    
    def _detect_corrections(self, conv: Dict[str, Any]):
        """Detect user corrections and learn from them"""
        # Patterns indicating user correction
        correction_patterns = [
            r"(?i)(no|wrong|incorrect|that'?s not right|you'?re wrong)",
            r"(?i)(actually|instead|should be|meant to)",
            r"(?i)(i (told|said|asked) you|i want you to)",
            r"(?i)(misunderstood|didn'?t understand|not what i meant)"
        ]
        
        conv_text = json.dumps(conv).lower()
        
        for pattern in correction_patterns:
            if re.search(pattern, conv_text):
                learning = LearningPattern(
                    pattern_type="mistake",
                    content=f"User correction detected in conversation",
                    context=str(conv.get('composerId', 'unknown'))[:50],
                    timestamp=datetime.now().isoformat()
                )
                self._add_learning(learning)
                break
    
    def _detect_mistakes(self, conv: Dict[str, Any]):
        """Detect common mistake patterns"""
        conv_text = json.dumps(conv).lower()
        
        mistake_indicators = {
            "auth": [r"authentication failed", r"credential.*error", r"401", r"403"],
            "json": [r"json.*error", r"parsing.*failed", r"invalid json"],
            "symlink": [r"display.*folder", r"show.*sidebar", r"left margin"],
            "supabase": [r"supabase.*auth", r"supabase.*error"],
            "n8n": [r"n8n.*error", r"workflow.*failed", r"node.*error"]
        }
        
        for mistake_type, patterns in mistake_indicators.items():
            for pattern in patterns:
                if re.search(pattern, conv_text):
                    learning = LearningPattern(
                        pattern_type="mistake",
                        content=f"Detected {mistake_type} related issue",
                        context=pattern,
                        timestamp=datetime.now().isoformat()
                    )
                    self._add_learning(learning)
    
    def _detect_solutions(self, conv: Dict[str, Any]):
        """Detect successful solutions"""
        conv_text = json.dumps(conv).lower()
        
        solution_indicators = [
            r"(?i)(fixed|solved|working now|success|resolved)",
            r"(?i)(that worked|perfect|exactly|great)",
            r"(?i)(✅|done|complete)"
        ]
        
        for pattern in solution_indicators:
            if re.search(pattern, conv_text):
                learning = LearningPattern(
                    pattern_type="solution",
                    content="Successful solution detected",
                    context=str(conv.get('composerId', 'unknown'))[:50],
                    timestamp=datetime.now().isoformat()
                )
                self._add_learning(learning)
                break
    
    def _add_learning(self, learning: LearningPattern):
        """Add learning to index (with deduplication)"""
        learning_dict = learning.to_dict()
        
        # Check if already exists
        existing_hashes = [l['hash'] for l in self.learnings]
        if learning.hash not in existing_hashes:
            self.learnings.append(learning_dict)
            self.stats["total_learnings_extracted"] += 1
    
    def generate_report(self) -> str:
        """Generate summary report"""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║          MEMORY AGGREGATOR - LEARNING REPORT              ║
╠════════════════════════════════════════════════════════════╣
║  Exports Processed:     {self.stats['total_exports_processed']:>4}                              ║
║  Conversations Found:   {self.stats['total_conversations']:>4}                              ║
║  Learnings Extracted:   {self.stats['total_learnings_extracted']:>4}                              ║
║  Last Run:              {self.stats.get('last_run', 'Never')[:19]:>19}           ║
╠════════════════════════════════════════════════════════════╣
║  LEARNING BREAKDOWN                                        ║
╠════════════════════════════════════════════════════════════╣
"""
        
        # Count by type
        types = {}
        for l in self.learnings:
            types[l['type']] = types.get(l['type'], 0) + 1
        
        for ltype, count in types.items():
            report += f"║  {ltype.capitalize():<20} {count:>4}                          ║\n"
        
        report += "╚════════════════════════════════════════════════════════════╝\n"
        
        return report


def main():
    """Main execution"""
    print("🚀 Memory Aggregator v2.0.0 - Starting...\n")
    
    aggregator = MemoryAggregator()
    aggregator.process_all_exports()
    
    # Generate and display report
    report = aggregator.generate_report()
    print(report)
    
    # Save report to log
    log_file = GLOBAL_COMMANDS / "ops/logs/memory_aggregator.log"
    with open(log_file, 'a') as f:
        f.write(f"\n{datetime.now().isoformat()}\n{report}\n")
    
    print(f"📝 Full log: {log_file}")


if __name__ == "__main__":
    main()

