"""
Value Alignment Tests (MANDATORY enforcement)
Purpose: Fail fast if alignment logic breaks
"""

from l9_agent.value_alignment import ValueAlignmentEngine
import structlog



logger = structlog.get_logger(__name__)
def run_value_alignment_tests():
    engine = ValueAlignmentEngine()

    perfect = engine.score_action(
        ["trust", "reciprocity", "coherence", "autonomy_support", "truthfulness"]
    )
    assert perfect == 1.0, f"Expected 1.0, got {perfect}"

    partial = engine.score_action(["trust", "coherence"])
    assert 0.0 < partial < 1.0, "Partial alignment invalid"

    none = engine.score_action([])
    assert none == 0.0, f"Expected 0.0, got {none}"

    logger.info("✅ Value alignment tests passed")


if __name__ == "__main__":
    run_value_alignment_tests()
