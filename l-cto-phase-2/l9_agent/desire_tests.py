"""
Desire/Will/Persistence Tests (ENFORCEMENT)
Purpose: Validate motivation core functionality
"""

from l9_agent.desire_engine import DesireEngine
import structlog
from l9_agent.will_engine import WillEngine
from l9_agent.persistence_engine import PersistenceEngine



logger = structlog.get_logger(__name__)
def run_desire_tests():
    desire = DesireEngine()
    will = WillEngine()
    persist = PersistenceEngine({"activation": 0.6, "abandonment": 0.2})

    desire.register_goal("test_goal")
    desire.reinforce("test_goal", 0.5)

    will.commit("test_goal", desire.get_desire("test_goal"))

    d = desire.get_desire("test_goal")
    w = will.get_will("test_goal")

    assert d > 0, "Desire should be positive after reinforcement"
    assert w > 0, "Will should be positive after commitment"
    assert persist.should_persist(d, w), (
        "Should persist with sufficient desire and will"
    )

    logger.info("✅ Desire/Will/Persistence tests passed")


if __name__ == "__main__":
    run_desire_tests()
