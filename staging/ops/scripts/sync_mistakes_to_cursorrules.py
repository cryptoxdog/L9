#!/usr/bin/env python3
"""
Sync Repeated Mistakes to .cursorrules
Automatically embeds repeated-mistakes.md content into global .cursorrules
Run by learning processor after updating repeated-mistakes.md
"""

import os
import re
from datetime import datetime
from pathlib import Path

def sync_mistakes_to_cursorrules():
    """Embed repeated mistakes directly into .cursorrules for auto-loading"""
    
    # Paths
    home = Path.home()
    mistakes_file = home / "Library/Application Support/Cursor/GlobalCommands/learning/failures/repeated-mistakes.md"
    cursorrules_file = home / ".cursorrules"
    
    print("🔄 Syncing repeated mistakes to .cursorrules...")
    
    # Read repeated mistakes
    if not mistakes_file.exists():
        print(f"❌ Mistakes file not found: {mistakes_file}")
        return False
    
    with open(mistakes_file, 'r') as f:
        mistakes_content = f.read()
    
    # Extract just the critical mistakes section
    mistakes_match = re.search(
        r'## 🚨 \*\*CRITICAL FAILURES TO NEVER REPEAT\*\*(.*?)---\n\n## 🔄',
        mistakes_content,
        re.DOTALL
    )
    
    if not mistakes_match:
        print("❌ Could not parse mistakes content")
        return False
    
    mistakes_section = mistakes_match.group(1).strip()
    
    # Parse individual mistakes
    mistake_pattern = r'### \*\*(\d+)\. (.*?)\*\*\n\*\*Mistake:\*\* (.*?)\n.*?\*\*Rule:\*\* (.*?)(?:\n\*\*Date Added:|---|\n\n###)'
    mistakes = re.findall(mistake_pattern, mistakes_section, re.DOTALL)
    
    # Build the embedded section
    embedded_section = f"""## 🚫 REPEATED MISTAKES - NEVER DO THESE AGAIN

**Source:** `~/Library/Application Support/Cursor/GlobalCommands/learning/failures/repeated-mistakes.md`
"""
    
    for num, title, mistake, rule in mistakes:
        # Clean up the text
        mistake_clean = ' '.join(mistake.strip().split())
        rule_clean = ' '.join(rule.strip().split())
        
        embedded_section += f"""
### {num}. {title}
❌ {mistake_clean}
✅ {rule_clean}
"""
    
    embedded_section += f"""
**Zero Tolerance Policy: ACTIVE**
**Auto-synced: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

---

*These rules apply GLOBALLY to every Cursor workspace*
*Last Updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
    
    # Read current .cursorrules
    if not cursorrules_file.exists():
        print(f"❌ .cursorrules not found: {cursorrules_file}")
        return False
    
    with open(cursorrules_file, 'r') as f:
        cursorrules_content = f.read()
    
    # Replace the repeated mistakes section
    pattern = r'## 🚫 REPEATED MISTAKES - NEVER DO THESE AGAIN.*?(?=\*These rules apply GLOBALLY|\Z)'
    
    if re.search(pattern, cursorrules_content, re.DOTALL):
        # Section exists - replace it
        new_content = re.sub(
            pattern,
            embedded_section.rstrip() + '\n\n',
            cursorrules_content,
            flags=re.DOTALL
        )
    else:
        # Section doesn't exist - add it before the footer
        footer_pattern = r'\n---\n\n\*These rules apply GLOBALLY'
        if re.search(footer_pattern, cursorrules_content):
            new_content = re.sub(
                footer_pattern,
                f'\n---\n\n{embedded_section}',
                cursorrules_content
            )
        else:
            # Just append
            new_content = cursorrules_content + '\n\n' + embedded_section
    
    # Write updated content
    with open(cursorrules_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Synced {len(mistakes)} mistakes to .cursorrules")
    print(f"📝 File: {cursorrules_file}")
    
    return True

if __name__ == '__main__':
    success = sync_mistakes_to_cursorrules()
    exit(0 if success else 1)

