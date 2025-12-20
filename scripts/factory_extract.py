#!/usr/bin/env python3
"""
L9 Research Factory - CLI Extraction Tool
==========================================

Extract production code from YAML agent schemas.

Usage:
    # Extract from schema file
    python scripts/factory_extract.py \\
        --schema path/to/schema.yaml \\
        --output L9/agents/new_agent/
    
    # With glue configuration
    python scripts/factory_extract.py \\
        --schema path/to/schema.yaml \\
        --glue path/to/glue.yaml \\
        --output L9/agents/new_agent/
    
    # Dry run (validate only)
    python scripts/factory_extract.py \\
        --schema path/to/schema.yaml \\
        --output L9/agents/new_agent/ \\
        --dry-run
    
    # Validate only (no extraction)
    python scripts/factory_extract.py \\
        --schema path/to/schema.yaml \\
        --validate-only

Version: 1.0.0
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.research_factory import (
    parse_schema,
    validate_schema,
    UniversalExtractor,
    load_glue_config,
)


def print_validation_result(result, verbose: bool = False):
    """Print validation result."""
    if result.valid:
        print("✅ Schema is valid")
    else:
        print("❌ Schema validation failed")
    
    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"    • [{error.code}] {error.message}")
            if error.path and verbose:
                print(f"      at: {error.path}")
    
    if result.warnings:
        print(f"\n  Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"    • [{warning.code}] {warning.message}")
            if warning.path and verbose:
                print(f"      at: {warning.path}")


def print_extraction_result(result, verbose: bool = False):
    """Print extraction result."""
    if result.success:
        print("✅ Extraction successful")
    else:
        print("❌ Extraction failed")
    
    if result.schema:
        print(f"\n  Agent: {result.schema.system.name}")
        print(f"  ID: {result.schema.get_agent_id()}")
        print(f"  Version: {result.schema.metadata.version}")
    
    print(f"\n  Files generated: {len(result.generated_files)}")
    if verbose and result.generated_files:
        for f in result.generated_files:
            print(f"    • {f.path} ({f.size_bytes} bytes)")
    
    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"    • {error}")
    
    if result.warnings:
        print(f"\n  Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"    • {warning}")
    
    if result.manifest:
        print(f"\n  Manifest:")
        print(f"    • Total lines: {result.manifest.total_lines}")
        print(f"    • Total bytes: {result.manifest.total_bytes}")
    
    print(f"\n  Duration: {result.duration_ms}ms")


async def main():
    parser = argparse.ArgumentParser(
        description="L9 Research Factory - Extract code from YAML schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument(
        "--schema", "-s",
        type=str,
        required=True,
        help="Path to YAML schema file",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for generated files",
    )
    
    parser.add_argument(
        "--glue", "-g",
        type=str,
        help="Path to glue configuration YAML",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and generate but don't write files",
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate schema, don't extract",
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation (warnings become errors)",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        sys.exit(1)
    
    if not args.validate_only and not args.output:
        print("Error: --output is required unless --validate-only is set", file=sys.stderr)
        sys.exit(1)
    
    # Parse schema
    try:
        schema = parse_schema(schema_path)
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"Error parsing schema: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate only mode
    if args.validate_only:
        result = validate_schema(schema)
        
        if args.json:
            print(json.dumps(result.to_dict()))
        else:
            print_validation_result(result, args.verbose)
        
        sys.exit(0 if result.valid else 1)
    
    # Load glue config if provided
    glue = None
    if args.glue:
        glue_path = Path(args.glue)
        if not glue_path.exists():
            print(f"Error: Glue file not found: {glue_path}", file=sys.stderr)
            sys.exit(1)
        glue = load_glue_config(glue_path)
    
    # Extract
    extractor = UniversalExtractor(strict_validation=args.strict)
    
    result = await extractor.extract(
        schema=schema,
        output_dir=args.output,
        glue=glue,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    
    if args.json:
        print(json.dumps(result.to_dict()))
    else:
        mode = "DRY RUN - " if args.dry_run else ""
        print(f"\n{mode}Extraction Result")
        print("=" * 50)
        print_extraction_result(result, args.verbose)
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    asyncio.run(main())

