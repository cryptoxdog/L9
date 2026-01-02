# L9 CodeGen System

Autonomous code generation from YAML specifications.

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `schemas/` | Schema definitions (Module-Spec-v2.4, DORA contract, samples) |
| `templates/` | Code templates (Python, README, glue) |
| `process/` | Pipeline definitions (phases, validation, dependencies) |
| `docs/` | Usage guides, references, phase documentation |
| `specs/` | YAML specs to be converted to code |
| `extractions/` | Generated output (gitignored) |

## Quick Start

1. Define spec using `schemas/Module-Spec-v2.4.yaml`
2. Run: `python -m agents.codegenagent generate specs/my_spec.yaml`
3. Review output in `extractions/`

## Key Files

| File | Description |
|------|-------------|
| `schemas/Module-Spec-v2.4.yaml` | Canonical 22-section module spec |
| `schemas/dora-contract.yaml` | DORA block enforcement rules |
| `schemas/Module-Prompt-CURSOR-v2.0.yaml` | Cursor-optimized module prompts |
| `process/meta.codegen.schema.yaml` | Pipeline orchestration |
| `templates/python/dora-template.py` | Python file template with DORA blocks |
| `templates/python/module-template.py` | Full L9 module template |

## Template Types

### Python Templates (`templates/python/`)
- `dora-template.py` - Minimal template with DORA header/footer/trace blocks
- `module-template.py` - Full L9 module with imports and initialization

### README Templates (`templates/readme/`)
- `root-readme-template.md` - Main repository README template
- `subsystem-template.md` - Subsystem README template
- `ai-super-prompt.md` - AI/Labs research prompt template

### Glue Templates (`templates/glue/`)
- Integration and wiring templates

## Process Flow

See `process/README.md` for detailed pipeline documentation.

```
YAML Spec → Dependency Resolution → Code Generation → Validation → DORA Compliance → File Emission
```

## Related Modules

- `agents/codegenagent/` - Python implementation of CodeGenAgent
- `ir_engine/` - Intermediate representation compiler
- `services/symbolic_computation/` - SymPy integration service

## Sample Schemas

Located in `schemas/samples/`:
- `simple_agent.yaml` - Basic agent example
- `domain_adapter.yaml` - Domain adapter pattern
- `orchestrator.yaml` - Orchestrator pattern
- `glue_layer.yaml` - Glue layer pattern
- `sympy_schema_v6.yaml` - SymPy service example

## Documentation

See `docs/` for:
- `USAGE_GUIDE.md` - Detailed usage instructions
- `QUICKSTART.md` - Quick start guide
- `INTEGRATION_GUIDE.md` - Integration and deployment
- `sympy-phases/` - SymPy development phase documentation

