"""
ACE (Autonomous Capital Engine) Module Adapter
L9 v3.6 Standard Module
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from core.capital.ace_risk_model import RiskModel, CapitalState, RiskScore
    from core.capital.ace_strategy_optimizer import StrategyOptimizer, CapitalGoal, Policy, CapitalDirective
    from core.capital.ace_simulation_bridge import SimulationBridge, Scenario, SimulationReport
except ImportError:
    logger.warning("ACE components not available, using stub")
    RiskModel = None
    StrategyOptimizer = None
    SimulationBridge = None


def handles(command: str) -> bool:
    """Check if this module handles the given command."""
    ace_commands = [
        "ace_risk_score",
        "ace_optimize",
        "ace_simulate",
        "ace",
        "capital_engine"
    ]
    return command in ace_commands


def run(task: dict) -> dict:
    """Execute ACE task."""
    command = task.get("command")
    
    if not RiskModel:
        return {
            "success": False,
            "module": "ace",
            "error": "ACE components not available"
        }
    
    try:
        if command == "ace_risk_score":
            return _ace_risk_score(task)
        elif command == "ace_optimize":
            return _ace_optimize(task)
        elif command == "ace_simulate":
            return _ace_simulate(task)
        else:
            return _ace_full_pipeline(task)
            
    except Exception as e:
        logger.exception(f"ACE execution failed: {e}")
        return {
            "success": False,
            "module": "ace",
            "operation": command,
            "error": str(e)
        }


def _ace_risk_score(task: dict) -> dict:
    """Calculate risk score for capital state."""
    capital_state_data = task.get("capital_state", {})
    
    risk_model = RiskModel()
    capital_state = CapitalState(**capital_state_data) if capital_state_data else CapitalState()
    risk_score = risk_model.score(capital_state)
    
    return {
        "success": True,
        "module": "ace",
        "operation": "risk_score",
        "output": {
            "risk_score": risk_score.score if hasattr(risk_score, 'score') else risk_score,
            "capital_state": capital_state_data
        }
    }


def _ace_optimize(task: dict) -> dict:
    """Optimize capital strategy."""
    goal_data = task.get("goal", {})
    policy_data = task.get("policy", {})
    
    optimizer = StrategyOptimizer()
    goal = CapitalGoal(**goal_data) if goal_data else CapitalGoal()
    policy = Policy(**policy_data) if policy_data else Policy()
    
    directive = optimizer.optimize(goal, policy)
    
    return {
        "success": True,
        "module": "ace",
        "operation": "optimize",
        "output": {
            "directive": directive.__dict__ if hasattr(directive, '__dict__') else directive
        }
    }


def _ace_simulate(task: dict) -> dict:
    """Run capital simulation."""
    directive_data = task.get("directive", {})
    scenarios_data = task.get("scenarios", [])
    
    bridge = SimulationBridge()
    directive = CapitalDirective(**directive_data) if directive_data else CapitalDirective()
    scenarios = [Scenario(**s) for s in scenarios_data] if scenarios_data else []
    
    report = bridge.run(directive, scenarios)
    
    return {
        "success": True,
        "module": "ace",
        "operation": "simulate",
        "output": {
            "report": report.__dict__ if hasattr(report, '__dict__') else report
        }
    }


def _ace_full_pipeline(task: dict) -> dict:
    """Execute full ACE pipeline: risk → optimize → simulate."""
    capital_state_data = task.get("capital_state", {})
    goal_data = task.get("goal", {})
    
    # 1. Risk scoring
    risk_model = RiskModel()
    capital_state = CapitalState(**capital_state_data) if capital_state_data else CapitalState()
    risk_score = risk_model.score(capital_state)
    
    # 2. Strategy optimization
    optimizer = StrategyOptimizer()
    goal = CapitalGoal(**goal_data) if goal_data else CapitalGoal()
    policy = Policy()
    directive = optimizer.optimize(goal, policy)
    
    # 3. Simulation
    bridge = SimulationBridge()
    scenarios = []
    report = bridge.run(directive, scenarios)
    
    return {
        "success": True,
        "module": "ace",
        "operation": "full_pipeline",
        "output": {
            "risk_score": risk_score.score if hasattr(risk_score, 'score') else risk_score,
            "directive": directive.__dict__ if hasattr(directive, '__dict__') else directive,
            "simulation_report": report.__dict__ if hasattr(report, '__dict__') else report
        }
    }
