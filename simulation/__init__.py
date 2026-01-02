"""
L9 Simulation - IR Candidate Evaluation Engine
==============================================

Simulates IR graphs to evaluate:
- Feasibility
- Risk assessment
- Resource requirements
- Failure modes

Components:
- SimulationEngine: Core simulation runner
- ScenarioLoader: Load and define scenarios
- OutcomeEvaluator: Evaluate and score results
"""

from simulation.simulation_engine import (
    SimulationEngine,
    SimulationConfig,
    SimulationRun,
    SimulationMetrics,
)
from simulation.scenario_loader import (
    ScenarioLoader,
    Scenario,
    ScenarioType,
)
from simulation.outcome_evaluator import (
    OutcomeEvaluator,
    EvaluationResult,
    EvaluationCriteria,
)

__all__ = [
    # Engine
    "SimulationEngine",
    "SimulationConfig",
    "SimulationRun",
    "SimulationMetrics",
    # Scenarios
    "ScenarioLoader",
    "Scenario",
    "ScenarioType",
    # Evaluation
    "OutcomeEvaluator",
    "EvaluationResult",
    "EvaluationCriteria",
]
