"""
L9 V3.5 Integration Tests
Validates Phase 2 & 3 implementations
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def test_ril_available():
    """Test RIL module imports."""
    from core.agents.relational_intelligence import RelationalIntelligence, ril_enabled
    
    ril = RelationalIntelligence()
    assert ril is not None
    assert callable(ril.analyze)
    assert callable(ril.adjust_output)


def test_toth_available():
    """Test ToT module imports."""
    from core.reasoning.toth import TreeOfThoughts, tot_enabled
    
    tot = TreeOfThoughts()
    assert tot is not None
    assert callable(tot.expand)


def test_psi_kt_available():
    """Test PSI-KT module imports."""
    from core.learning.psi_kt import PSIKTTracer, psi_kt_enabled
    
    tracer = PSIKTTracer()
    assert tracer is not None
    assert callable(tracer.trace)


def test_subjective_logic_available():
    """Test Subjective Logic module imports."""
    from core.bayesian.subjective_logic import SubjectiveLogicAdapter, subjective_logic_enabled
    
    adapter = SubjectiveLogicAdapter()
    assert adapter is not None
    assert callable(adapter.from_probability)


def test_meta_oversight_available():
    """Test Meta-Oversight module imports."""
    from core.governance.meta_oversight import MetaOversight, meta_oversight_enabled
    
    oversight = MetaOversight()
    assert oversight is not None
    assert callable(oversight.monitor_agent)


def test_lean_bridge_available():
    """Test Lean bridge module imports."""
    from core.validation.lean_bridge import LeanBridge, lean_enabled
    
    bridge = LeanBridge()
    assert bridge is not None
    assert callable(bridge.verify_constraint)


def test_ace_modules_available():
    """Test ACE module imports."""
    from core.capital import RiskModel, StrategyOptimizer, SimulationBridge, ace_enabled
    
    risk_model = RiskModel()
    optimizer = StrategyOptimizer()
    bridge = SimulationBridge()
    
    assert risk_model is not None
    assert optimizer is not None
    assert bridge is not None


def test_scenario_cache_available():
    """Test scenario cache module imports."""
    from core.reasoning.scenario_cache import ScenarioCache, scenario_cache_enabled
    
    cache = ScenarioCache()
    assert cache is not None
    assert callable(cache.store)


def test_block_registry_available():
    """Test block registry module imports."""
    from core.reasoning.block_registry import BlockRegistry, block_registry_enabled
    
    registry = BlockRegistry()
    assert registry is not None
    assert callable(registry.create)


def test_agentql_enforcer_available():
    """Test AgentQL enforcer module imports."""
    from core.governance.agentql_enforcer import AgentQLEnforcer, agentql_enforcement_enabled
    
    enforcer = AgentQLEnforcer()
    assert enforcer is not None
    assert callable(enforcer.enforce)


def test_power_commands_available():
    """Test power commands module imports."""
    from core.commands import POWER_COMMANDS, execute_command, power_commands_enabled
    
    assert len(POWER_COMMANDS) == 10
    assert callable(execute_command)
    
    # Test command execution
    result = execute_command('health-check')
    assert result['success'] == True


def test_meta_orchestrator_available():
    """Test meta-orchestrator module imports."""
    from core.commands.meta_orchestrator import MetaOrchestrator
    
    orchestrator = MetaOrchestrator()
    assert orchestrator is not None
    assert callable(orchestrator.execute_chain)


def test_chimera_ril_integration():
    """Test Chimera + RIL integration."""
    from core.agents.chimera_agent import ChimeraAgent
    
    agent = ChimeraAgent('test_001', tier='operational')
    assert agent is not None
    
    # RIL should be None when feature flag disabled
    assert agent.ril is None


def test_forge_board_tot_integration():
    """Test FORGE Board + ToT integration."""
    from core.governance.forge_board import FORGEBoard
    
    board = FORGEBoard()
    assert board is not None
    
    # ToT should be None when feature flag disabled
    assert board.tot is None


def test_rpkt_psi_kt_integration():
    """Test RPKT + PSI-KT integration."""
    from core.learning.rpkt_tracer import RPKTTracer
    
    class DummyLLM:
        pass
    
    tracer = RPKTTracer(DummyLLM())
    assert tracer is not None
    
    # PSI-KT should be None when feature flag disabled
    assert tracer.psi_kt is None


if __name__ == "__main__":
    print("Running L9 V3.5 integration tests...")
    pytest.main([__file__, '-v'])

