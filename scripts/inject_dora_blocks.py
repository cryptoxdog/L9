#!/usr/bin/env python3
"""
DORA Block Auto-Injection Script
=================================
Fast, token-efficient batch injection of DORA blocks for all Python classes.

Usage:
    python inject_dora_blocks.py --repo /path/to/L9 --dry-run
    python inject_dora_blocks.py --repo /path/to/L9 --execute
"""

import ast
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import argparse
import json


@dataclass
class ClassInfo:
    """Information about a discovered class."""
    name: str
    file_path: str
    line_number: int
    module_path: str


@dataclass
class DoraMetadata:
    """DORA block metadata for a file."""
    component_id: str
    component_name: str
    module_version: str
    created_at: str
    created_by: str
    layer: str
    domain: str
    type: str
    status: str
    governance_level: str
    compliance_required: bool
    audit_trail: bool
    purpose: str
    dependencies: List[str]


class DoraBlockInjector:
    """Automated DORA block injection engine."""
    
    # Layer mapping based on directory structure
    LAYER_MAP = {
        "core": "foundation",
        "agents": "intelligence",
        "api": "operations",
        "memory": "learning",
        "runtime": "operations",
        "services": "operations",
        "orchestration": "intelligence",
        "orchestrators": "intelligence",
        "world_model": "learning",
        "simulation": "learning",
        "governance": "security",
        "compliance": "security",
        "security": "security",
    }
    
    # Domain mapping
    DOMAIN_MAP = {
        "agents": "agent_execution",
        "memory": "memory_substrate",
        "governance": "governance",
        "core/agents": "agent_execution",
        "core/governance": "governance",
        "core/memory": "memory_substrate",
        "core/tools": "tool_registry",
        "core/worldmodel": "world_model",
        "services/symbolic_computation": "symbolic_computation",
        "orchestrators": "orchestration",
        "api": "api_gateway",
    }
    
    # Type mapping based on filename patterns
    TYPE_MAP = {
        "service": ["service", "client", "adapter"],
        "engine": ["engine", "executor", "processor"],
        "collector": ["collector", "extractor", "loader"],
        "tracker": ["tracker", "monitor", "observer"],
        "utility": ["helper", "util", "tool"],
        "schema": ["schema", "model", "config"],
        "adapter": ["adapter", "bridge", "wrapper"],
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.classes_found: List[ClassInfo] = []
        self.files_to_process: Dict[str, List[ClassInfo]] = {}
        self.component_id_counter = {}
        
    def scan_repository(self) -> None:
        """Scan repository for all Python files with classes."""
        print(f"🔍 Scanning repository: {self.repo_path}")
        
        for py_file in self.repo_path.rglob("*.py"):
            # Skip archived, tests, and __pycache__
            if any(skip in str(py_file) for skip in ["_archived", "tests", "__pycache__", ".venv"]):
                continue
                
            classes = self._extract_classes(py_file)
            if classes:
                self.files_to_process[str(py_file)] = classes
                self.classes_found.extend(classes)
        
        print(f"✅ Found {len(self.classes_found)} classes in {len(self.files_to_process)} files")
    
    def _extract_classes(self, file_path: Path) -> List[ClassInfo]:
        """Extract class definitions from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    module_path = self._get_module_path(file_path)
                    classes.append(ClassInfo(
                        name=node.name,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        module_path=module_path
                    ))
            
            return classes
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
            return []
    
    def _get_module_path(self, file_path: Path) -> str:
        """Convert file path to Python module path."""
        rel_path = file_path.relative_to(self.repo_path)
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        return ".".join(module_parts)
    
    def _generate_component_id(self, file_path: str, layer: str) -> str:
        """Generate unique component ID."""
        # Extract domain abbreviation
        parts = Path(file_path).relative_to(self.repo_path).parts
        
        if len(parts) >= 2:
            domain_abbrev = parts[0][:3].upper()
        else:
            domain_abbrev = "L9"
        
        layer_abbrev = layer[:4].upper()
        
        # Get counter for this prefix
        prefix = f"{domain_abbrev}-{layer_abbrev}"
        if prefix not in self.component_id_counter:
            self.component_id_counter[prefix] = 1
        else:
            self.component_id_counter[prefix] += 1
        
        counter = self.component_id_counter[prefix]
        return f"{domain_abbrev}-{layer_abbrev}-{counter:03d}"
    
    def _infer_layer(self, file_path: str) -> str:
        """Infer layer from file path."""
        parts = Path(file_path).relative_to(self.repo_path).parts
        
        for part in parts:
            if part in self.LAYER_MAP:
                return self.LAYER_MAP[part]
        
        return "operations"  # Default
    
    def _infer_domain(self, file_path: str) -> str:
        """Infer domain from file path."""
        parts = Path(file_path).relative_to(self.repo_path).parts
        
        # Try multi-part matches first
        for i in range(len(parts)):
            path_segment = "/".join(parts[:i+1])
            if path_segment in self.DOMAIN_MAP:
                return self.DOMAIN_MAP[path_segment]
        
        # Try single part matches
        for part in parts:
            if part in self.DOMAIN_MAP:
                return self.DOMAIN_MAP[part]
        
        # Default to first directory
        return parts[0] if parts else "general"
    
    def _infer_type(self, file_path: str) -> str:
        """Infer component type from filename."""
        filename = Path(file_path).stem.lower()
        
        for comp_type, patterns in self.TYPE_MAP.items():
            if any(pattern in filename for pattern in patterns):
                return comp_type
        
        return "utility"  # Default
    
    def _infer_governance_level(self, domain: str, layer: str) -> str:
        """Infer governance level based on domain and layer."""
        critical_domains = ["governance", "memory_substrate", "agent_execution", "security"]
        critical_layers = ["security", "foundation"]
        
        if domain in critical_domains or layer in critical_layers:
            return "critical"
        elif layer == "intelligence":
            return "high"
        elif layer == "learning":
            return "high"
        else:
            return "medium"
    
    def _generate_purpose(self, classes: List[ClassInfo], file_path: str) -> str:
        """Generate purpose statement based on classes and file path."""
        filename = Path(file_path).stem
        class_names = [c.name for c in classes]
        
        if len(class_names) == 1:
            return f"Implements {class_names[0]} for {filename.replace('_', ' ')} functionality"
        else:
            return f"Provides {filename.replace('_', ' ')} components including {', '.join(class_names[:3])}"
    
    def _extract_dependencies(self, file_path: str) -> List[str]:
        """Extract import dependencies from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            deps = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("l9.") or alias.name.startswith("L9."):
                            deps.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and (node.module.startswith("l9.") or node.module.startswith("L9.")):
                        deps.add(node.module)
            
            return sorted(list(deps))[:5]  # Limit to top 5
        except:
            return []
    
    def generate_metadata(self, file_path: str, classes: List[ClassInfo]) -> DoraMetadata:
        """Generate DORA metadata for a file."""
        layer = self._infer_layer(file_path)
        domain = self._infer_domain(file_path)
        comp_type = self._infer_type(file_path)
        governance_level = self._infer_governance_level(domain, layer)
        
        component_id = self._generate_component_id(file_path, layer)
        component_name = Path(file_path).stem.replace("_", " ").title()
        purpose = self._generate_purpose(classes, file_path)
        dependencies = self._extract_dependencies(file_path)
        
        return DoraMetadata(
            component_id=component_id,
            component_name=component_name,
            module_version="1.0.0",
            created_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            created_by="L9_DORA_Injector",
            layer=layer,
            domain=domain,
            type=comp_type,
            status="active",
            governance_level=governance_level,
            compliance_required=True,
            audit_trail=True,
            purpose=purpose,
            dependencies=dependencies
        )
    
    def _check_existing_dora_block(self, file_path: str) -> bool:
        """Check if file already has a DORA block."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for DORA block markers
            return "__dora_block__" in content or "L9 DORA BLOCK" in content
        except:
            return False
    
    def _format_dora_block(self, metadata: DoraMetadata) -> str:
        """Format DORA block as Python code."""
        deps_str = json.dumps(metadata.dependencies, indent=4)
        
        return f'''

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {{
    "component_id": "{metadata.component_id}",
    "component_name": "{metadata.component_name}",
    "module_version": "{metadata.module_version}",
    "created_at": "{metadata.created_at}",
    "created_by": "{metadata.created_by}",
    "layer": "{metadata.layer}",
    "domain": "{metadata.domain}",
    "type": "{metadata.type}",
    "status": "{metadata.status}",
    "governance_level": "{metadata.governance_level}",
    "compliance_required": {str(metadata.compliance_required)},
    "audit_trail": {str(metadata.audit_trail)},
    "purpose": "{metadata.purpose}",
    "dependencies": {deps_str},
}}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
'''
    
    def inject_dora_block(self, file_path: str, metadata: DoraMetadata, dry_run: bool = True) -> bool:
        """Inject DORA block at the end of a file."""
        try:
            # Check if already has DORA block
            if self._check_existing_dora_block(file_path):
                print(f"⏭️  Skipping {file_path} (already has DORA block)")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove trailing whitespace
            content = content.rstrip()
            
            # Add DORA block
            dora_block = self._format_dora_block(metadata)
            new_content = content + dora_block
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Injected DORA block into {file_path}")
            else:
                print(f"🔍 [DRY RUN] Would inject DORA block into {file_path}")
            
            return True
        except Exception as e:
            print(f"❌ Error injecting DORA block into {file_path}: {e}")
            return False
    
    def process_all_files(self, dry_run: bool = True) -> Dict[str, any]:
        """Process all files and inject DORA blocks."""
        print(f"\n{'🔍 DRY RUN MODE' if dry_run else '🚀 EXECUTION MODE'}")
        print("=" * 80)
        
        results = {
            "total_files": len(self.files_to_process),
            "injected": 0,
            "skipped": 0,
            "failed": 0,
            "metadata": []
        }
        
        for file_path, classes in self.files_to_process.items():
            metadata = self.generate_metadata(file_path, classes)
            
            success = self.inject_dora_block(file_path, metadata, dry_run)
            
            if success:
                results["injected"] += 1
                results["metadata"].append({
                    "file": file_path,
                    "component_id": metadata.component_id,
                    "classes": [c.name for c in classes]
                })
            else:
                if self._check_existing_dora_block(file_path):
                    results["skipped"] += 1
                else:
                    results["failed"] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, any], output_path: str = "dora_injection_report.json") -> None:
        """Generate injection report."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 INJECTION REPORT")
        print("=" * 80)
        print(f"Total files processed: {results['total_files']}")
        print(f"✅ Successfully injected: {results['injected']}")
        print(f"⏭️  Skipped (existing): {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"\n📄 Full report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Inject DORA blocks into L9 repository")
    parser.add_argument("--repo", required=True, help="Path to L9 repository")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes)")
    parser.add_argument("--execute", action="store_true", help="Execute injection (makes changes)")
    parser.add_argument("--report", default="dora_injection_report.json", help="Output report path")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Error: Must specify either --dry-run or --execute")
        sys.exit(1)
    
    if args.dry_run and args.execute:
        print("❌ Error: Cannot specify both --dry-run and --execute")
        sys.exit(1)
    
    injector = DoraBlockInjector(args.repo)
    injector.scan_repository()
    
    results = injector.process_all_files(dry_run=args.dry_run)
    injector.generate_report(results, args.report)
    
    print("\n✅ DORA injection complete!")


if __name__ == "__main__":
    main()
