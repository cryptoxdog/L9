"""
L9 Global State Audit

Scans Python files for suspicious module-level mutable state patterns.

This is a heuristic tool, NOT a formal guarantee.

It looks for:
  - top-level assignments to dict/list/set
  - names like STATE, CACHE, active_*, *_state, *_cache
and prints their locations for manual review.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[2]


def iter_python_files() -> List[Path]:
    ignored = {"tests", ".venv", "venv", "migrations", "l9_private"}
    files: List[Path] = []

    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT)
        parts = set(rel.parts)
        if parts & ignored:
            continue
        files.append(path)
    return files


class GlobalStateVisitor(ast.NodeVisitor):
    def __init__(self, filename: Path):
        self.filename = filename
        self.suspicious: List[Tuple[int, str]] = []

    def visit_Assign(self, node: ast.Assign):
        # Only look at module-level assignments
        if not isinstance(getattr(node, "parent", None), ast.Module):
            return

        # Track targets
        target_names = []
        for t in node.targets:
            if isinstance(t, ast.Name):
                target_names.append(t.id)

        # Track suspicious value types
        suspicious_value = isinstance(
            node.value,
            (ast.Dict, ast.List, ast.Set, ast.Call),
        )

        # Heuristic: name patterns
        name_patterns = ("STATE", "CACHE", "active_", "_state", "_cache")
        suspicious_name = any(
            any(pattern in name.upper() for pattern in name_patterns)
            for name in target_names
        )

        if suspicious_value or suspicious_name:
            line = node.lineno
            for name in target_names:
                self.suspicious.append((line, name))

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore[attr-defined]
            self.visit(child)


def main():
    files = iter_python_files()
    print(f"[L9 STATE AUDIT] Scanning {len(files)} Python files under {ROOT}")

    total_hits = 0

    for path in files:
        try:
            src = path.read_text(encoding="utf-8")
        except Exception as e:  # pragma: no cover
            print(f"[WARN] Could not read {path}: {e}")
            continue

        try:
            tree = ast.parse(src)
        except SyntaxError as e:  # pragma: no cover
            print(f"[WARN] Syntax error in {path}: {e}")
            continue

        visitor = GlobalStateVisitor(path)
        visitor.visit(tree)

        if visitor.suspicious:
            print(f"\n[FILE] {path.relative_to(ROOT)}")
            for lineno, name in visitor.suspicious:
                print(f"  line {lineno:4d}: {name}")
            total_hits += len(visitor.suspicious)

    print(f"\n[L9 STATE AUDIT] Suspicious global state declarations: {total_hits}")


if __name__ == "__main__":
    main()

