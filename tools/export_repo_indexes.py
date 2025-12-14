#!/usr/bin/env python3
"""
export_repo_indexes.py - Enhanced (No FastAPI dependency)
Generates comprehensive repo index files for LLM context.
Works with distributed API architectures (memory APIs, agent routers, VPS-facing, local-dev).
"""

import os
import shutil
import json
import subprocess
import sys
import re
import ast
import fnmatch
from pathlib import Path
from collections import defaultdict

# Configuration
REPO_DIR = "/Users/ib-mac/Projects/L9"
EXPORT_DIR = "/Users/ib-mac/Dropbox/Repo_Dropbox_IB/L9-index-export"

# Directories to skip
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".cursor", ".dora", ".secrets", 
             "l9/venv", "secrets", ".DS_Store", "node_modules", ".pytest_cache"}


def load_gitignore_patterns():
    """Load and parse .gitignore patterns."""
    gitignore_path = os.path.join(REPO_DIR, ".gitignore")
    patterns = []
    
    if not os.path.exists(gitignore_path):
        return patterns
    
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Skip negation patterns for now (we're just filtering out)
                if line.startswith('!'):
                    continue
                patterns.append(line)
    except Exception:
        pass
    
    return patterns


def is_ignored(rel_path, patterns, is_dir=False):
    """
    Check if a path matches any gitignore pattern.
    
    Args:
        rel_path: Relative path from repo root (e.g., ".env" or ".cursor-commands/")
        patterns: List of gitignore patterns
        is_dir: Whether the path is a directory
    
    Returns:
        True if the path should be ignored
    """
    # Check exact matches
    path_parts = rel_path.split(os.sep)
    basename = path_parts[-1] if path_parts else rel_path
    
    for pattern in patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern_dir = pattern.rstrip('/')
            # Match directory name or any parent directory
            if is_dir and (fnmatch.fnmatch(basename, pattern_dir) or 
                          fnmatch.fnmatch(rel_path, pattern_dir) or
                          any(fnmatch.fnmatch(part, pattern_dir) for part in path_parts)):
                return True
        else:
            # Match against basename or full path
            if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
            # Match against any path component
            if any(fnmatch.fnmatch(part, pattern) for part in path_parts):
                return True
    
    return False


def generate_tree():
    """Generate tree.txt using actual directory structure, respecting .gitignore."""
    lines = []
    gitignore_patterns = load_gitignore_patterns()
    
    def walk_dir(path, prefix="", max_depth=3, current_depth=0, rel_path_prefix=""):
        if current_depth >= max_depth:
            return
        
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return
        
        # Filter out entries that match gitignore or SKIP_DIRS
        filtered_entries = []
        for e in entries:
            if e in SKIP_DIRS:
                continue
            
            # Build relative path from repo root
            rel_path = os.path.join(rel_path_prefix, e) if rel_path_prefix else e
            
            # Check if ignored
            full_path = os.path.join(path, e)
            is_dir = os.path.isdir(full_path)
            
            if is_ignored(rel_path, gitignore_patterns, is_dir=is_dir):
                continue
            
            filtered_entries.append(e)
        
        dirs = [e for e in filtered_entries if os.path.isdir(os.path.join(path, e))]
        files = [e for e in filtered_entries if os.path.isfile(os.path.join(path, e))]
        
        for f in files[:10]:
            lines.append(f"{prefix}├── {f}")
        
        if len(files) > 10:
            lines.append(f"{prefix}├── ... ({len(files) - 10} more files)")
        
        for i, d in enumerate(dirs):
            is_last = (i == len(dirs) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{d}/")
            
            extension = "    " if is_last else "│   "
            new_rel_prefix = os.path.join(rel_path_prefix, d) if rel_path_prefix else d
            walk_dir(os.path.join(path, d), prefix + extension, max_depth, current_depth + 1, new_rel_prefix)
    
    lines.append("L9/")
    walk_dir(REPO_DIR, "", max_depth=3, current_depth=0, rel_path_prefix="")
    return "\n".join(lines)


def generate_api_surfaces():
    """Map all callable interfaces across different API surface types."""
    api_surfaces = defaultdict(list)
    
    # Find all routers, classes with __call__, and async functions that look like handlers
    router_pattern = re.compile(r'(\w+)\s*=\s*(?:APIRouter|Router)\(')
    callable_pattern = re.compile(r'(?:def|async def)\s+(\w+)\s*\(')
    
    surface_types = {
        "memory": os.path.join(REPO_DIR, "memory"),
        "agents": os.path.join(REPO_DIR, "agents"),
        "api": os.path.join(REPO_DIR, "api"),
        "services": os.path.join(REPO_DIR, "services"),
        "orchestration": os.path.join(REPO_DIR, "orchestration"),
    }
    
    for surface_name, search_path in surface_types.items():
        if not os.path.isdir(search_path):
            continue
        
        for root, dirs, files in os.walk(search_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            
            for fname in files:
                if fname.endswith(".py"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Find routers/interfaces
                            routers = router_pattern.findall(content)
                            if routers:
                                rel_path = os.path.relpath(fpath, REPO_DIR)
                                for router in routers:
                                    api_surfaces[surface_name].append(f"  {rel_path}::{router}")
                            
                            # Find callables (handlers)
                            callables = callable_pattern.findall(content)
                            if callables and ("handler" in fname or "interface" in fname):
                                rel_path = os.path.relpath(fpath, REPO_DIR)
                                for callable_name in callables[:3]:  # Limit per file
                                    api_surfaces[surface_name].append(f"  {rel_path}::{callable_name}()")
                    except Exception:
                        pass
    
    if api_surfaces:
        lines = []
        for surface_type in ["api", "agents", "services", "memory", "orchestration"]:
            if surface_type in api_surfaces:
                lines.append(f"\n# {surface_type.upper()} Surface:")
                lines.extend(sorted(set(api_surfaces[surface_type]))[:20])  # Top 20 per surface
        return "\n".join(lines)
    
    return "No API surfaces found."


def generate_entrypoints():
    """Identify app entrypoints with useful metadata."""
    entrypoints = []
    gitignore_patterns = load_gitignore_patterns()
    
    # Patterns to find entry points
    fastapi_pattern = re.compile(r'app\s*=\s*FastAPI\s*\([^)]*title\s*=\s*["\']([^"\']+)["\']', re.DOTALL)
    uvicorn_pattern = re.compile(r'uvicorn\.run\s*\([^)]*\)', re.DOTALL)
    main_block_pattern = re.compile(r'if\s+__name__\s*==\s*["\']__main__["\']\s*:')
    
    for root, dirs, files in os.walk(REPO_DIR):
        # Filter dirs using gitignore
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_ignored(
            os.path.relpath(os.path.join(root, d), REPO_DIR), 
            gitignore_patterns, 
            is_dir=True
        )]
        
        for fname in files:
            if not fname.endswith(".py"):
                continue
            
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, REPO_DIR)
            
            # Skip if ignored
            if is_ignored(rel_path, gitignore_patterns, is_dir=False):
                continue
            
            # Skip test files
            if "test" in fname.lower() or "tests" in root:
                continue
            
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    entry_info = {
                        "path": rel_path,
                        "type": None,
                        "title": None,
                        "port": None,
                        "host": None,
                        "has_main": False,
                        "routes": [],
                    }
                    
                    # Check for FastAPI app (must have "app = FastAPI" assignment)
                    if re.search(r'\bapp\s*=\s*FastAPI\s*\(', content):
                        entry_info["type"] = "FastAPI"
                        fastapi_match = fastapi_pattern.search(content)
                        if fastapi_match:
                            entry_info["title"] = fastapi_match.group(1)
                        
                        # Extract routes (look for @app. or @router. decorators)
                        route_pattern = re.compile(r'@(?:app|router)\.(get|post|put|delete|patch|websocket|options|head)\s*\(["\']([^"\']+)["\']')
                        routes = route_pattern.findall(content)
                        entry_info["routes"] = [f"{method.upper()} {path}" for method, path in routes[:15]]
                        
                        # Extract router includes
                        include_pattern = re.compile(r'\.include_router\s*\([^,]+,\s*prefix\s*=\s*["\']([^"\']+)["\']')
                        includes = include_pattern.findall(content)
                        if includes:
                            entry_info["routes"].extend([f"ROUTER {prefix}/*" for prefix in includes[:5]])
                    
                    # Check for uvicorn.run
                    uvicorn_match = uvicorn_pattern.search(content)
                    if uvicorn_match:
                        # Extract host and port
                        host_match = re.search(r'host\s*=\s*["\']([^"\']+)["\']', content)
                        port_match = re.search(r'port\s*=\s*(\d+)', content)
                        if host_match:
                            entry_info["host"] = host_match.group(1)
                        if port_match:
                            entry_info["port"] = port_match.group(1)
                        entry_info["type"] = entry_info["type"] or "Uvicorn"
                    
                    # Check for main block
                    if main_block_pattern.search(content):
                        entry_info["has_main"] = True
                        if not entry_info["type"]:
                            entry_info["type"] = "Script"
                    
                    # Only add if it's a real entry point
                    if entry_info["type"] or entry_info["has_main"]:
                        # Build description
                        lines = [f"{rel_path}"]
                        
                        if entry_info["type"]:
                            lines.append(f"  Type: {entry_info['type']}")
                        if entry_info["title"]:
                            lines.append(f"  Title: {entry_info['title']}")
                        if entry_info["host"] or entry_info["port"]:
                            addr = f"{entry_info['host'] or 'localhost'}:{entry_info['port'] or '8000'}"
                            lines.append(f"  Address: {addr}")
                        
                        if entry_info["routes"]:
                            lines.append(f"  Routes ({len(entry_info['routes'])}):")
                            for route in entry_info["routes"][:10]:  # Show first 10 routes
                                lines.append(f"    - {route}")
                            if len(entry_info["routes"]) > 10:
                                lines.append(f"    ... and {len(entry_info['routes']) - 10} more")
                        
                        if entry_info["has_main"] and entry_info["type"] != "FastAPI":
                            lines.append(f"  Has __main__ block: Yes")
                        
                        entrypoints.append("\n".join(lines))
                        
            except Exception:
                pass
    
    if entrypoints:
        lines = ["# Entry Points\n"]
        lines.extend(sorted(set(entrypoints)))
        return "\n".join(lines)
    return "No entrypoints found."


def generate_env_refs():
    """Extract environment variable references."""
    env_vars = set()
    
    getenv_pattern = re.compile(r'os\.(?:getenv|environ)\.get\(["\']([A-Za-z_][A-Za-z0-9_]*)["\']')
    environ_pattern = re.compile(r'os\.environ\[["\']([A-Za-z_][A-Za-z0-9_]*)["\']')
    dotenv_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)=', re.MULTILINE)
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        env_vars.update(getenv_pattern.findall(content))
                        env_vars.update(environ_pattern.findall(content))
                except Exception:
                    pass
            
            elif fname.startswith(".env"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        env_vars.update(dotenv_pattern.findall(content))
                except Exception:
                    pass
    
    if env_vars:
        return "\n".join(sorted(env_vars))
    return "No environment variables found."


def generate_imports():
    """Extract top-level Python imports from source code."""
    imports = defaultdict(set)
    
    import_pattern = re.compile(r'^(?:import|from)\s+([\w\.]+)', re.MULTILINE)
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = import_pattern.findall(content)
                        for match in matches:
                            top_level = match.split('.')[0]
                            imports[top_level].add(match)
                except Exception:
                    pass
    
    if imports:
        lines = []
        for top_level in sorted(imports.keys()):
            lines.append(f"# {top_level}")
            for imp in sorted(imports[top_level]):
                lines.append(f"  {imp}")
        return "\n".join(lines)
    return "No imports found."


def generate_dependencies():
    """Parse requirements.txt and show actual vs declared dependencies."""
    lines = ["# Dependencies from requirements.txt\n"]
    
    req_file = os.path.join(REPO_DIR, "requirements.txt")
    if os.path.exists(req_file):
        try:
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        lines.append(line)
        except Exception:
            pass
    
    return "\n".join(lines) if len(lines) > 1 else "No requirements.txt found."


def generate_class_definitions():
    """Extract class definitions with docstrings."""
    classes = []
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        tree = ast.parse(f.read())
                        rel_path = os.path.relpath(fpath, REPO_DIR)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                docstring = ast.get_docstring(node) or "No docstring"
                                docstring = docstring.split('\n')[0][:60]  # First line, 60 chars
                                classes.append(f"{rel_path}::{node.name} - {docstring}")
                except Exception:
                    pass
    
    if classes:
        return "\n".join(sorted(classes))
    return "No classes found."


def generate_function_signatures():
    """Extract function names and signatures."""
    functions = []
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        tree = ast.parse(f.read())
                        rel_path = os.path.relpath(fpath, REPO_DIR)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                args = [arg.arg for arg in node.args.args]
                                signature = f"{node.name}({', '.join(args)})"
                                docstring = ast.get_docstring(node) or ""
                                docstring = docstring.split('\n')[0][:40] if docstring else ""
                                functions.append(f"{rel_path}::{signature} - {docstring}")
                except Exception:
                    pass
    
    if functions:
        return "\n".join(sorted(functions[:200]))  # Limit to top 200
    return "No functions found."


def generate_config_files():
    """List all configuration files."""
    config_patterns = [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", "Dockerfile", "docker-compose"]
    config_files = []
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for fname in files:
            if any(fname.endswith(ext) or fname.startswith(ext) for ext in config_patterns):
                rel_path = os.path.relpath(os.path.join(root, fname), REPO_DIR)
                config_files.append(rel_path)
    
    if config_files:
        return "\n".join(sorted(set(config_files)))
    return "No config files found."


def generate_module_architecture():
    """Map module structure and purposes from __init__.py docstrings."""
    architecture = []
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        if "__init__.py" in files:
            rel_path = os.path.relpath(root, REPO_DIR)
            if rel_path == ".":
                continue
            
            init_file = os.path.join(root, "__init__.py")
            try:
                with open(init_file, 'r', encoding='utf-8', errors='ignore') as f:
                    docstring = f.read(500)  # First 500 chars
                    docstring = docstring.split('"""')[1] if '"""' in docstring else "No module docstring"
                    docstring = docstring.split('\n')[0][:60]
                    architecture.append(f"{rel_path}/ - {docstring}")
            except Exception:
                pass
    
    if architecture:
        return "\n".join(sorted(architecture))
    return "No module architecture found."


def main():
    """Generate index files and export them."""
    
    if not os.path.isdir(REPO_DIR):
        print(f"❌ Repo directory not found: {REPO_DIR}")
        sys.exit(1)
    
    print(f"📁 Using repo: {REPO_DIR}")
    print(f"📤 Export destination: {EXPORT_DIR}")
    
    try:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        print(f"✅ Export directory ready")
    except Exception as e:
        print(f"❌ Failed to create export directory: {e}")
        sys.exit(1)
    
    # Define generators - ORDER MATTERS for LLM context efficiency
    generators = {
        "tree.txt": ("📊 Directory structure", generate_tree),
        "architecture.txt": ("🏗️  Module architecture", generate_module_architecture),
        "api_surfaces.txt": ("🌐 API surfaces (memory/agents/services)", generate_api_surfaces),
        "entrypoints.txt": ("🚀 Entry points", generate_entrypoints),
        "dependencies.txt": ("📦 Dependencies", generate_dependencies),
        "class_definitions.txt": ("📋 Classes & data models", generate_class_definitions),
        "function_signatures.txt": ("⚙️  Function signatures", generate_function_signatures),
        "config_files.txt": ("⚙️  Configuration files", generate_config_files),
        "env_refs.txt": ("🔐 Environment variables", generate_env_refs),
        "imports.txt": ("📚 Python imports", generate_imports),
    }
    
    print("\n📝 Generating indexes...\n")
    
    results = {}
    for filename, (emoji_desc, generator) in generators.items():
        print(f"  {emoji_desc}...", end=" ", flush=True)
        
        try:
            content = generator()
            
            # Write to repo root
            repo_file = os.path.join(REPO_DIR, filename)
            with open(repo_file, "w", encoding='utf-8') as f:
                f.write(content)
            
            # Copy to export dir
            export_file = os.path.join(EXPORT_DIR, filename)
            shutil.copy(repo_file, export_file)
            
            size = len(content.encode('utf-8'))
            results[filename] = size
            print(f"✅ ({size:,} bytes)")
        except Exception as e:
            print(f"❌ {e}")
            results[filename] = 0
    
    print(f"\n✨ Done! Files exported to:")
    print(f"   {EXPORT_DIR}")
    print(f"\n📋 Summary:")
    total_size = 0
    for filename, size in sorted(results.items()):
        status = "✅" if size > 0 else "⚠️"
        print(f"   {status} {filename:30} {size:>12,} bytes")
        total_size += size
    
    print(f"\n   📊 Total: {total_size:,} bytes")
    print(f"\n💡 Load order for LLMs (most context-critical first):")
    print("   1. architecture.txt - understand module purposes")
    print("   2. api_surfaces.txt - understand API surfaces (memory/agents/services)")
    print("   3. tree.txt - understand structure")
    print("   4. class_definitions.txt - understand data models")
    print("   5. dependencies.txt - understand tech stack")


if __name__ == "__main__":
    main()
