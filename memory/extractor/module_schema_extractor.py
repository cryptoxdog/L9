"""
Module Schema Extractor

Extracts L9 module definitions from kernel YAML files.
Output: Extracted Files/modules/*.yaml
"""

import yaml
from pathlib import Path
from typing import Dict
from .base_extractor import BaseExtractor


class ModuleSchemaExtractor(BaseExtractor):
    """Extracts L9 module schema definitions."""

    def extract(self, input_path: Path, output_root: Path) -> Dict:
        """Extract module schemas from kernel."""
        self.logger.info(f"ModuleSchemaExtractor: Processing {input_path.name}")

        # Only process YAML files
        if input_path.suffix not in [".yaml", ".yml"]:
            return {
                "success": False,
                "files_extracted": 0,
                "errors": ["Not a YAML file"],
            }

        try:
            # Load kernel
            with open(input_path, "r") as f:
                kernel = yaml.safe_load(f)

            # Check if this is a cognition suite kernel
            if "kernel" not in kernel or "modules" not in kernel.get("kernel", {}):
                return {
                    "success": False,
                    "files_extracted": 0,
                    "errors": ["Not a cognition suite kernel"],
                }

            # Generate modules
            modules_generated = self.generate_modules(kernel, output_root)

            self.logger.info(f"  ✅ Generated {modules_generated} module schemas")

            return {
                "success": True,
                "files_extracted": modules_generated,
                "output_path": str(output_root / "modules"),
                "errors": [],
            }

        except Exception as e:
            return {
                "success": False,
                "files_extracted": 0,
                "errors": [f"Failed to process: {e}"],
            }

    def generate_modules(self, kernel: Dict, output_root: Path) -> int:
        """Generate module YAML files from kernel."""
        output_dir = self.create_output_dir(output_root, "modules")
        count = 0

        kernel_data = kernel["kernel"]
        naming = kernel_data["naming"]

        for module in kernel_data["modules"]:
            code = module["code"]

            # Generate module file
            module_file = output_dir / f"{naming['base_prefix']}{code}_module.yaml"
            module_data = {
                "id": f"{naming['id_pattern']}".format(short_code=code),
                "name": module["name"],
                "version": "0.1.0",
                "ring": module["ring"],
                "scope": module["scope"],
                "tags": module["tags"],
                "status": "draft",
            }

            with open(module_file, "w") as f:
                yaml.dump(module_data, f, default_flow_style=False, allow_unicode=True)

            count += 1

        return count

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "MEM-LEAR-023",
    "component_name": "Module Schema Extractor",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "learning",
    "domain": "memory_substrate",
    "type": "collector",
    "status": "active",
    "governance_level": "critical",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements ModuleSchemaExtractor for module schema extractor functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
