#!/usr/bin/env python3
"""
Multi-Format DORA Block Auto-Injection Script
==============================================
Injects DORA blocks into YAML, JSON, and Markdown files.

Usage:
    python inject_dora_multiformat.py --repo /path/to/L9 --dry-run
    python inject_dora_multiformat.py --repo /path/to/L9 --execute
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import yaml


@dataclass
class DoraMetadata:
    """DORA block metadata."""
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


class MultiFormatDoraInjector:
    """Multi-format DORA block injection engine."""
    
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
        "config": "foundation",
        "schemas": "foundation",
    }
    
    DOMAIN_MAP = {
        "agents": "agent_execution",
        "memory": "memory_substrate",
        "governance": "governance",
        "config": "configuration",
        "schemas": "schema_registry",
        "api": "api_gateway",
        "orchestrators": "orchestration",
        "world_model": "world_model",
        "services": "service_layer",
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.files_to_process: Dict[str, str] = {}  # file_path -> file_type
        self.component_id_counter = {}
        
    def scan_repository(self, file_types: List[str]) -> None:
        """Scan repository for specified file types."""
        print(f"🔍 Scanning repository for: {', '.join(file_types)}")
        
        for file_type in file_types:
            for file_path in self.repo_path.rglob(f"*.{file_type}"):
                # Skip archived, tests, node_modules, .venv
                if any(skip in str(file_path) for skip in [
                    "_archived", "tests", "__pycache__", ".venv", 
                    "node_modules", ".git", "venv"
                ]):
                    continue
                
                # Skip package files
                if file_path.name in ["package.json", "package-lock.json", "tsconfig.json"]:
                    continue
                    
                self.files_to_process[str(file_path)] = file_type
        
        print(f"✅ Found {len(self.files_to_process)} files to process")
    
    def _generate_component_id(self, file_path: str, layer: str) -> str:
        """Generate unique component ID."""
        parts = Path(file_path).relative_to(self.repo_path).parts
        
        if len(parts) >= 2:
            domain_abbrev = parts[0][:3].upper()
        else:
            domain_abbrev = "L9"
        
        layer_abbrev = layer[:4].upper()
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
        
        return "operations"
    
    def _infer_domain(self, file_path: str) -> str:
        """Infer domain from file path."""
        parts = Path(file_path).relative_to(self.repo_path).parts
        
        for part in parts:
            if part in self.DOMAIN_MAP:
                return self.DOMAIN_MAP[part]
        
        return parts[0] if parts else "general"
    
    def _infer_type(self, file_path: str, file_type: str) -> str:
        """Infer component type from filename and type."""
        filename = Path(file_path).stem.lower()
        
        if file_type in ["yaml", "yml"]:
            if "config" in filename or "settings" in filename:
                return "config"
            elif "schema" in filename:
                return "schema"
            else:
                return "config"
        elif file_type == "json":
            if "schema" in filename:
                return "schema"
            elif "config" in filename:
                return "config"
            else:
                return "schema"
        elif file_type == "md":
            return "schema"
        
        return "config"
    
    def _infer_governance_level(self, domain: str, layer: str) -> str:
        """Infer governance level."""
        critical_domains = ["governance", "memory_substrate", "agent_execution", "security", "configuration"]
        critical_layers = ["security", "foundation"]
        
        if domain in critical_domains or layer in critical_layers:
            return "critical"
        elif layer == "intelligence":
            return "high"
        elif layer == "learning":
            return "high"
        else:
            return "medium"
    
    def _generate_purpose(self, file_path: str, file_type: str) -> str:
        """Generate purpose statement."""
        filename = Path(file_path).stem
        
        if file_type in ["yaml", "yml"]:
            return f"Configuration file for {filename.replace('_', ' ').replace('-', ' ')}"
        elif file_type == "json":
            return f"Schema or configuration definition for {filename.replace('_', ' ').replace('-', ' ')}"
        elif file_type == "md":
            return f"Documentation for {filename.replace('_', ' ').replace('-', ' ')}"
        
        return f"Configuration file: {filename}"
    
    def generate_metadata(self, file_path: str, file_type: str) -> DoraMetadata:
        """Generate DORA metadata for a file."""
        layer = self._infer_layer(file_path)
        domain = self._infer_domain(file_path)
        comp_type = self._infer_type(file_path, file_type)
        governance_level = self._infer_governance_level(domain, layer)
        
        component_id = self._generate_component_id(file_path, layer)
        component_name = Path(file_path).stem.replace("_", " ").replace("-", " ").title()
        purpose = self._generate_purpose(file_path, file_type)
        
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
            dependencies=[]
        )
    
    def _check_existing_dora_block(self, file_path: str, file_type: str) -> bool:
        """Check if file already has a DORA block."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_type in ["yaml", "yml"]:
                return "l9_trace:" in content or "l9_dora:" in content
            elif file_type == "json":
                return '"_l9_trace"' in content or '"_l9_dora"' in content
            elif file_type == "md":
                return "## L9 DORA BLOCK" in content
            
            return False
        except:
            return False
    
    def _format_yaml_dora_block(self, metadata: DoraMetadata) -> str:
        """Format DORA block for YAML."""
        return f'''
# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
l9_dora:
  component_id: "{metadata.component_id}"
  component_name: "{metadata.component_name}"
  module_version: "{metadata.module_version}"
  created_at: "{metadata.created_at}"
  created_by: "{metadata.created_by}"
  layer: "{metadata.layer}"
  domain: "{metadata.domain}"
  type: "{metadata.type}"
  status: "{metadata.status}"
  governance_level: "{metadata.governance_level}"
  compliance_required: {str(metadata.compliance_required).lower()}
  audit_trail: {str(metadata.audit_trail).lower()}
  purpose: "{metadata.purpose}"
  dependencies: []
# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
'''
    
    def _format_json_dora_block(self, metadata: DoraMetadata) -> Dict:
        """Format DORA block for JSON."""
        return {
            "_l9_dora": {
                "component_id": metadata.component_id,
                "component_name": metadata.component_name,
                "module_version": metadata.module_version,
                "created_at": metadata.created_at,
                "created_by": metadata.created_by,
                "layer": metadata.layer,
                "domain": metadata.domain,
                "type": metadata.type,
                "status": metadata.status,
                "governance_level": metadata.governance_level,
                "compliance_required": metadata.compliance_required,
                "audit_trail": metadata.audit_trail,
                "purpose": metadata.purpose,
                "dependencies": []
            }
        }
    
    def _format_markdown_dora_block(self, metadata: DoraMetadata) -> str:
        """Format DORA block for Markdown."""
        return f'''

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | {metadata.component_id} |
| **Component Name** | {metadata.component_name} |
| **Module Version** | {metadata.module_version} |
| **Created At** | {metadata.created_at} |
| **Created By** | {metadata.created_by} |
| **Layer** | {metadata.layer} |
| **Domain** | {metadata.domain} |
| **Type** | {metadata.type} |
| **Status** | {metadata.status} |
| **Governance Level** | {metadata.governance_level} |
| **Compliance Required** | {metadata.compliance_required} |
| **Audit Trail** | {metadata.audit_trail} |
| **Purpose** | {metadata.purpose} |

---
'''
    
    def inject_yaml_dora_block(self, file_path: str, metadata: DoraMetadata, dry_run: bool) -> bool:
        """Inject DORA block into YAML file."""
        try:
            if self._check_existing_dora_block(file_path, "yaml"):
                print(f"⏭️  Skipping {file_path} (already has DORA block)")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.rstrip()
            dora_block = self._format_yaml_dora_block(metadata)
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
    
    def inject_json_dora_block(self, file_path: str, metadata: DoraMetadata, dry_run: bool) -> bool:
        """Inject DORA block into JSON file."""
        try:
            if self._check_existing_dora_block(file_path, "json"):
                print(f"⏭️  Skipping {file_path} (already has DORA block)")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dora_block = self._format_json_dora_block(metadata)
            data.update(dora_block)
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Injected DORA block into {file_path}")
            else:
                print(f"🔍 [DRY RUN] Would inject DORA block into {file_path}")
            
            return True
        except Exception as e:
            print(f"❌ Error injecting DORA block into {file_path}: {e}")
            return False
    
    def inject_markdown_dora_block(self, file_path: str, metadata: DoraMetadata, dry_run: bool) -> bool:
        """Inject DORA block into Markdown file."""
        try:
            if self._check_existing_dora_block(file_path, "md"):
                print(f"⏭️  Skipping {file_path} (already has DORA block)")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.rstrip()
            dora_block = self._format_markdown_dora_block(metadata)
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
            "by_type": {"yaml": 0, "json": 0, "md": 0},
            "metadata": []
        }
        
        for file_path, file_type in self.files_to_process.items():
            metadata = self.generate_metadata(file_path, file_type)
            
            success = False
            if file_type in ["yaml", "yml"]:
                success = self.inject_yaml_dora_block(file_path, metadata, dry_run)
            elif file_type == "json":
                success = self.inject_json_dora_block(file_path, metadata, dry_run)
            elif file_type == "md":
                success = self.inject_markdown_dora_block(file_path, metadata, dry_run)
            
            if success:
                results["injected"] += 1
                results["by_type"][file_type] = results["by_type"].get(file_type, 0) + 1
                results["metadata"].append({
                    "file": file_path,
                    "type": file_type,
                    "component_id": metadata.component_id
                })
            else:
                if self._check_existing_dora_block(file_path, file_type):
                    results["skipped"] += 1
                else:
                    results["failed"] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, any], output_path: str) -> None:
        """Generate injection report."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 INJECTION REPORT")
        print("=" * 80)
        print(f"Total files processed: {results['total_files']}")
        print(f"✅ Successfully injected: {results['injected']}")
        print(f"   - YAML: {results['by_type'].get('yaml', 0) + results['by_type'].get('yml', 0)}")
        print(f"   - JSON: {results['by_type'].get('json', 0)}")
        print(f"   - Markdown: {results['by_type'].get('md', 0)}")
        print(f"⏭️  Skipped (existing): {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"\n📄 Full report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Inject DORA blocks into multi-format files")
    parser.add_argument("--repo", required=True, help="Path to L9 repository")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--execute", action="store_true", help="Execute injection")
    parser.add_argument("--report", default="dora_multiformat_report.json", help="Output report path")
    parser.add_argument("--types", default="yaml,yml,json,md", help="Comma-separated file types")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Error: Must specify either --dry-run or --execute")
        sys.exit(1)
    
    file_types = args.types.split(",")
    
    injector = MultiFormatDoraInjector(args.repo)
    injector.scan_repository(file_types)
    
    results = injector.process_all_files(dry_run=args.dry_run)
    injector.generate_report(results, args.report)
    
    print("\n✅ Multi-format DORA injection complete!")


if __name__ == "__main__":
    main()
