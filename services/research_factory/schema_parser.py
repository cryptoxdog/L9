"""
L9 Research Factory - Schema Parser
====================================

Parses YAML agent schemas into validated Pydantic models.

The Research Factory schema format (v6.0+) requires 12 sections:
1. system - Agent identity and role
2. integration - Dependencies and wiring points
3. governance - Escalation, compliance, audit scope
4. memorytopology - Working/episodic/semantic/causal/archive memory
5. communicationstack - Input/output/channels
6. reasoningengine - Logic framework and modes
7. collaborationnetwork - Partners and interaction protocol
8. learningsystem - Feedback loops and autonomy profile
9. worldmodelintegration - External context integration
10. cursorinstructions - File generation directives
11. deployment - Runtime, endpoints, telemetry
12. metadata - Version, owner, status

Version: 1.0.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# =============================================================================
# Block 1: System Block
# =============================================================================

class SystemBlock(BaseModel):
    """
    Agent identity and role definition.
    
    Example:
        system: L9 Main Agent
        module: coreagent
        name: MainAgent
        role: Central Domain-Tensor Orchestrator...
        rootpath: L9/agents/main
    """
    system: str = Field(..., description="Full agent name/identity")
    module: str = Field(..., description="Functional area/module name")
    name: str = Field(..., description="PascalCase agent name")
    role: str = Field(..., description="Agent role description (2-3 sentences)")
    rootpath: str = Field(..., description="Base path for generated code")
    
    @field_validator("name")
    @classmethod
    def validate_name_pascal_case(cls, v: str) -> str:
        """Ensure name is PascalCase."""
        if not v[0].isupper():
            raise ValueError(f"Agent name must be PascalCase, got: {v}")
        return v


# =============================================================================
# Block 2: Integration Block
# =============================================================================

class IntegrationBlock(BaseModel):
    """
    Dependencies and wiring points.
    
    Example:
        integration:
          connectto:
            - L9/core
            - L9/worldmodel
          shareddomains:
            - PlastOS
            - MortgageOS
    """
    connectto: list[str] = Field(default_factory=list, description="Paths this agent connects to")
    shareddomains: list[str] = Field(default_factory=list, description="Domains this agent serves")


# =============================================================================
# Block 3: Governance Block
# =============================================================================

class GovernanceBlock(BaseModel):
    """
    Escalation, compliance, and audit configuration.
    
    Example:
        governance:
          anchors:
            - Igor
            - Compliance Officer
          mode: hybrid
          humanoverride: true
          escalationpolicy: Auto-escalate if confidence < 0.7
          auditscope:
            - packet_reception
            - reasoning_decisions
    """
    anchors: list[str] = Field(default_factory=list, description="Human oversight anchors")
    mode: str = Field(default="hybrid", description="Governance mode: hybrid|autonomous|supervised")
    humanoverride: bool = Field(default=True, description="Allow human override")
    complianceauditor: Optional[str] = Field(None, description="Path to compliance auditor script")
    escalationpolicy: Optional[str] = Field(None, description="When to escalate decisions")
    performancereporting: Optional[str] = Field(None, description="Path to performance dashboard")
    auditscope: list[str] = Field(default_factory=list, description="What to audit")
    
    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate governance mode."""
        valid_modes = {"hybrid", "autonomous", "supervised"}
        if v.lower() not in valid_modes:
            raise ValueError(f"Invalid governance mode: {v}. Must be one of: {valid_modes}")
        return v.lower()


# =============================================================================
# Block 4: Memory Topology Block
# =============================================================================

class MemoryLayerConfig(BaseModel):
    """Configuration for a single memory layer."""
    storagetype: str = Field(..., description="Storage backend type")
    purpose: str = Field(..., description="What this layer stores")
    keyspace: Optional[str] = Field(None, description="Key pattern for Redis-like storage")
    retention: Optional[str] = Field(None, description="Data retention policy")
    indexby: Optional[list[str]] = Field(None, description="Index fields")
    structure: Optional[list[dict[str, Any]]] = Field(None, description="Graph structure definition")
    schema: Optional[list[dict[str, Any]]] = Field(None, description="Causal schema definition")


class CrossAgentSharingConfig(BaseModel):
    """Cross-agent memory sharing configuration."""
    enabled: bool = Field(default=False)
    layer: Optional[str] = Field(None, description="Sharing layer name")


class MemoryTopologyBlock(BaseModel):
    """
    Multi-layer memory architecture.
    
    Layers:
    - workingmemory: Fast cache (Redis)
    - episodicmemory: Decision logs (PostgreSQL)
    - semanticmemory: Entity graphs (Neo4j)
    - causalmemory: Reasoning traces (HypergraphDB)
    - longtermpersistence: Archive (S3)
    """
    workingmemory: Optional[MemoryLayerConfig] = None
    episodicmemory: Optional[MemoryLayerConfig] = None
    semanticmemory: Optional[MemoryLayerConfig] = None
    causalmemory: Optional[MemoryLayerConfig] = None
    longtermpersistence: Optional[MemoryLayerConfig] = None
    crossagentsharing: Optional[CrossAgentSharingConfig] = None


# =============================================================================
# Block 5: Communication Stack Block
# =============================================================================

class ChannelConfig(BaseModel):
    """Communication channel configuration."""
    slack: bool = Field(default=False)
    email: bool = Field(default=False)
    webhook: bool = Field(default=False)
    api: bool = Field(default=True)


class CommunicationStackBlock(BaseModel):
    """
    Input/output communication configuration.
    
    Example:
        communicationstack:
          input: [structuredapi, messagesqueue]
          output: [structuredapi, eventstream]
          channels:
            slack: true
            email: false
    """
    input: list[str] = Field(default_factory=list, description="Input methods")
    output: list[str] = Field(default_factory=list, description="Output methods")
    channels: Optional[ChannelConfig] = None


# =============================================================================
# Block 6: Reasoning Engine Block
# =============================================================================

class KnowledgeFusionConfig(BaseModel):
    """Knowledge fusion layer configuration."""
    mode: str = Field(default="blend", description="Fusion mode")
    sourceblend: list[str] = Field(default_factory=list, description="Sources to blend")


class ReasoningFeedbackConfig(BaseModel):
    """Reasoning feedback loop configuration."""
    policy: str = Field(default="reinforcement_reflection")
    rewardfunction: Optional[str] = Field(None, description="How to measure success")
    penaltyfunction: Optional[str] = Field(None, description="How to measure failure")
    retrainintervalhours: int = Field(default=168, description="Hours between retraining")


class ReasoningEngineBlock(BaseModel):
    """
    Logic framework and reasoning modes.
    
    Example:
        reasoningengine:
          framework: multimodal_reflective
          model: gpt4_orchestrator
          strategymodes:
            - causal_inference
            - pattern_matching
    """
    framework: str = Field(default="multimodal_reflective", description="Reasoning framework")
    model: str = Field(default="gpt-4o", description="Primary LLM model")
    secondarymodels: list[str] = Field(default_factory=list, description="Supporting models")
    strategymodes: list[str] = Field(default_factory=list, description="Available reasoning strategies")
    temporalscope: Optional[str] = Field(None, description="Temporal context window")
    knowledgefusionlayer: Optional[KnowledgeFusionConfig] = None
    reasoningfeedbackloop: Optional[ReasoningFeedbackConfig] = None


# =============================================================================
# Block 7: Collaboration Network Block
# =============================================================================

class CollaboratorConfig(BaseModel):
    """Configuration for a collaborating agent."""
    name: str
    role: str
    interaction: str = Field(default="bidirectional")


class CollaborationNetworkBlock(BaseModel):
    """
    Partner agents and interaction protocols.
    
    Example:
        collaborationnetwork:
          collaborators:
            - name: TensorAIOS
              role: Neural scoring
              interaction: api_call
    """
    collaborators: list[CollaboratorConfig] = Field(default_factory=list)
    protocol: str = Field(default="PacketEnvelope", description="Communication protocol")


# =============================================================================
# Block 8: Learning System Block
# =============================================================================

class AutonomyProfileConfig(BaseModel):
    """Autonomy profile configuration."""
    mode: str = Field(default="controlled_autonomy")
    tasklimit: Optional[str] = Field(None, description="Max parallel tasks")
    decisionlatencymaxms: int = Field(default=1000, description="Max decision latency")
    escalationtriggers: list[str] = Field(default_factory=list)


class LearningSystemBlock(BaseModel):
    """
    Feedback loops and autonomy profile.
    
    Example:
        learningsystem:
          architecture: continuous_metalearning
          modules:
            - drift_detector
            - pattern_extractor
          feedbackchannels:
            - governance_bus
            - user_feedback
    """
    architecture: str = Field(default="continuous_metalearning")
    modules: list[str] = Field(default_factory=list, description="Learning modules")
    feedbackchannels: list[str] = Field(default_factory=list, description="Feedback sources")
    autonomyprofile: Optional[AutonomyProfileConfig] = None


# =============================================================================
# Block 9: World Model Integration Block
# =============================================================================

class WorldModelIntegrationBlock(BaseModel):
    """
    External context integration.
    
    Example:
        worldmodelintegration:
          enabled: true
          sources:
            - market_data
            - entity_graph
          updatefrequency: realtime
    """
    enabled: bool = Field(default=True)
    sources: list[str] = Field(default_factory=list, description="World model data sources")
    updatefrequency: str = Field(default="realtime", description="How often to update")
    contextwindow: Optional[str] = Field(None, description="Context window size")


# =============================================================================
# Block 10: Cursor Instructions Block
# =============================================================================

class CursorInstructionsBlock(BaseModel):
    """
    File generation directives for code extraction.
    
    Example:
        cursorinstructions:
          createifmissing:
            - L9/agents/main
            - L9/agents/main/modules
          generatefiles:
            - controller.py
            - router.py
          linkexisting:
            - L9/core/governance.py
          generatedocs:
            - README.md
            - API_SPEC.md
    """
    createifmissing: list[str] = Field(default_factory=list, description="Directories to create")
    generatefiles: list[str] = Field(default_factory=list, description="Files to generate")
    linkexisting: list[str] = Field(default_factory=list, description="Existing files to link")
    generatedocs: list[str] = Field(default_factory=list, description="Documentation to generate")
    postgeneration: Optional[dict[str, Any]] = Field(None, description="Post-generation actions")


# =============================================================================
# Block 11: Deployment Block
# =============================================================================

class TelemetryConfig(BaseModel):
    """Telemetry configuration."""
    metrics: bool = Field(default=True)
    tracing: bool = Field(default=True)
    logging: bool = Field(default=True)
    dashboardpath: Optional[str] = Field(None)


class DeploymentBlock(BaseModel):
    """
    Runtime, endpoints, and telemetry configuration.
    
    Example:
        deployment:
          runtime: python_3.11_async
          endpoints:
            - /agent/main/status
            - /agent/main/process
          telemetry:
            metrics: true
            tracing: true
    """
    runtime: str = Field(default="python_3.11_async", description="Runtime environment")
    endpoints: list[str] = Field(default_factory=list, description="API endpoints to expose")
    healthcheck: Optional[str] = Field(None, description="Health check endpoint")
    telemetry: Optional[TelemetryConfig] = None
    replicas: int = Field(default=1, description="Number of replicas")
    resources: Optional[dict[str, Any]] = Field(None, description="Resource requirements")


# =============================================================================
# Block 12: Metadata Block
# =============================================================================

class MetadataBlock(BaseModel):
    """
    Version, owner, and status information.
    
    Example:
        metadata:
          version: 6.0.0
          created: 2025-01-01
          updated: 2025-01-15
          owner: L9 System Architect
          status: production
          tags:
            - core-agent
            - orchestration
    """
    version: str = Field(default="1.0.0", description="Schema version")
    created: Optional[str] = Field(None, description="Creation date")
    updated: Optional[str] = Field(None, description="Last update date")
    owner: Optional[str] = Field(None, description="Schema owner")
    status: str = Field(default="draft", description="Status: draft|review|production")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        valid_statuses = {"draft", "review", "production", "deprecated"}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Invalid status: {v}. Must be one of: {valid_statuses}")
        return v.lower()


# =============================================================================
# Main Agent Schema Model
# =============================================================================

class AgentSchema(BaseModel):
    """
    Complete agent schema model with all 12 required sections.
    
    This is the main model that represents a parsed Research Factory schema.
    """
    # Required identity fields (parsed from YAML frontmatter or system block)
    title: Optional[str] = Field(None, description="Schema title")
    purpose: Optional[str] = Field(None, description="Agent purpose")
    summary: Optional[str] = Field(None, description="Agent summary")
    description: Optional[str] = Field(None, description="Detailed description")
    
    # The 12 required blocks - ALL REQUIRED, NO DEFAULTS
    # v2.5: Missing sections = HARD FAIL
    system: SystemBlock = Field(..., description="Agent identity and role")
    integration: IntegrationBlock = Field(..., description="Dependencies and wiring points")
    governance: GovernanceBlock = Field(..., description="Escalation, compliance, audit scope")
    memorytopology: MemoryTopologyBlock = Field(..., description="Memory layer configuration")
    communicationstack: CommunicationStackBlock = Field(..., description="Input/output/channels")
    reasoningengine: ReasoningEngineBlock = Field(..., description="Logic framework and modes")
    collaborationnetwork: CollaborationNetworkBlock = Field(..., description="Partners and protocol")
    learningsystem: LearningSystemBlock = Field(..., description="Feedback loops and autonomy")
    worldmodelintegration: WorldModelIntegrationBlock = Field(..., description="External context integration")
    cursorinstructions: CursorInstructionsBlock = Field(..., description="File generation directives")
    deployment: DeploymentBlock = Field(..., description="Runtime, endpoints, telemetry")
    metadata: MetadataBlock = Field(..., description="Version, owner, status")
    
    # STRICT: Reject unknown fields
    model_config = {"extra": "forbid"}
    
    def get_agent_id(self) -> str:
        """Generate a unique agent ID from the schema."""
        name = self.system.name.lower().replace(" ", "-")
        version = self.metadata.version.replace(".", "-")
        return f"{name}-v{version}"
    
    def get_output_path(self) -> Path:
        """Get the output path for generated code."""
        return Path(self.system.rootpath)


# =============================================================================
# Parsing Functions
# =============================================================================

def parse_schema(source: str | Path | dict[str, Any]) -> AgentSchema:
    """
    Parse a YAML schema into an AgentSchema model.
    
    Args:
        source: YAML string, file path, or pre-parsed dict
        
    Returns:
        Validated AgentSchema instance
        
    Raises:
        ValueError: If schema is invalid
        FileNotFoundError: If file path doesn't exist
    """
    # Handle different input types
    if isinstance(source, dict):
        data = source
    elif isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {path}")
        with open(path, "r") as f:
            content = f.read()
        data = yaml.safe_load(content)
    else:
        # Assume it's a YAML string
        data = yaml.safe_load(source)
    
    if data is None:
        raise ValueError("Empty schema")
    
    # Handle system block that might be a string (e.g., "system: L9 Main Agent")
    if "system" in data and isinstance(data["system"], str):
        # Convert string-style system to block format
        system_name = data["system"]
        data["system"] = {
            "system": system_name,
            "module": data.get("module", "agent"),
            "name": data.get("name", system_name.replace(" ", "")),
            "role": data.get("role", data.get("description", "")),
            "rootpath": data.get("rootpath", f"L9/agents/{system_name.lower().replace(' ', '_')}"),
        }
    
    # Parse and validate
    try:
        schema = AgentSchema.model_validate(data)
        logger.info(
            "Parsed schema: agent=%s, version=%s",
            schema.system.name,
            schema.metadata.version,
        )
        return schema
    except Exception as e:
        logger.error("Failed to parse schema: %s", str(e))
        raise ValueError(f"Invalid schema: {e}") from e


def parse_schema_file(filepath: str | Path) -> AgentSchema:
    """
    Parse a schema from a file path.
    
    Args:
        filepath: Path to YAML schema file
        
    Returns:
        Validated AgentSchema instance
    """
    return parse_schema(Path(filepath))


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Main schema
    "AgentSchema",
    # Block models
    "SystemBlock",
    "IntegrationBlock",
    "GovernanceBlock",
    "MemoryTopologyBlock",
    "CommunicationStackBlock",
    "ReasoningEngineBlock",
    "CollaborationNetworkBlock",
    "LearningSystemBlock",
    "WorldModelIntegrationBlock",
    "CursorInstructionsBlock",
    "DeploymentBlock",
    "MetadataBlock",
    # Sub-models
    "MemoryLayerConfig",
    "ChannelConfig",
    "CollaboratorConfig",
    "TelemetryConfig",
    # Functions
    "parse_schema",
    "parse_schema_file",
]

