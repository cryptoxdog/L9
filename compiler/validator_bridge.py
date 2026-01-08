# compiler/validator_bridge.py

from compiler.schemas import validate_schema

def validate_outputs(artifacts: dict):
    for name, artifact in artifacts.items():
        validate_schema(name, artifact)

    # HARD FAIL CONDITIONS
    for inv in artifacts.get("typed_invariants.yaml", {}).get("typed_invariants", []):
        if not inv["enforced_by"]:
            raise RuntimeError(
                f"Invariant {inv['id']} has no enforcement target"
            )

