#!/usr/bin/env python3
"""
export_repo_indexes.py - Enhanced (No FastAPI dependency)
Generates comprehensive repo index files for LLM context.
Works with distributed API architectures (memory APIs, agent routers, VPS-facing, local-dev).
"""

import os
import structlog
import sys
import re
import ast
import fnmatch
from collections import defaultdict

# Configuration

logger = structlog.get_logger(__name__)
REPO_DIR = "/Users/ib-mac/Projects/L9"
REPO_INDEX_DIR = "/Users/ib-mac/Projects/L9/readme/repo-index"
DROPBOX_EXPORT_DIR = "/Users/ib-mac/Dropbox/Repo_Dropbox_IB/L9-index-export"

# Directories to skip
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".cursor",
    ".dora",
    ".secrets",
    "l9/venv",
    "secrets",
    ".DS_Store",
    "node_modules",
    ".pytest_cache",
}


def load_gitignore_patterns():
    """Load and parse .gitignore patterns."""
    gitignore_path = os.path.join(REPO_DIR, ".gitignore")
    patterns = []

    if not os.path.exists(gitignore_path):
        return patterns

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Skip negation patterns for now (we're just filtering out)
                if line.startswith("!"):
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
        if pattern.endswith("/"):
            pattern_dir = pattern.rstrip("/")
            # Match directory name or any parent directory
            if is_dir and (
                fnmatch.fnmatch(basename, pattern_dir)
                or fnmatch.fnmatch(rel_path, pattern_dir)
                or any(fnmatch.fnmatch(part, pattern_dir) for part in path_parts)
            ):
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
            is_last = i == len(dirs) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{d}/")

            extension = "    " if is_last else "│   "
            new_rel_prefix = os.path.join(rel_path_prefix, d) if rel_path_prefix else d
            walk_dir(
                os.path.join(path, d),
                prefix + extension,
                max_depth,
                current_depth + 1,
                new_rel_prefix,
            )

    lines.append("L9/")
    walk_dir(REPO_DIR, "", max_depth=3, current_depth=0, rel_path_prefix="")
    return "\n".join(lines)


def generate_api_surfaces():
    """Map all callable interfaces across different API surface types."""
    api_surfaces = defaultdict(list)

    # Find all routers, classes with __call__, and async functions that look like handlers
    router_pattern = re.compile(r"(\w+)\s*=\s*(?:APIRouter|Router)\(")
    callable_pattern = re.compile(r"(?:def|async def)\s+(\w+)\s*\(")

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
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                            # Find routers/interfaces
                            routers = router_pattern.findall(content)
                            if routers:
                                rel_path = os.path.relpath(fpath, REPO_DIR)
                                for router in routers:
                                    api_surfaces[surface_name].append(
                                        f"  {rel_path}::{router}"
                                    )

                            # Find callables (handlers)
                            callables = callable_pattern.findall(content)
                            if callables and (
                                "handler" in fname or "interface" in fname
                            ):
                                rel_path = os.path.relpath(fpath, REPO_DIR)
                                for callable_name in callables[:3]:  # Limit per file
                                    api_surfaces[surface_name].append(
                                        f"  {rel_path}::{callable_name}()"
                                    )
                    except Exception:
                        pass

    if api_surfaces:
        lines = []
        for surface_type in ["api", "agents", "services", "memory", "orchestration"]:
            if surface_type in api_surfaces:
                lines.append(f"\n# {surface_type.upper()} Surface:")
                lines.extend(
                    sorted(set(api_surfaces[surface_type]))[:20]
                )  # Top 20 per surface
        return "\n".join(lines)

    return "No API surfaces found."


def generate_entrypoints():
    """Identify app entrypoints with useful metadata."""
    entrypoints = []
    gitignore_patterns = load_gitignore_patterns()

    # Patterns to find entry points
    fastapi_pattern = re.compile(
        r'app\s*=\s*FastAPI\s*\([^)]*title\s*=\s*["\']([^"\']+)["\']', re.DOTALL
    )
    uvicorn_pattern = re.compile(r"uvicorn\.run\s*\([^)]*\)", re.DOTALL)
    main_block_pattern = re.compile(r'if\s+__name__\s*==\s*["\']__main__["\']\s*:')

    for root, dirs, files in os.walk(REPO_DIR):
        # Filter dirs using gitignore
        dirs[:] = [
            d
            for d in dirs
            if d not in SKIP_DIRS
            and not is_ignored(
                os.path.relpath(os.path.join(root, d), REPO_DIR),
                gitignore_patterns,
                is_dir=True,
            )
        ]

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
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
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
                    if re.search(r"\bapp\s*=\s*FastAPI\s*\(", content):
                        entry_info["type"] = "FastAPI"
                        fastapi_match = fastapi_pattern.search(content)
                        if fastapi_match:
                            entry_info["title"] = fastapi_match.group(1)

                        # Extract routes (look for @app. or @router. decorators)
                        route_pattern = re.compile(
                            r'@(?:app|router)\.(get|post|put|delete|patch|websocket|options|head)\s*\(["\']([^"\']+)["\']'
                        )
                        routes = route_pattern.findall(content)
                        entry_info["routes"] = [
                            f"{method.upper()} {path}" for method, path in routes[:15]
                        ]

                        # Extract router includes
                        include_pattern = re.compile(
                            r'\.include_router\s*\([^,]+,\s*prefix\s*=\s*["\']([^"\']+)["\']'
                        )
                        includes = include_pattern.findall(content)
                        if includes:
                            entry_info["routes"].extend(
                                [f"ROUTER {prefix}/*" for prefix in includes[:5]]
                            )

                    # Check for uvicorn.run
                    uvicorn_match = uvicorn_pattern.search(content)
                    if uvicorn_match:
                        # Extract host and port
                        host_match = re.search(
                            r'host\s*=\s*["\']([^"\']+)["\']', content
                        )
                        port_match = re.search(r"port\s*=\s*(\d+)", content)
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
                            for route in entry_info["routes"][
                                :10
                            ]:  # Show first 10 routes
                                lines.append(f"    - {route}")
                            if len(entry_info["routes"]) > 10:
                                lines.append(
                                    f"    ... and {len(entry_info['routes']) - 10} more"
                                )

                        if entry_info["has_main"] and entry_info["type"] != "FastAPI":
                            lines.append("  Has __main__ block: Yes")

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

    getenv_pattern = re.compile(
        r'os\.(?:getenv|environ)\.get\(["\']([A-Za-z_][A-Za-z0-9_]*)["\']'
    )
    environ_pattern = re.compile(r'os\.environ\[["\']([A-Za-z_][A-Za-z0-9_]*)["\']')
    dotenv_pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=", re.MULTILINE)

    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        env_vars.update(getenv_pattern.findall(content))
                        env_vars.update(environ_pattern.findall(content))
                except Exception:
                    pass

            elif fname.startswith(".env"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
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

    import_pattern = re.compile(r"^(?:import|from)\s+([\w\.]+)", re.MULTILINE)

    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        matches = import_pattern.findall(content)
                        for match in matches:
                            top_level = match.split(".")[0]
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
            with open(req_file, "r") as f:
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
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        tree = ast.parse(f.read())
                        rel_path = os.path.relpath(fpath, REPO_DIR)

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                docstring = ast.get_docstring(node) or "No docstring"
                                docstring = docstring.split("\n")[0][
                                    :60
                                ]  # First line, 60 chars
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
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        tree = ast.parse(f.read())
                        rel_path = os.path.relpath(fpath, REPO_DIR)

                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                args = [arg.arg for arg in node.args.args]
                                signature = f"{node.name}({', '.join(args)})"
                                docstring = ast.get_docstring(node) or ""
                                docstring = (
                                    docstring.split("\n")[0][:40] if docstring else ""
                                )
                                functions.append(
                                    f"{rel_path}::{signature} - {docstring}"
                                )
                except Exception:
                    pass

    if functions:
        return "\n".join(sorted(functions[:200]))  # Limit to top 200
    return "No functions found."


def generate_config_files():
    """List all configuration files."""
    config_patterns = [
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".ini",
        ".cfg",
        "Dockerfile",
        "docker-compose",
    ]
    config_files = []

    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            if any(
                fname.endswith(ext) or fname.startswith(ext) for ext in config_patterns
            ):
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
                with open(init_file, "r", encoding="utf-8", errors="ignore") as f:
                    docstring = f.read(500)  # First 500 chars
                    docstring = (
                        docstring.split('"""')[1]
                        if '"""' in docstring
                        else "No module docstring"
                    )
                    docstring = docstring.split("\n")[0][:60]
                    architecture.append(f"{rel_path}/ - {docstring}")
            except Exception:
                pass

    if architecture:
        return "\n".join(sorted(architecture))
    return "No module architecture found."


# =============================================================================
# NEW: Wiring & Architecture Index Generators
# =============================================================================


def generate_wiring_map():
    """Generate high-level wiring/execution spine map."""
    lines = [
        "# L9 Wiring Map",
        "# ==============",
        "# How components connect: Entrypoint → Orchestration → Memory → Persistence",
        "",
        "## EXECUTION SPINE",
        "",
        "```",
        "uvicorn api.server:app",
        "    │",
        "    ▼",
        "┌─────────────────────────────────────────────────────────┐",
        "│  api/server.py (FastAPI)                                │",
        "│                                                         │",
        "│  lifespan():                                           │",
        "│    1. run_migrations()  → migrations/*.sql             │",
        "│    2. init_service()    → memory substrate (Postgres)  │",
        "│    3. get_neo4j_client() → Neo4j graph DB              │",
        "│    4. get_redis_client() → Redis cache/queues          │",
        "└─────────────────────────────────────────────────────────┘",
        "    │",
        "    ▼ Routers mounted",
        "┌─────────────────────────────────────────────────────────┐",
        "│  ROUTERS                                                │",
        "│                                                         │",
        "│  /os/*        → api/os_routes.py         (health)      │",
        "│  /agent/*     → api/agent_routes.py      (tasks)       │",
        "│  /memory/*    → api/memory/router.py     (packets)     │",
        "│  /world-model/* → api/world_model_api.py (entities)    │",
        "│  /ws/agent    → WebSocket handler        (real-time)   │",
        "└─────────────────────────────────────────────────────────┘",
        "    │",
        "    ▼ WebSocket path",
        "┌─────────────────────────────────────────────────────────┐",
        "│  WEBSOCKET LAYER                                        │",
        "│                                                         │",
        "│  1. Handshake → ws_orchestrator.register()             │",
        "│  2. Message loop:                                       │",
        "│     └→ ingest_packet() → Memory DAG                    │",
        "│     └→ orchestrators/ws_bridge.py → TaskEnvelope       │",
        "│                                                         │",
        "│  runtime/websocket_orchestrator.py (connection mgmt)   │",
        "└─────────────────────────────────────────────────────────┘",
        "    │",
        "    ▼ Packet ingestion",
        "┌─────────────────────────────────────────────────────────┐",
        "│  MEMORY SUBSYSTEM                                       │",
        "│                                                         │",
        "│  memory/ingestion.py::ingest_packet()                  │",
        "│       ▼                                                 │",
        "│  memory/substrate_graph.py::SubstrateDAG.run()         │",
        "│       │                                                 │",
        "│       ├→ intake_node                                   │",
        "│       ├→ reasoning_node                                │",
        "│       ├→ memory_write_node                             │",
        "│       ├→ semantic_embed_node                           │",
        "│       ├→ extract_insights_node                         │",
        "│       ├→ store_insights_node                           │",
        "│       ├→ world_model_trigger_node                      │",
        "│       └→ checkpoint_node                               │",
        "└─────────────────────────────────────────────────────────┘",
        "    │",
        "    ▼ DB writes",
        "┌─────────────────────────────────────────────────────────┐",
        "│  PERSISTENCE LAYER                                      │",
        "│                                                         │",
        "│  PostgreSQL + pgvector (l9-postgres:5432)              │",
        "│    ├─ packet_store          (all packets)              │",
        "│    ├─ agent_memory_events   (agent activity)           │",
        "│    ├─ reasoning_traces      (structured reasoning)     │",
        "│    ├─ semantic_memory       (vector embeddings)        │",
        "│    ├─ knowledge_facts       (extracted facts)          │",
        "│    └─ tasks                 (task queue persistence)   │",
        "│                                                         │",
        "│  Neo4j Graph DB (l9-neo4j:7687)                        │",
        "│    ├─ Entity nodes          (users, agents, events)    │",
        "│    ├─ Relationship edges    (causality, ownership)     │",
        "│    ├─ Event timeline        (temporal chains)          │",
        "│    └─ Tool registry         (registered tools graph)   │",
        "│                                                         │",
        "│  Redis (redis:6379)                                    │",
        "│    ├─ Task queue backend    (priority sorted sets)     │",
        "│    ├─ Rate limiting         (sliding window counters)  │",
        "│    └─ Session/context cache (ephemeral state)          │",
        "└─────────────────────────────────────────────────────────┘",
        "```",
        "",
        "## KEY SINGLETONS",
        "",
        "| Singleton | Module | Purpose |",
        "|-----------|--------|---------|",
        "| ws_orchestrator | runtime.websocket_orchestrator | WebSocket connection manager |",
        "| _service | memory.substrate_service | Memory substrate singleton |",
        "| _repository | memory.substrate_repository | PostgreSQL connection pool |",
        "| _world_model_engine | world_model.engine | World model singleton |",
        "| _neo4j_client | memory.graph_client | Neo4j graph client |",
        "| _redis_client | runtime.redis_client | Redis cache/queue client |",
        "",
        "## GRACEFUL DEGRADATION",
        "",
        "| Service | If Unavailable | Fallback |",
        "|---------|----------------|----------|",
        "| Neo4j | Graph features disabled | No tool registry, no permission graph |",
        "| Redis | In-memory fallback | TaskQueue uses deque, local rate limiting |",
        "| PostgreSQL | FATAL | System cannot start |",
    ]
    return "\n".join(lines)


def generate_agent_catalog():
    """Generate catalog of all agents with roles and capabilities."""
    lines = [
        "# L9 Agent Catalog",
        "# =================",
        "# All agents with their roles, models, and tool bindings.",
        "",
    ]

    # Parse agents/ directory
    agents_dir = os.path.join(REPO_DIR, "agents")
    if os.path.isdir(agents_dir):
        lines.append("## Core Agents (agents/)")
        lines.append("")
        for fname in sorted(os.listdir(agents_dir)):
            if fname.endswith(".py") and not fname.startswith("__"):
                fpath = os.path.join(agents_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2000)
                        # Extract class name and docstring
                        class_match = re.search(
                            r'class\s+(\w+).*?(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
                            content,
                            re.DOTALL,
                        )
                        if class_match:
                            class_name = class_match.group(1)
                            docstring = (
                                class_match.group(2) or class_match.group(3) or ""
                            ).strip()
                            docstring = (
                                docstring.split("\n")[0][:80]
                                if docstring
                                else "No docstring"
                            )
                            lines.append(f"- **{class_name}** (`{fname}`)")
                            lines.append(f"  - {docstring}")
                            lines.append("")
                except Exception:
                    pass

    # Parse config/agents/ YAML files
    config_agents_dir = os.path.join(REPO_DIR, "config", "agents")
    if os.path.isdir(config_agents_dir):
        lines.append("")
        lines.append("## Configured Agents (config/agents/)")
        lines.append("")
        for fname in sorted(os.listdir(config_agents_dir)):
            if fname.endswith((".yaml", ".yml")):
                fpath = os.path.join(config_agents_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        import yaml

                        data = yaml.safe_load(f)
                        if data:
                            agent_id = data.get("agent_id") or data.get("id", fname)
                            name = data.get("name", agent_id)
                            model = data.get("model", "gpt-4o")
                            tools = data.get("tools", [])
                            tool_count = len(tools)
                            lines.append(f"- **{name}** (id: `{agent_id}`)")
                            lines.append(f"  - Model: {model}")
                            lines.append(f"  - Tools: {tool_count}")
                            if tools and isinstance(tools[0], (str, dict)):
                                tool_names = [
                                    t
                                    if isinstance(t, str)
                                    else t.get("tool_id", t.get("id", "?"))
                                    for t in tools[:5]
                                ]
                                lines.append(f"  - Tool IDs: {', '.join(tool_names)}")
                            lines.append("")
                except Exception:
                    pass

    # Parse orchestrators/README.md for agent coordination patterns
    lines.append("")
    lines.append("## Agent Layers")
    lines.append("")
    lines.append("```")
    lines.append("                    ┌─────────────┐")
    lines.append("                    │   IGOR      │  (Human authority)")
    lines.append("                    └──────┬──────┘")
    lines.append("                           │ escalation")
    lines.append("                    ┌──────▼──────┐")
    lines.append("                    │   L (CTO)   │  (AI OS core agent)")
    lines.append("                    └──────┬──────┘")
    lines.append("            ┌──────────────┼──────────────┐")
    lines.append("            ▼              ▼              ▼")
    lines.append("     ┌────────────┐ ┌────────────┐ ┌────────────┐")
    lines.append("     │ Research   │ │ Architect  │ │ Coder      │")
    lines.append("     │ Agents     │ │ Agents     │ │ Agents     │")
    lines.append("     └────────────┘ └────────────┘ └────────────┘")
    lines.append("            │              │              │")
    lines.append("            ▼              ▼              ▼")
    lines.append("     ┌────────────┐ ┌────────────┐ ┌────────────┐")
    lines.append("     │ Mac Agent  │ │ QA Agent   │ │ Reflection │")
    lines.append("     │            │ │            │ │ Agent      │")
    lines.append("     └────────────┘ └────────────┘ └────────────┘")
    lines.append("```")
    lines.append("")
    lines.append("## Authority Hierarchy")
    lines.append("")
    lines.append("Igor > L (CTO) > Research agents > Mac agent")
    lines.append("")
    lines.append("High-risk operations require Igor approval before execution.")

    return "\n".join(lines)


def generate_kernel_catalog():
    """Generate catalog of the 10 governance kernels."""
    lines = [
        "# L9 Kernel Catalog",
        "# ==================",
        "# 10 governance/identity/behavior kernels that define L's identity and constraints.",
        "",
        "## Kernel Stack (private/kernels/00_system/)",
        "",
    ]

    kernel_dir = os.path.join(REPO_DIR, "private", "kernels", "00_system")
    if os.path.isdir(kernel_dir):
        for fname in sorted(os.listdir(kernel_dir)):
            if fname.endswith((".yaml", ".yml")) and not fname.startswith("_"):
                fpath = os.path.join(kernel_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        import yaml

                        data = yaml.safe_load(f)
                        if data:
                            kernel_id = data.get(
                                "kernel_id", fname.replace(".yaml", "")
                            )
                            name = data.get("name", kernel_id)
                            version = data.get("version", "1.0")
                            purpose = data.get("purpose", data.get("description", ""))
                            if isinstance(purpose, str):
                                purpose = purpose.split("\n")[0][:100]
                            lines.append(f"### {fname}")
                            lines.append(f"- **ID**: {kernel_id}")
                            lines.append(f"- **Name**: {name}")
                            lines.append(f"- **Version**: {version}")
                            lines.append(f"- **Purpose**: {purpose}")
                            lines.append("")
                except Exception:
                    pass

    lines.append("")
    lines.append("## Kernel Wiring Functions (core/kernel_wiring/)")
    lines.append("")
    lines.append("| Function | Source File | Purpose |")
    lines.append("|----------|-------------|---------|")

    wiring_functions = [
        ("get_active_mode()", "master_wiring.py", "Get current system mode"),
        ("get_identity_profile()", "identity_wiring.py", "Get L's identity profile"),
        (
            "apply_identity_to_response()",
            "identity_wiring.py",
            "Apply identity to outputs",
        ),
        ("get_reasoning_mode()", "cognitive_wiring.py", "Get reasoning mode config"),
        (
            "should_enable_meta_cognition()",
            "cognitive_wiring.py",
            "Check meta-cognition flag",
        ),
        (
            "get_output_verbosity()",
            "behavioral_wiring.py",
            "Get output verbosity level",
        ),
        ("is_topic_blocked()", "behavioral_wiring.py", "Check if topic is blocked"),
        ("get_memory_layers_config()", "memory_wiring.py", "Get memory layer config"),
        ("should_checkpoint_now()", "memory_wiring.py", "Check checkpoint trigger"),
        ("get_worldmodel_schema()", "worldmodel_wiring.py", "Get world model schema"),
        ("get_execution_state_machine()", "execution_wiring.py", "Get execution FSM"),
        (
            "get_allowed_transitions()",
            "execution_wiring.py",
            "Get allowed state transitions",
        ),
        ("get_safety_policies()", "safety_wiring.py", "Get safety policies"),
        (
            "is_destructive_action()",
            "safety_wiring.py",
            "Check if action is destructive",
        ),
        ("get_dev_policies()", "developer_wiring.py", "Get developer policies"),
        (
            "get_packet_protocol()",
            "packet_protocol_wiring.py",
            "Get packet protocol config",
        ),
        (
            "get_allowed_event_types()",
            "packet_protocol_wiring.py",
            "Get allowed event types",
        ),
        ("get_default_channel()", "packet_protocol_wiring.py", "Get default channel"),
    ]

    for func, source, purpose in wiring_functions:
        lines.append(f"| `{func}` | {source} | {purpose} |")

    return "\n".join(lines)


def generate_tool_catalog():
    """Generate catalog of all tools with metadata."""
    lines = [
        "# L9 Tool Catalog",
        "# ================",
        "# All tools with category, scope, risk level, and approval requirements.",
        "",
        "## Tool Scopes",
        "",
        "| Scope | Description |",
        "|-------|-------------|",
        "| `internal` | L9-internal operations, no external calls |",
        "| `external` | Calls external APIs (GitHub, Notion, etc.) |",
        "| `requires_igor_approval` | High-risk, needs explicit Igor approval |",
        "",
        "## Risk Levels",
        "",
        "| Risk | Description |",
        "|------|-------------|",
        "| `low` | Read-only or safe operations |",
        "| `medium` | Write operations with rollback |",
        "| `high` | Destructive or irreversible operations |",
        "",
        "## L Agent Tools",
        "",
        "| Tool | Category | Scope | Risk | Approval Required |",
        "|------|----------|-------|------|-------------------|",
    ]

    # Parse tool definitions from tool_graph.py
    tool_graph_path = os.path.join(REPO_DIR, "core", "tools", "tool_graph.py")
    if os.path.exists(tool_graph_path):
        try:
            with open(tool_graph_path, "r", encoding="utf-8") as f:
                content = f.read()

                # Extract L_INTERNAL_TOOLS definitions
                tool_pattern = re.compile(
                    r"ToolDefinition\(\s*"
                    r'name="([^"]+)".*?'
                    r'(?:description="([^"]*)")?.*?'
                    r'(?:category="([^"]*)")?.*?'
                    r'(?:scope="([^"]*)")?.*?'
                    r'(?:risk_level="([^"]*)")?.*?'
                    r"(?:requires_igor_approval=(True|False))?",
                    re.DOTALL,
                )

                # Simpler approach: just extract the key info
                for match in re.finditer(
                    r"ToolDefinition\([^)]+\)", content, re.DOTALL
                ):
                    tool_def = match.group(0)
                    name = re.search(r'name="([^"]+)"', tool_def)
                    category = re.search(r'category="([^"]+)"', tool_def)
                    scope = re.search(r'scope="([^"]+)"', tool_def)
                    risk = re.search(r'risk_level="([^"]+)"', tool_def)
                    approval = re.search(
                        r"requires_igor_approval=(True|False)", tool_def
                    )

                    if name:
                        lines.append(
                            f"| `{name.group(1)}` | "
                            f"{category.group(1) if category else 'general'} | "
                            f"{scope.group(1) if scope else 'internal'} | "
                            f"{risk.group(1) if risk else 'low'} | "
                            f"{'Yes' if approval and approval.group(1) == 'True' else 'No'} |"
                        )
        except Exception:
            pass

    lines.append("")
    lines.append("## External API Dependencies")
    lines.append("")
    lines.append("| API | Used By |")
    lines.append("|-----|---------|")
    lines.append("| OpenAI | LLM chat, embeddings |")
    lines.append("| PostgreSQL | Memory substrate, packet store |")
    lines.append("| Neo4j | Graph DB, tool registry |")
    lines.append("| Redis | Task queue, rate limiting |")
    lines.append("| Slack | Messaging, webhooks |")
    lines.append("| GitHub (MCP) | Issues, PRs |")
    lines.append("| Notion (MCP) | Pages, databases |")
    lines.append("| Vercel (MCP) | Deployments |")
    lines.append("| Perplexity | Research queries |")
    lines.append("| Firecrawl | Web scraping |")

    return "\n".join(lines)


def generate_orchestrator_catalog():
    """Generate catalog of all orchestrators."""
    lines = [
        "# L9 Orchestrator Catalog",
        "# ========================",
        "# Agent coordination patterns for the L9 platform.",
        "",
        "## Orchestrator Pattern",
        "",
        "Each orchestrator follows a consistent structure:",
        "```",
        "<orchestrator>/",
        "├── __init__.py       # Module exports",
        "├── interface.py      # Abstract interface / protocol",
        "├── orchestrator.py   # Main orchestrator implementation",
        "└── *.py              # Additional components",
        "```",
        "",
        "## Available Orchestrators",
        "",
    ]

    orchestrators = [
        ("action_tool", "Tool execution with validation and error handling"),
        ("evolution", "Self-improvement via feedback loops and pattern adaptation"),
        ("memory", "Memory housekeeping, garbage collection, and optimization"),
        ("meta", "Meta-reasoning for strategy selection and reflection"),
        ("reasoning", "Inference chain coordination with confidence tracking"),
        ("research_swarm", "Multi-agent research with convergence and synthesis"),
        ("world_model", "World model updates, scheduling, and causal inference"),
    ]

    for name, description in orchestrators:
        orch_dir = os.path.join(REPO_DIR, "orchestrators", name)
        if os.path.isdir(orch_dir):
            files = [
                f
                for f in os.listdir(orch_dir)
                if f.endswith(".py") and not f.startswith("__")
            ]
            lines.append(f"### {name}/")
            lines.append(f"**Purpose:** {description}")
            lines.append(f"**Files:** {', '.join(files)}")
            lines.append("")

    lines.append("")
    lines.append("## Orchestration Layer (orchestration/)")
    lines.append("")

    orch_files = [
        ("unified_controller.py", "Central orchestration controller"),
        ("task_router.py", "HTTP task routing"),
        ("slack_task_router.py", "Slack-specific task routing"),
        ("ws_task_router.py", "WebSocket task routing"),
        ("plan_executor.py", "Plan execution engine"),
        ("long_plan_graph.py", "Long-running plan DAG"),
        ("cell_orchestrator.py", "Collaborative cell orchestration"),
        ("orchestrator_kernel.py", "Orchestrator kernel interface"),
    ]

    for fname, desc in orch_files:
        fpath = os.path.join(REPO_DIR, "orchestration", fname)
        if os.path.exists(fpath):
            lines.append(f"- `{fname}` - {desc}")

    lines.append("")
    lines.append("## Interface Contract")
    lines.append("")
    lines.append("All orchestrators implement:")
    lines.append("```python")
    lines.append("class OrchestratorInterface(Protocol):")
    lines.append("    async def run(self, context: Any) -> Any: ...")
    lines.append("    async def health_check(self) -> dict: ...")
    lines.append("```")

    return "\n".join(lines)


def generate_event_types():
    """Generate catalog of event types and packet kinds."""
    lines = [
        "# L9 Event Types",
        "# ===============",
        "# PacketEnvelope kinds, event types, and schema information.",
        "",
        "## PacketKind Enum",
        "",
        "| Kind | Description |",
        "|------|-------------|",
        "| `EVENT` | General event |",
        "| `INSIGHT` | Extracted insight |",
        "| `RESULT` | Execution result |",
        "| `ERROR` | Error event |",
        "| `COMMAND` | Command packet |",
        "| `QUERY` | Query packet |",
        "",
        "## PacketEnvelope Schema",
        "",
        "```",
        "PacketEnvelope:",
        "  packet_id: UUID           # Unique identifier",
        "  packet_type: str          # Type of packet",
        "  kind: PacketKind          # Classification",
        "  payload: dict             # Arbitrary JSON payload",
        "  timestamp: datetime       # Creation timestamp",
        "  metadata: PacketMetadata  # Schema version, agent, domain",
        "  confidence: PacketConfidence  # Score 0-1, rationale",
        "  provenance: PacketProvenance  # Parent packet, source agent",
        "```",
        "",
        "## Memory DAG Pipeline Events",
        "",
        "| Stage | Event | Description |",
        "|-------|-------|-------------|",
        "| 1 | `intake` | Packet received and validated |",
        "| 2 | `reasoning` | Reasoning trace extracted |",
        "| 3 | `memory_write` | Packet written to store |",
        "| 4 | `semantic_embed` | Vector embedding generated |",
        "| 5 | `extract_insights` | Insights extracted |",
        "| 6 | `store_insights` | Insights stored |",
        "| 7 | `world_model_trigger` | World model update triggered |",
        "| 8 | `checkpoint` | DAG state checkpointed |",
        "",
        "## WebSocket Event Types",
        "",
        "| Event | Direction | Description |",
        "|-------|-----------|-------------|",
        "| `handshake` | Client → Server | Agent registration |",
        "| `task_request` | Client → Server | Task submission |",
        "| `task_result` | Server → Client | Task completion |",
        "| `error` | Server → Client | Error notification |",
        "| `ping` | Bidirectional | Keepalive |",
        "",
        "## Slack Event Types",
        "",
        "| Event | Handler | Description |",
        "|-------|---------|-------------|",
        "| `message` | webhook_slack.py | Slack message received |",
        "| `app_mention` | webhook_slack.py | Bot mentioned |",
        "| `slash_command` | webhook_slack.py | Slash command invoked |",
    ]

    return "\n".join(lines)


def generate_singleton_registry():
    """Generate registry of key singleton instances."""
    lines = [
        "# L9 Singleton Registry",
        "# ======================",
        "# Key singleton instances and their modules.",
        "",
        "## Core Singletons",
        "",
        "| Singleton | Module | Purpose | Init |",
        "|-----------|--------|---------|------|",
        "| `ws_orchestrator` | runtime.websocket_orchestrator | WebSocket connection manager | Startup |",
        "| `_service` | memory.substrate_service | Memory substrate singleton | Lazy |",
        "| `_repository` | memory.substrate_repository | PostgreSQL connection pool | Lazy |",
        "| `_world_model_engine` | world_model.engine | World model singleton | Lazy |",
        "| `_neo4j_client` | memory.graph_client | Neo4j graph database client | Lazy |",
        "| `_redis_client` | runtime.redis_client | Redis cache/queue client | Lazy |",
        "",
        "## FastAPI State",
        "",
        "| Key | Module | Purpose |",
        "|-----|--------|---------|",
        "| `app.state.neo4j_client` | api.server | Neo4j client for request context |",
        "| `app.state.redis_client` | api.server | Redis client for request context |",
        "",
        "## Singleton Access Patterns",
        "",
        "### Memory Substrate",
        "```python",
        "from memory.substrate_service import get_service",
        "service = await get_service()",
        "```",
        "",
        "### Neo4j Client",
        "```python",
        "from memory.graph_client import get_neo4j_client",
        "client = await get_neo4j_client()  # Returns None if unavailable",
        "```",
        "",
        "### Redis Client",
        "```python",
        "from runtime.redis_client import get_redis_client",
        "client = await get_redis_client()  # Returns in-memory fallback if unavailable",
        "```",
        "",
        "### WebSocket Orchestrator",
        "```python",
        "from runtime.websocket_orchestrator import ws_orchestrator",
        "await ws_orchestrator.broadcast(message)",
        "```",
        "",
        "## Lifecycle",
        "",
        "1. **Startup** (`lifespan()` in api/server.py):",
        "   - `run_migrations()` - Apply SQL migrations",
        "   - `init_service()` - Initialize memory substrate",
        "   - `get_neo4j_client()` - Connect to Neo4j",
        "   - `get_redis_client()` - Connect to Redis",
        "",
        "2. **Shutdown** (`lifespan()` exit):",
        "   - `close_service()` - Close memory substrate",
        "   - `close_neo4j_client()` - Close Neo4j",
        "   - `close_redis_client()` - Close Redis",
    ]

    return "\n".join(lines)


def main():
    """Generate index files and export them."""

    if not os.path.isdir(REPO_DIR):
        logger.info(f"❌ Repo directory not found: {REPO_DIR}")
        sys.exit(1)

    logger.info(f"📁 Using repo: {REPO_DIR}")
    logger.info("📤 Export destinations:")
    logger.info(f"   - {REPO_INDEX_DIR}")
    logger.info(f"   - {DROPBOX_EXPORT_DIR}")

    try:
        os.makedirs(REPO_INDEX_DIR, exist_ok=True)
        os.makedirs(DROPBOX_EXPORT_DIR, exist_ok=True)
        logger.info("✅ Export directories ready")
    except Exception as e:
        logger.error(f"❌ Failed to create export directories: {e}")
        sys.exit(1)

    # Define generators - ORDER MATTERS for LLM context efficiency
    generators = {
        # Core architecture (load first for context)
        "wiring_map.txt": ("🔌 Wiring map (execution spine)", generate_wiring_map),
        "architecture.txt": ("🏗️  Module architecture", generate_module_architecture),
        "tree.txt": ("📊 Directory structure", generate_tree),
        # Agent/orchestration layer
        "agent_catalog.txt": ("🤖 Agent catalog", generate_agent_catalog),
        "kernel_catalog.txt": (
            "🧠 Kernel catalog (10 kernels)",
            generate_kernel_catalog,
        ),
        "orchestrator_catalog.txt": (
            "🎭 Orchestrator catalog",
            generate_orchestrator_catalog,
        ),
        "tool_catalog.txt": ("🔧 Tool catalog", generate_tool_catalog),
        # Events and schemas
        "event_types.txt": ("📨 Event types & packet kinds", generate_event_types),
        "singleton_registry.txt": (
            "📦 Singleton registry",
            generate_singleton_registry,
        ),
        # API and code structure
        "api_surfaces.txt": (
            "🌐 API surfaces (memory/agents/services)",
            generate_api_surfaces,
        ),
        "entrypoints.txt": ("🚀 Entry points", generate_entrypoints),
        "class_definitions.txt": (
            "📋 Classes & data models",
            generate_class_definitions,
        ),
        "function_signatures.txt": (
            "⚙️  Function signatures",
            generate_function_signatures,
        ),
        # Configuration and dependencies
        "config_files.txt": ("⚙️  Configuration files", generate_config_files),
        "dependencies.txt": ("📦 Dependencies", generate_dependencies),
        "env_refs.txt": ("🔐 Environment variables", generate_env_refs),
        "imports.txt": ("📚 Python imports", generate_imports),
    }

    logger.info("\n📝 Generating indexes...\n")

    results = {}
    for filename, (emoji_desc, generator) in generators.items():
        logger.info(f"  {emoji_desc}...", end=" ", flush=True)

        try:
            content = generator()

            # Write to repo index directory
            repo_file = os.path.join(REPO_INDEX_DIR, filename)
            with open(repo_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Write to Dropbox export directory
            dropbox_file = os.path.join(DROPBOX_EXPORT_DIR, filename)
            with open(dropbox_file, "w", encoding="utf-8") as f:
                f.write(content)

            size = len(content.encode("utf-8"))
            results[filename] = size
            logger.info(f"✅ ({size:,} bytes)")
        except Exception as e:
            logger.info(f"❌ {e}")
            results[filename] = 0

    logger.info("\n✨ Done! Files exported to:")
    logger.info(f"   📂 {REPO_INDEX_DIR}")
    logger.info(f"   ☁️  {DROPBOX_EXPORT_DIR}")
    logger.info("\n📋 Summary:")
    total_size = 0
    for filename, size in sorted(results.items()):
        status = "✅" if size > 0 else "⚠️"
        logger.info(f"   {status} {filename:30} {size:>12,} bytes")
        total_size += size

    logger.info(f"\n   📊 Total: {total_size:,} bytes")
    logger.info("\n💡 Load order for LLMs (most context-critical first):")
    logger.info("   1. wiring_map.txt - understand execution spine & data flow")
    logger.info("   2. architecture.txt - understand module purposes")
    logger.info("   3. agent_catalog.txt - understand agent layers & capabilities")
    logger.info("   4. kernel_catalog.txt - understand governance kernels")
    logger.info("   5. orchestrator_catalog.txt - understand orchestration patterns")
    logger.info("   6. tool_catalog.txt - understand tool capabilities & risks")
    logger.info("   7. event_types.txt - understand packet/event schemas")
    logger.info("   8. api_surfaces.txt - understand API endpoints")
    logger.info("   9. tree.txt - understand directory structure")
    logger.info("   10. class_definitions.txt - understand data models")


if __name__ == "__main__":
    main()
