"""
Agent Bootstrap Phase Unit Tests
================================

Unit tests for the 7-phase atomic agent bootstrap ceremony.
Tests each phase in isolation with mocks for dependencies.

Version: 1.0.0
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
import structlog

logger = structlog.get_logger(__name__)

# =============================================================================
# Phase 0: Validate Blueprint
# =============================================================================


class TestPhase0Validate:
    """Tests for Phase 0: Validate Blueprint"""

    @pytest.mark.asyncio
    async def test_validate_agent_config_success(self):
        """Valid AgentConfig with kernels passes validation."""
        from core.agents.bootstrap.phase_0_validate import validate_blueprint
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            kernel_refs=["01_master_kernel.yaml", "02_identity_kernel.yaml"],
        )

        mock_substrate = MagicMock()
        mock_substrate.is_ready = MagicMock(return_value=True)

        errors = await validate_blueprint(config, mock_substrate)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_agent_config_missing_id(self):
        """AgentConfig without agent_id fails validation."""
        from core.agents.bootstrap.phase_0_validate import validate_blueprint
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="",  # Empty ID
            name="Test Agent",
            kernel_refs=["01_master_kernel.yaml"],
        )

        mock_substrate = MagicMock()

        errors = await validate_blueprint(config, mock_substrate)
        assert any("agent_id" in e.lower() for e in errors)

    @pytest.mark.asyncio
    async def test_validate_substrate_not_ready(self):
        """Validation fails when substrate is not ready."""
        from core.agents.bootstrap.phase_0_validate import validate_blueprint
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            kernel_refs=["01_master_kernel.yaml"],
        )

        mock_substrate = MagicMock()
        mock_substrate.is_ready = MagicMock(return_value=False)

        errors = await validate_blueprint(config, mock_substrate)
        assert any("substrate" in e.lower() for e in errors)


# =============================================================================
# Phase 1: Load Kernels
# =============================================================================


class TestPhase1LoadKernels:
    """Tests for Phase 1: Load Kernels"""

    @pytest.mark.asyncio
    async def test_load_kernels_success(self):
        """Kernels load successfully with valid YAML files."""
        from core.agents.bootstrap.phase_1_load_kernels import load_kernels

        kernel_refs = ["01_master_kernel.yaml"]

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=MagicMock(
                            return_value=MagicMock(
                                read=MagicMock(return_value="kernel_id: master\nrules:\n  - rule: test")
                            )
                        ),
                        __exit__=MagicMock(return_value=None),
                    )
                ),
            ):
                kernels, errors = await load_kernels(kernel_refs)

        # Should succeed without errors
        assert errors == []

    @pytest.mark.asyncio
    async def test_load_kernels_file_not_found(self):
        """Missing kernel file returns error."""
        from core.agents.bootstrap.phase_1_load_kernels import load_kernels

        kernel_refs = ["nonexistent_kernel.yaml"]

        with patch("pathlib.Path.exists", return_value=False):
            kernels, errors = await load_kernels(kernel_refs)

        assert len(errors) > 0
        assert any("not found" in e.lower() for e in errors)


# =============================================================================
# Phase 2: Instantiate Agent
# =============================================================================


class TestPhase2Instantiate:
    """Tests for Phase 2: Instantiate Agent"""

    @pytest.mark.asyncio
    async def test_instantiate_agent_creates_instance(self):
        """Agent instance is created with valid UUID."""
        from core.agents.bootstrap.phase_2_instantiate import instantiate_agent
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
        )

        # Mock Neo4j client
        mock_neo4j = AsyncMock()
        mock_neo4j.run_query = AsyncMock(return_value=[{"created": True}])

        with patch(
            "core.agents.bootstrap.phase_2_instantiate.get_neo4j_client",
            return_value=mock_neo4j,
        ):
            instance, errors = await instantiate_agent(config)

        assert errors == []
        assert instance is not None
        assert instance.agent_id == "test-agent"
        # Verify instance_id is valid UUID
        UUID(instance.instance_id)


# =============================================================================
# Phase 3: Bind Kernels
# =============================================================================


class TestPhase3BindKernels:
    """Tests for Phase 3: Bind Kernels"""

    @pytest.mark.asyncio
    async def test_bind_kernels_activates_all(self):
        """All kernels are bound and activated."""
        from core.agents.bootstrap.phase_3_bind_kernels import bind_kernels

        mock_instance = MagicMock()
        mock_instance.agent_id = "test-agent"
        mock_instance.instance_id = "inst-123"

        kernels = [
            {"kernel_id": "master", "hash": "abc123"},
            {"kernel_id": "identity", "hash": "def456"},
        ]

        # Mock Neo4j
        mock_neo4j = AsyncMock()
        mock_neo4j.run_query = AsyncMock(return_value=[])

        with patch(
            "core.agents.bootstrap.phase_3_bind_kernels.get_neo4j_client",
            return_value=mock_neo4j,
        ):
            errors = await bind_kernels(mock_instance, kernels)

        assert errors == []
        # Verify Neo4j was called for each kernel
        assert mock_neo4j.run_query.call_count >= 2


# =============================================================================
# Phase 4: Load Identity
# =============================================================================


class TestPhase4LoadIdentity:
    """Tests for Phase 4: Load Identity"""

    @pytest.mark.asyncio
    async def test_load_identity_hydrates_memory(self):
        """Identity is loaded and written to memory."""
        from core.agents.bootstrap.phase_4_load_identity import load_identity
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
        )

        mock_instance = MagicMock()
        mock_instance.agent_id = "test-agent"

        mock_substrate = AsyncMock()
        mock_substrate.write_packet = AsyncMock(return_value=MagicMock(id="pkt-123"))

        # Mock identity YAML
        identity_yaml = """
        name: Test Agent
        personality: Helpful
        background: Test background
        """

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open",
                MagicMock(
                    return_value=MagicMock(
                        __enter__=MagicMock(
                            return_value=MagicMock(read=MagicMock(return_value=identity_yaml))
                        ),
                        __exit__=MagicMock(return_value=None),
                    )
                ),
            ):
                errors = await load_identity(config, mock_instance, mock_substrate)

        assert errors == []


# =============================================================================
# Phase 5: Bind Tools
# =============================================================================


class TestPhase5BindTools:
    """Tests for Phase 5: Bind Tools"""

    @pytest.mark.asyncio
    async def test_bind_tools_registers_in_graph(self):
        """Tools are registered in Neo4j."""
        from core.agents.bootstrap.phase_5_bind_tools import bind_tools

        mock_instance = MagicMock()
        mock_instance.agent_id = "test-agent"
        mock_instance.instance_id = "inst-123"

        # Mock tools
        tools = [
            {"tool_id": "memory_search", "name": "memory_search"},
            {"tool_id": "memory_write", "name": "memory_write"},
        ]

        mock_neo4j = AsyncMock()
        mock_neo4j.run_query = AsyncMock(return_value=[])

        with patch(
            "core.agents.bootstrap.phase_5_bind_tools.get_neo4j_client",
            return_value=mock_neo4j,
        ):
            with patch(
                "core.agents.bootstrap.phase_5_bind_tools.get_tool_definitions",
                return_value=tools,
            ):
                errors = await bind_tools(mock_instance)

        assert errors == []


# =============================================================================
# Phase 6: Wire Governance
# =============================================================================


class TestPhase6WireGovernance:
    """Tests for Phase 6: Wire Governance"""

    @pytest.mark.asyncio
    async def test_wire_governance_creates_gates(self):
        """Governance gates are wired for high-risk tools."""
        from core.agents.bootstrap.phase_6_wire_governance import wire_governance

        mock_instance = MagicMock()
        mock_instance.agent_id = "test-agent"
        mock_instance.instance_id = "inst-123"

        kernels = [{"kernel_id": "safety", "rules": ["no destructive ops without approval"]}]

        mock_neo4j = AsyncMock()
        mock_neo4j.run_query = AsyncMock(return_value=[])

        with patch(
            "core.agents.bootstrap.phase_6_wire_governance.get_neo4j_client",
            return_value=mock_neo4j,
        ):
            errors = await wire_governance(mock_instance, kernels)

        assert errors == []


# =============================================================================
# Phase 7: Verify and Lock
# =============================================================================


class TestPhase7VerifyAndLock:
    """Tests for Phase 7: Verify and Lock"""

    @pytest.mark.asyncio
    async def test_verify_smoke_tests_all_systems(self):
        """Smoke tests verify all systems are operational."""
        from core.agents.bootstrap.phase_7_verify_and_lock import verify_and_lock

        mock_instance = MagicMock()
        mock_instance.agent_id = "test-agent"
        mock_instance.instance_id = "inst-123"
        mock_instance.status = "INITIALIZING"

        mock_substrate = AsyncMock()
        mock_substrate.is_ready = MagicMock(return_value=True)
        mock_substrate.write_packet = AsyncMock(return_value=MagicMock(id="pkt-123"))

        mock_neo4j = AsyncMock()
        mock_neo4j.is_available = MagicMock(return_value=True)
        mock_neo4j.run_query = AsyncMock(return_value=[{"ok": True}])

        with patch(
            "core.agents.bootstrap.phase_7_verify_and_lock.get_neo4j_client",
            return_value=mock_neo4j,
        ):
            instance, errors = await verify_and_lock(mock_instance, mock_substrate)

        assert errors == []
        assert instance.status == "READY"
        assert instance.initialization_signature is not None

    @pytest.mark.asyncio
    async def test_verify_fails_on_broken_substrate(self):
        """Verification fails when substrate is down."""
        from core.agents.bootstrap.phase_7_verify_and_lock import verify_and_lock

        mock_instance = MagicMock()
        mock_instance.agent_id = "test-agent"
        mock_instance.instance_id = "inst-123"
        mock_instance.status = "INITIALIZING"

        mock_substrate = AsyncMock()
        mock_substrate.is_ready = MagicMock(return_value=False)

        instance, errors = await verify_and_lock(mock_instance, mock_substrate)

        assert len(errors) > 0
        assert any("substrate" in e.lower() for e in errors)


# =============================================================================
# Orchestrator Tests
# =============================================================================


class TestBootstrapOrchestrator:
    """Tests for the bootstrap orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_all_phases_success(self):
        """Orchestrator runs all 7 phases successfully."""
        from core.agents.bootstrap.orchestrator import AgentBootstrapOrchestrator
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            kernel_refs=["01_master_kernel.yaml"],
        )

        mock_substrate = AsyncMock()
        mock_substrate.is_ready = MagicMock(return_value=True)
        mock_substrate.write_packet = AsyncMock(return_value=MagicMock(id="pkt-123"))

        # Mock all phases to succeed
        with patch(
            "core.agents.bootstrap.orchestrator.validate_blueprint",
            return_value=[],
        ):
            with patch(
                "core.agents.bootstrap.orchestrator.load_kernels",
                return_value=(
                    [{"kernel_id": "master", "hash": "abc123"}],
                    [],
                ),
            ):
                with patch(
                    "core.agents.bootstrap.orchestrator.instantiate_agent",
                    return_value=(
                        MagicMock(
                            agent_id="test-agent",
                            instance_id="inst-123",
                            status="READY",
                            initialization_signature="sig123",
                        ),
                        [],
                    ),
                ):
                    with patch(
                        "core.agents.bootstrap.orchestrator.bind_kernels",
                        return_value=[],
                    ):
                        with patch(
                            "core.agents.bootstrap.orchestrator.load_identity",
                            return_value=[],
                        ):
                            with patch(
                                "core.agents.bootstrap.orchestrator.bind_tools",
                                return_value=[],
                            ):
                                with patch(
                                    "core.agents.bootstrap.orchestrator.wire_governance",
                                    return_value=[],
                                ):
                                    with patch(
                                        "core.agents.bootstrap.orchestrator.verify_and_lock",
                                        return_value=(
                                            MagicMock(
                                                agent_id="test-agent",
                                                instance_id="inst-123",
                                                status="READY",
                                                initialization_signature="sig123",
                                            ),
                                            [],
                                        ),
                                    ):
                                        orchestrator = AgentBootstrapOrchestrator(mock_substrate)
                                        instance = await orchestrator.bootstrap_agent(config)

        assert instance is not None
        assert instance.status == "READY"

    @pytest.mark.asyncio
    async def test_orchestrator_phase_failure_rollback(self):
        """Orchestrator rolls back on phase failure."""
        from core.agents.bootstrap.orchestrator import (
            AgentBootstrapOrchestrator,
            BootstrapError,
        )
        from core.agents.schemas import AgentConfig

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            kernel_refs=["01_master_kernel.yaml"],
        )

        mock_substrate = AsyncMock()
        mock_substrate.is_ready = MagicMock(return_value=True)

        # Phase 0 succeeds, Phase 1 fails
        with patch(
            "core.agents.bootstrap.orchestrator.validate_blueprint",
            return_value=[],
        ):
            with patch(
                "core.agents.bootstrap.orchestrator.load_kernels",
                return_value=([], ["Kernel file not found"]),
            ):
                orchestrator = AgentBootstrapOrchestrator(mock_substrate)

                with pytest.raises(BootstrapError) as exc_info:
                    await orchestrator.bootstrap_agent(config)

                assert "Phase 1" in str(exc_info.value) or "kernel" in str(exc_info.value).lower()

