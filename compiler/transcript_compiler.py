# compiler/transcript_compiler.py

from compiler.lexer import extract_claims
from compiler.classifier import classify_claim
from compiler.emitters import (
    decisions,
    ial_candidates,
    invariants,
    work_packets,
)
from compiler.validator_bridge import validate_outputs

class TranscriptCompiler:
    def compile(self, transcript_text: str) -> dict:
        claims = extract_claims(transcript_text)

        buckets = {
            "decisions": [],
            "ials": [],
            "invariants": [],
            "tasks": [],
        }

        for claim in claims:
            kind, payload = classify_claim(claim)
            if kind == "decision":
                buckets["decisions"].append(payload)
            elif kind == "ial":
                buckets["ials"].append(payload)
            elif kind == "invariant":
                buckets["invariants"].append(payload)
            elif kind == "task":
                buckets["tasks"].append(payload)

        artifacts = {
            "decisions.yaml": decisions.emit(buckets["decisions"]),
            "ial_candidates.yaml": ial_candidates.emit(buckets["ials"]),
            "typed_invariants.yaml": invariants.emit(buckets["invariants"]),
            "work_packets.yaml": work_packets.emit(buckets["tasks"]),
        }

        validate_outputs(artifacts)
        return artifacts