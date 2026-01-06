#!/usr/bin/env python3
"""
Audit Orphan Classes: Find "Wired But Not Used" Code in L9

This script identifies classes, modules, and routes that are:
- WIRED: Successfully imported, registered, or referenced
- NOT USED: Have stub implementations, no callers, or working alternatives

Categories detected:
1. Stub adapters (v2.6 Module-Spec generated but not implemented)
2. Dead imports (imported but never called)
3. Orphan routes (registered but handlers are empty)
4. Duplicate implementations (same functionality in multiple places)
5. Feature-flagged dead code (flag=False permanently)

Usage:
    python scripts/audit_orphan_classes.py
    python scripts/audit_orphan_classes.py --json
    python scripts/audit_orphan_classes.py --fix-suggestions
"""

import ast
import os
import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import structlog

logger = structlog.get_logger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

REPO_ROOT = Path(__file__).parent.parent
SCAN_DIRS = ["api", "core", "memory", "orchestration", "runtime", "services"]
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "venv", ".venv", "tests"}
EXCLUDE_FILES = {"__init__.py"}

# Known stub patterns (from Module-Spec v2.6 generator)
STUB_PATTERNS = [
    r'return\s*\{\s*["\']status["\']\s*:\s*["\']processed["\']\s*\}',
    r'raise\s+NotImplementedError',
    r'pass\s*$',
    r'\.\.\.  # TODO',
    r'# STUB',
    r'# NOT IMPLEMENTED',
]

# Known feature flags that disable code
DISABLED_FLAGS = [
    "_has_slack_webhook_adapter",
    "_has_legacy_chat",
]

# Files that should never be flagged as orphan
PROTECTED_FILES = {
    "executor.py",
    "kernel_loader.py",
    "memory_substrate_service.py",
    "websocket_orchestrator.py",
    "docker-compose.yml",
}


# ══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class ClassInfo:
    """Information about a discovered class."""
    name: str
    file_path: str
    line_number: int
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    is_stub: bool = False
    stub_reason: Optional[str] = None
    has_callers: bool = True
    caller_count: int = 0


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    names: List[str]
    file_path: str
    line_number: int
    is_used: bool = True


@dataclass
class RouteInfo:
    """Information about a FastAPI route."""
    path: str
    method: str
    handler_name: str
    file_path: str
    line_number: int
    is_stub: bool = False
    stub_reason: Optional[str] = None


@dataclass
class OrphanReport:
    """Complete audit report."""
    stub_classes: List[ClassInfo] = field(default_factory=list)
    dead_imports: List[ImportInfo] = field(default_factory=list)
    orphan_routes: List[RouteInfo] = field(default_factory=list)
    duplicate_implementations: List[Dict] = field(default_factory=list)
    disabled_feature_flags: List[Dict] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════════════════
# AST VISITORS
# ══════════════════════════════════════════════════════════════════════════════


class ClassVisitor(ast.NodeVisitor):
    """Extract class definitions from Python AST."""

    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.classes: List[ClassInfo] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{self._get_full_attr(base)}")

        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        # Check if class is a stub (but not Exception/ABC classes - they're supposed to be minimal)
        is_exception = any(
            b in ["Exception", "BaseException", "Error", "ABC", "Protocol"] 
            or b.endswith("Error") 
            or b.endswith("Exception")
            or b.endswith("ABC")
            for b in base_classes
        )
        is_stub, stub_reason = (False, None) if is_exception else self._check_if_stub(node)

        class_info = ClassInfo(
            name=node.name,
            file_path=self.file_path,
            line_number=node.lineno,
            base_classes=base_classes,
            methods=methods,
            is_stub=is_stub,
            stub_reason=stub_reason,
        )
        self.classes.append(class_info)
        self.generic_visit(node)

    def _get_full_attr(self, node: ast.Attribute) -> str:
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_full_attr(node.value)}.{node.attr}"
        return node.attr

    def _check_if_stub(self, node: ast.ClassDef) -> Tuple[bool, Optional[str]]:
        """Check if a class is a stub implementation."""
        # Get source code for class body
        try:
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 50
            class_source = "\n".join(self.source_lines[start_line:end_line])
        except:
            return False, None

        for pattern in STUB_PATTERNS:
            if re.search(pattern, class_source):
                return True, f"Matches stub pattern: {pattern[:30]}..."

        # Check if all methods are pass/NotImplementedError
        stub_methods = 0
        total_methods = 0
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total_methods += 1
                body = item.body
                if len(body) == 1:
                    stmt = body[0]
                    if isinstance(stmt, ast.Pass):
                        stub_methods += 1
                    elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                        # Docstring only
                        stub_methods += 1
                    elif isinstance(stmt, ast.Raise):
                        stub_methods += 1

        if total_methods > 0 and stub_methods == total_methods:
            return True, f"All {total_methods} methods are stubs"

        return False, None


class ImportVisitor(ast.NodeVisitor):
    """Extract import statements from Python AST."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.imports: List[ImportInfo] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(ImportInfo(
                module=alias.name,
                names=[alias.asname or alias.name],
                file_path=self.file_path,
                line_number=node.lineno,
            ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.imports.append(ImportInfo(
            module=module,
            names=names,
            file_path=self.file_path,
            line_number=node.lineno,
        ))
        self.generic_visit(node)


class RouteVisitor(ast.NodeVisitor):
    """Extract FastAPI route definitions."""

    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.routes: List[RouteInfo] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._check_decorators(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._check_decorators(node)
        self.generic_visit(node)

    def _check_decorators(self, node):
        for decorator in node.decorator_list:
            route_info = self._parse_route_decorator(decorator, node)
            if route_info:
                self.routes.append(route_info)

    def _parse_route_decorator(self, decorator, func_node) -> Optional[RouteInfo]:
        """Parse @router.get/post/etc decorators."""
        if not isinstance(decorator, ast.Call):
            return None

        # Check if it's a route decorator
        if isinstance(decorator.func, ast.Attribute):
            method = decorator.func.attr
            if method not in ("get", "post", "put", "delete", "patch", "options", "head"):
                return None

            # Extract path from first argument
            path = "/"
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value

            # Check if handler is stub
            is_stub, stub_reason = self._check_handler_stub(func_node)

            return RouteInfo(
                path=path,
                method=method.upper(),
                handler_name=func_node.name,
                file_path=self.file_path,
                line_number=func_node.lineno,
                is_stub=is_stub,
                stub_reason=stub_reason,
            )
        return None

    def _check_handler_stub(self, node) -> Tuple[bool, Optional[str]]:
        """Check if route handler is a stub."""
        try:
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20
            func_source = "\n".join(self.source_lines[start_line:end_line])
        except:
            return False, None

        for pattern in STUB_PATTERNS:
            if re.search(pattern, func_source):
                return True, f"Matches stub pattern"

        return False, None


# ══════════════════════════════════════════════════════════════════════════════
# ANALYZERS
# ══════════════════════════════════════════════════════════════════════════════


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in scan directories."""
    files = []
    for scan_dir in SCAN_DIRS:
        dir_path = root / scan_dir
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob("*.py"):
            # Skip excluded directories
            if any(excl in py_file.parts for excl in EXCLUDE_DIRS):
                continue
            # Skip excluded files
            if py_file.name in EXCLUDE_FILES:
                continue
            files.append(py_file)
    return files


def analyze_file(file_path: Path) -> Tuple[List[ClassInfo], List[ImportInfo], List[RouteInfo]]:
    """Analyze a single Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        logger.warning("could_not_parse_file", file_path=str(file_path), error=str(e))
        return [], [], []

    rel_path = str(file_path.relative_to(REPO_ROOT))

    # Extract classes
    class_visitor = ClassVisitor(rel_path, source)
    class_visitor.visit(tree)

    # Extract imports
    import_visitor = ImportVisitor(rel_path)
    import_visitor.visit(tree)

    # Extract routes
    route_visitor = RouteVisitor(rel_path, source)
    route_visitor.visit(tree)

    return class_visitor.classes, import_visitor.imports, route_visitor.routes


def find_class_usages(all_classes: List[ClassInfo], all_files: List[Path]) -> Dict[str, int]:
    """Count how many times each class is referenced."""
    usage_counts: Dict[str, int] = defaultdict(int)

    class_names = {c.name for c in all_classes}

    for file_path in all_files:
        try:
            source = file_path.read_text(encoding="utf-8")
        except:
            continue

        for class_name in class_names:
            # Simple pattern: class name used as identifier
            pattern = rf'\b{re.escape(class_name)}\b'
            matches = re.findall(pattern, source)
            # Subtract 1 for the definition itself
            count = len(matches) - 1 if matches else 0
            usage_counts[class_name] += max(0, count)

    return usage_counts


def find_feature_flags(server_file: Path) -> List[Dict]:
    """Find disabled feature flags in server.py."""
    disabled = []
    try:
        source = server_file.read_text(encoding="utf-8")
        for flag in DISABLED_FLAGS:
            pattern = rf'{flag}\s*=\s*False'
            if re.search(pattern, source):
                disabled.append({
                    "flag": flag,
                    "file": str(server_file.relative_to(REPO_ROOT)),
                    "status": "disabled",
                })
    except:
        pass
    return disabled


def find_duplicate_classes(all_classes: List[ClassInfo]) -> List[Dict]:
    """Find classes with the same name in different files."""
    by_name: Dict[str, List[ClassInfo]] = defaultdict(list)
    for cls in all_classes:
        by_name[cls.name].append(cls)

    duplicates = []
    for name, classes in by_name.items():
        if len(classes) > 1:
            duplicates.append({
                "class_name": name,
                "count": len(classes),
                "locations": [{"file": c.file_path, "line": c.line_number} for c in classes],
            })

    return duplicates


# ══════════════════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ══════════════════════════════════════════════════════════════════════════════


def generate_report(
    all_classes: List[ClassInfo],
    all_imports: List[ImportInfo],
    all_routes: List[RouteInfo],
    usage_counts: Dict[str, int],
    disabled_flags: List[Dict],
    duplicates: List[Dict],
) -> OrphanReport:
    """Generate the complete orphan report."""

    # Find stub classes
    stub_classes = [c for c in all_classes if c.is_stub]

    # Find classes with no callers (excluding self-reference)
    for cls in all_classes:
        cls.caller_count = usage_counts.get(cls.name, 0)
        cls.has_callers = cls.caller_count > 0

    orphan_classes = [c for c in all_classes if not c.has_callers and not c.is_stub]

    # Find stub routes
    stub_routes = [r for r in all_routes if r.is_stub]

    # Generate summary
    summary = {
        "total_classes": len(all_classes),
        "stub_classes": len(stub_classes),
        "orphan_classes": len(orphan_classes),
        "total_routes": len(all_routes),
        "stub_routes": len(stub_routes),
        "disabled_flags": len(disabled_flags),
        "duplicate_classes": len(duplicates),
    }

    return OrphanReport(
        stub_classes=stub_classes,
        dead_imports=[],  # TODO: Implement dead import detection
        orphan_routes=stub_routes,
        duplicate_implementations=duplicates,
        disabled_feature_flags=disabled_flags,
        summary=summary,
    )


def print_report(report: OrphanReport, show_suggestions: bool = False):
    """Print human-readable report."""
    logger.info("\n" + "═" * 80)
    logger.info("  L9 ORPHAN CLASS AUDIT REPORT")
    logger.info("═" * 80 + "\n")

    # Summary
    logger.info("📊 SUMMARY")
    logger.info("-" * 40)
    for key, value in report.summary.items():
        logger.info(f"  {key.replace('_', ' ').title()}: {value}")
    logger.info()

    # Stub Classes
    if report.stub_classes:
        logger.info("🔴 STUB CLASSES (Wired But Not Implemented)")
        logger.info("-" * 40)
        for cls in report.stub_classes:
            logger.info(f"  • {cls.name}")
            logger.info(f"    File: {cls.file_path}:{cls.line_number}")
            logger.info(f"    Reason: {cls.stub_reason}")
            if show_suggestions:
                logger.info(f"    Suggestion: DELETE or IMPLEMENT")
            logger.info()

    # Orphan Routes
    if report.orphan_routes:
        logger.info("🟡 STUB ROUTES (Registered But Empty Handlers)")
        logger.info("-" * 40)
        for route in report.orphan_routes:
            logger.info(f"  • {route.method} {route.path}")
            logger.info(f"    Handler: {route.handler_name}")
            logger.info(f"    File: {route.file_path}:{route.line_number}")
            logger.info()

    # Duplicate Classes
    if report.duplicate_implementations:
        logger.info("🟠 DUPLICATE CLASS NAMES")
        logger.info("-" * 40)
        for dup in report.duplicate_implementations:
            logger.info(f"  • {dup['class_name']} ({dup['count']} occurrences)")
            for loc in dup['locations']:
                logger.info(f"    - {loc['file']}:{loc['line']}")
            logger.info()

    # Disabled Flags
    if report.disabled_feature_flags:
        logger.info("⚫ DISABLED FEATURE FLAGS")
        logger.info("-" * 40)
        for flag in report.disabled_feature_flags:
            logger.info(f"  • {flag['flag']} = False")
            logger.info(f"    File: {flag['file']}")
            logger.info()

    logger.info("═" * 80)
    logger.info("  AUDIT COMPLETE")
    logger.info("═" * 80 + "\n")


def print_json(report: OrphanReport):
    """Print JSON report."""
    output = {
        "summary": report.summary,
        "stub_classes": [asdict(c) for c in report.stub_classes],
        "orphan_routes": [asdict(r) for r in report.orphan_routes],
        "duplicate_implementations": report.duplicate_implementations,
        "disabled_feature_flags": report.disabled_feature_flags,
    }
    logger.info(json.dumps(output, indent=2))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Audit L9 repo for orphan classes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fix-suggestions", action="store_true", help="Show fix suggestions")
    args = parser.parse_args()

    logger.info("🔍 Scanning L9 repository for orphan classes...\n")

    # Find all Python files
    all_files = find_python_files(REPO_ROOT)
    logger.info(f"  Found {len(all_files)} Python files to analyze")

    # Analyze each file
    all_classes: List[ClassInfo] = []
    all_imports: List[ImportInfo] = []
    all_routes: List[RouteInfo] = []

    for file_path in all_files:
        classes, imports, routes = analyze_file(file_path)
        all_classes.extend(classes)
        all_imports.extend(imports)
        all_routes.extend(routes)

    logger.info(f"  Found {len(all_classes)} classes")
    logger.info(f"  Found {len(all_routes)} routes")

    # Find class usages
    logger.info("  Analyzing class usages...")
    usage_counts = find_class_usages(all_classes, all_files)

    # Find disabled feature flags
    server_file = REPO_ROOT / "api" / "server.py"
    disabled_flags = find_feature_flags(server_file)

    # Find duplicate classes
    duplicates = find_duplicate_classes(all_classes)

    # Generate report
    report = generate_report(
        all_classes,
        all_imports,
        all_routes,
        usage_counts,
        disabled_flags,
        duplicates,
    )

    # Output
    if args.json:
        print_json(report)
    else:
        print_report(report, show_suggestions=args.fix_suggestions)


if __name__ == "__main__":
    main()

