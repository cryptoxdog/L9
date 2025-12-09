#!/usr/bin/env python3
"""
Sync Project Rules (.mdc files) from Dropbox Governance to Workspace
Ensures all Project Rules are available in workspace .cursor/rules/
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

def sync_project_rules(workspace_path: Path = None, source_path: Path = None, dry_run: bool = False) -> Tuple[int, int, List[str]]:
    """
    Sync Project Rules from source to workspace
    
    Returns:
        (copied_count, skipped_count, missing_files)
    """
    if workspace_path is None:
        workspace_path = Path.cwd()
    else:
        workspace_path = Path(workspace_path)
    
    if source_path is None:
        source_path = Path.home() / "Dropbox/Cursor Governance/.cursor/rules"
    else:
        source_path = Path(source_path)
    
    workspace_rules_dir = workspace_path / ".cursor/rules"
    workspace_rules_dir.mkdir(parents=True, exist_ok=True)
    
    if not source_path.exists():
        print(f"❌ Source rules directory not found: {source_path}")
        return 0, 0, []
    
    # Find all .mdc files in source
    source_files = list(source_path.glob("*.mdc"))
    
    if not source_files:
        print(f"⚠️  No .mdc files found in source: {source_path}")
        return 0, 0, []
    
    copied_count = 0
    skipped_count = 0
    missing_files = []
    
    print(f"🔄 Syncing Project Rules from: {source_path}")
    print(f"   To: {workspace_rules_dir}")
    print()
    
    for source_file in source_files:
        target_file = workspace_rules_dir / source_file.name
        
        # Check if file needs updating
        should_copy = True
        if target_file.exists():
            # Compare modification times
            source_mtime = source_file.stat().st_mtime
            target_mtime = target_file.stat().st_mtime
            
            if source_mtime <= target_mtime:
                should_copy = False
                skipped_count += 1
                if not dry_run:
                    print(f"   ⏭️  Skipped (up to date): {source_file.name}")
        
        if should_copy:
            if dry_run:
                print(f"   📋 Would copy: {source_file.name}")
                copied_count += 1
            else:
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"   ✅ Copied: {source_file.name}")
                    copied_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to copy {source_file.name}: {e}")
                    missing_files.append(source_file.name)
    
    # Check for files in workspace that don't exist in source
    workspace_files = list(workspace_rules_dir.glob("*.mdc"))
    source_names = {f.name for f in source_files}
    extra_files = [f for f in workspace_files if f.name not in source_names]
    
    if extra_files:
        print()
        print(f"⚠️  Found {len(extra_files)} files in workspace not in source:")
        for f in extra_files:
            print(f"   📄 {f.name} (keeping)")
    
    return copied_count, skipped_count, missing_files

def main():
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be copied")
        print()
    
    copied, skipped, missing = sync_project_rules(dry_run=dry_run)
    
    print()
    print("="*70)
    print("SYNC SUMMARY")
    print("="*70)
    print(f"   Copied: {copied} files")
    print(f"   Skipped: {skipped} files (already up to date)")
    if missing:
        print(f"   Failed: {len(missing)} files")
    print()
    
    if not dry_run:
        # Count final files
        workspace_rules = Path.cwd() / ".cursor/rules"
        final_count = len(list(workspace_rules.glob("*.mdc")))
        print(f"✅ Total Project Rules in workspace: {final_count}")
    
    return 0 if not missing else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

