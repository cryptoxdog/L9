"""
Trust Model Tests
Purpose: Validate trust tracking functionality
"""

from l9_agent.trust_model import TrustModel
import structlog



logger = structlog.get_logger(__name__)
def test_initial_trust():
    t = TrustModel(initial=0.5)
    assert 0.0 <= t.trust_score <= 1.0
    logger.info("✅ Initial trust test passed")


def test_reinforcement():
    t = TrustModel(initial=0.5)
    t.reinforce(0.1)
    assert t.trust_score > 0.5
    logger.info("✅ Reinforcement test passed")


def test_penalty():
    t = TrustModel(initial=0.5)
    t.penalize(0.2)
    assert t.trust_score < 0.5
    logger.info("✅ Penalty test passed")


def run_trust_tests():
    test_initial_trust()
    test_reinforcement()
    test_penalty()
    logger.info("✅ All trust tests passed")


if __name__ == "__main__":
    run_trust_tests()
