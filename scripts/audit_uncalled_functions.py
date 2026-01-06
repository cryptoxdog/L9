#!/usr/bin/env python3
"""
L9 Uncalled Function Auditor v2.0
==================================

Finds functions defined with no parameters `def func():` that are TRULY never called.

Filters out FALSE POSITIVES:
- FastAPI route handlers (@router.*, @app.*, @pytest.fixture)
- Dictionary-registered functions (called via dict lookup)
- Template/archive/deprecated files
- Docstring examples
- Known entry points

Usage:
    python scripts/audit_uncalled_functions.py
    python scripts/audit_uncalled_functions.py --include-private  # include _private functions
    python scripts/audit_uncalled_functions.py --include-tests    # include test files
    python scripts/audit_uncalled_functions.py --verbose          # show why functions were skipped
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import NamedTuple, Optional
import structlog

logger = structlog.get_logger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Directories to skip entirely
SKIP_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules', 
    '.venv', 'venv', 'env', '.cursor', 'docs', 'reports',
    # Template/archive directories (never meant to be called)
    'archive', 'deprecated', 'templates', '.dora',
    'codegen/templates', 'codegen/code-gen-files',
}

# Partial path patterns to skip (template/example files)
SKIP_PATH_PATTERNS = [
    'template',
    'example',
    '/archive/',
    '/deprecated/',
    '/.dora/',
    '/igor/audit-tools/',  # Duplicate of tools/export_repo_indexes.py
]

# Function names that are entry points (called by framework, not direct calls)
ENTRY_POINTS = {
    'main', 'setup', 'teardown', 'run', 'start', 'stop',
    'configure', 'initialize', 'cleanup', 'shutdown',
    'lifespan',  # FastAPI lifespan
    'on_startup', 'on_shutdown',  # FastAPI events
    'reload_config',  # Hot-reload utility for config modules
}

# Decorators that indicate framework-invoked functions (false positives)
FRAMEWORK_DECORATORS = [
    r'@router\.',           # FastAPI router decorators
    r'@app\.',              # FastAPI app decorators  
    r'@pytest\.',           # pytest fixtures/marks
    r'@fixture',            # pytest fixture shorthand
    r'@mark\.',             # pytest marks
    r'@celery\.',           # Celery task decorators
    r'@dramatiq\.',         # Dramatiq actor decorators
    r'@click\.',            # Click CLI decorators
    r'@staticmethod',       # Could be called via class
    r'@classmethod',        # Could be called via class
    r'@property',           # Property getter
    r'@.*\.getter',         # Property getter
    r'@.*\.setter',         # Property setter
]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class FunctionInfo(NamedTuple):
    """Information about a function definition."""
    name: str
    line_num: int
    filepath: Path
    has_decorator: bool
    decorator_text: str
    is_dict_registered: bool
    in_docstring: bool
    skip_reason: Optional[str]


# =============================================================================
# DETECTION FUNCTIONS
# =============================================================================

def should_skip_file(filepath: Path, root: Path) -> bool:
    """Check if file should be skipped based on path patterns."""
    rel_path = str(filepath.relative_to(root))
    
    # Check skip directories
    for skip_dir in SKIP_DIRS:
        if skip_dir in filepath.parts:
            return True
    
    # Check path patterns
    for pattern in SKIP_PATH_PATTERNS:
        if pattern in rel_path.lower():
            return True
    
    return False


def has_framework_decorator(lines: list[str], func_line_idx: int) -> tuple[bool, str]:
    """
    Check if function has a framework decorator in the lines above it.
    Returns (has_decorator, decorator_text).
    """
    # Look at up to 5 lines above the function definition
    start_idx = max(0, func_line_idx - 5)
    
    for i in range(func_line_idx - 1, start_idx - 1, -1):
        line = lines[i].strip()
        
        # Stop if we hit another def/class (we've gone too far)
        if line.startswith('def ') or line.startswith('async def ') or line.startswith('class '):
            break
        
        # Check for framework decorators
        for pattern in FRAMEWORK_DECORATORS:
            if re.search(pattern, line):
                return True, line
        
        # Also catch any @something.something pattern for routers
        if re.match(r'^@\w+\.\w+', line):
            return True, line
    
    return False, ""


def is_dict_registered(func_name: str, content: str) -> bool:
    """
    Check if function is registered in a dictionary (called via dict lookup).
    
    Patterns detected:
    - "key": func_name
    - "key": func_name,
    - ("desc", func_name)
    - (emoji, func_name)
    """
    patterns = [
        # Dict value: "key": func_name or "key": func_name,
        rf'["\'][^"\']+["\']\s*:\s*{re.escape(func_name)}\s*[,\}})]',
        # Tuple with function: ("desc", func_name) or (emoji, func_name)
        rf'\([^)]*,\s*{re.escape(func_name)}\s*\)',
        # List element: [func_name, other] or [other, func_name]
        rf'\[\s*{re.escape(func_name)}\s*[,\]]',
        # Direct assignment to dict: generators["key"] = func_name
        rf'\[["\'][^"\']+["\']\]\s*=\s*{re.escape(func_name)}',
    ]
    
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    
    return False


def is_in_docstring(lines: list[str], func_line_idx: int) -> bool:
    """
    Check if function definition is inside a docstring (example code).
    """
    # Count triple quotes before this line
    content_before = '\n'.join(lines[:func_line_idx])
    
    # Find all docstring markers
    triple_double = content_before.count('"""')
    triple_single = content_before.count("'''")
    
    # If odd number of markers, we're inside a docstring
    return (triple_double % 2 == 1) or (triple_single % 2 == 1)


def is_function_referenced(func_name: str, all_content: str) -> bool:
    """
    Check if function is called OR referenced anywhere.
    
    Detects:
    - Direct calls: func_name()
    - References: func_name (passed as callback, stored in variable, etc.)
    - Attribute access: obj.func_name
    """
    # Pattern for direct call (excluding definition)
    call_pattern = rf'(?<!def\s)(?<!async def\s){re.escape(func_name)}\s*\('
    if re.search(call_pattern, all_content):
        return True
    
    # Pattern for reference (function passed as value, not called)
    # Look for patterns like: = func_name, (func_name, or func_name)
    ref_patterns = [
        rf'=\s*{re.escape(func_name)}\s*[,\n\]]',  # assignment
        rf',\s*{re.escape(func_name)}\s*[,\)\]]',   # in tuple/list
        rf'\(\s*{re.escape(func_name)}\s*[,\)]',    # first arg or only arg
    ]
    
    for pattern in ref_patterns:
        if re.search(pattern, all_content):
            return True
    
    return False


# =============================================================================
# MAIN SCANNING LOGIC
# =============================================================================

def find_python_files(root: Path, include_tests: bool = False) -> list[Path]:
    """Find all Python files to scan."""
    files = []
    for path in root.rglob('*.py'):
        # Skip if path should be skipped
        if should_skip_file(path, root):
            continue
        
        # Skip tests unless requested
        if not include_tests and ('test_' in path.name or '/tests/' in str(path)):
            continue
        
        files.append(path)
    return files


def analyze_file(filepath: Path, all_content: str, include_private: bool, verbose: bool) -> list[FunctionInfo]:
    """
    Analyze a file for truly uncalled parameterless functions.
    Returns list of FunctionInfo for functions that are TRULY uncalled.
    """
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []
    
    lines = content.split('\n')
    results = []
    
    for i, line in enumerate(lines):
        # Match: def function_name(): or async def function_name():
        match = re.match(r'\s*(async\s+)?def\s+([a-z_][a-z0-9_]*)\s*\(\s*\)\s*:', line)
        if not match:
            continue
        
        func_name = match.group(2)
        line_num = i + 1  # 1-indexed
        
        # Skip private functions unless requested
        if not include_private and func_name.startswith('_'):
            continue
        
        # Skip dunder methods
        if func_name.startswith('__') and func_name.endswith('__'):
            continue
        
        # Skip known entry points
        if func_name in ENTRY_POINTS:
            if verbose:
                logger.info(f"  SKIP (entry point): {func_name} at {filepath}:{line_num}")
            continue
        
        # Check for framework decorators (FALSE POSITIVE)
        has_decorator, decorator_text = has_framework_decorator(lines, i)
        if has_decorator:
            if verbose:
                logger.info(f"  SKIP (decorator): {func_name} has {decorator_text}")
            continue
        
        # Check if in docstring (FALSE POSITIVE)
        if is_in_docstring(lines, i):
            if verbose:
                logger.info(f"  SKIP (docstring): {func_name} is inside a docstring")
            continue
        
        # Check if registered in dictionary (FALSE POSITIVE)
        if is_dict_registered(func_name, all_content):
            if verbose:
                logger.info(f"  SKIP (dict-registered): {func_name} is registered in a dict")
            continue
        
        # Check if function is called or referenced anywhere
        if is_function_referenced(func_name, all_content):
            if verbose:
                logger.info(f"  SKIP (referenced): {func_name} is called/referenced")
            continue
        
        # This is a TRUE uncalled function
        results.append(FunctionInfo(
            name=func_name,
            line_num=line_num,
            filepath=filepath,
            has_decorator=False,
            decorator_text="",
            is_dict_registered=False,
            in_docstring=False,
            skip_reason=None,
        ))
    
    return results


def main():
    include_private = '--include-private' in sys.argv
    include_tests = '--include-tests' in sys.argv
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    root = Path(__file__).parent.parent
    
    logger.info(f"\n{'='*70}")
    logger.info("L9 UNCALLED FUNCTION AUDIT v2.0")
    logger.info(f"{'='*70}")
    logger.info(f"Scanning: {root}")
    logger.info(f"Include private (_func): {include_private}")
    logger.info(f"Include test files: {include_tests}")
    logger.info(f"Verbose mode: {verbose}")
    
    logger.info("\nFalse positive filters enabled:")
    logger.info("  ✓ FastAPI/pytest decorators (@router.*, @app.*, @pytest.*)")
    logger.info("  ✓ Dictionary-registered functions")
    logger.info("  ✓ Template/archive/deprecated directories")
    logger.info("  ✓ Docstring examples")
    logger.info("  ✓ Known entry points")
    
    # Get all Python files
    py_files = find_python_files(root, include_tests)
    logger.info(f"\nFiles to scan: {len(py_files)}")
    
    # Build complete codebase content for call checking
    logger.info("Building codebase index...")
    all_content = ""
    for f in py_files:
        try:
            all_content += f.read_text(encoding='utf-8', errors='ignore') + "\n"
        except Exception:
            pass
    
    # Analyze each file
    logger.info("Scanning for truly uncalled functions...")
    
    if verbose:
        logger.info("\n--- Verbose Output ---")
    
    all_uncalled: list[FunctionInfo] = []
    
    for filepath in py_files:
        uncalled = analyze_file(filepath, all_content, include_private, verbose)
        all_uncalled.extend(uncalled)
    
    # Group by file for output
    by_file: dict[Path, list[FunctionInfo]] = defaultdict(list)
    for func_info in all_uncalled:
        by_file[func_info.filepath].append(func_info)
    
    logger.info(f"\n{'='*70}")
    logger.info("TRULY UNCALLED PARAMETERLESS FUNCTIONS")
    logger.info(f"{'='*70}")
    
    if not by_file:
        logger.info("\n✅ No truly uncalled parameterless functions found!")
        logger.info("   All detected functions are either:")
        logger.info("   - Called/referenced somewhere in the codebase")
        logger.info("   - Framework-invoked (decorators)")
        logger.info("   - Registered in dictionaries")
        logger.info("   - In template/archive directories")
    else:
        for filepath in sorted(by_file.keys()):
            rel_path = filepath.relative_to(root)
            logger.info(f"\n📁 {rel_path}")
            logger.info("-" * 50)
            for func_info in sorted(by_file[filepath], key=lambda x: x.line_num):
                logger.info(f"  Line {func_info.line_num:4d}: def {func_info.name}()")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"SUMMARY: {len(all_uncalled)} truly uncalled functions")
    logger.info(f"         {len(by_file)} files affected")
    logger.info(f"{'='*70}")
    
    if all_uncalled:
        logger.info("\nRecommended actions:")
        logger.info("  1. Wire to lifecycle (startup/shutdown) if cleanup function")
        logger.info("  2. Delete if truly dead code")
        logger.info("  3. Add API endpoint if utility function")
        logger.info("  4. Add to ENTRY_POINTS if legitimate entry point")
        logger.info("\nRun with --verbose to see why other functions were filtered out.")


if __name__ == "__main__":
    main()
