"""
Tests for L9 Research Factory - Full Extraction Pipeline
=========================================================

Tests the complete extraction pipeline:
- Schema parsing
- Schema validation
- Template rendering
- Code generation
- File writing

Version: 1.0.0
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest

from services.research_factory.schema_parser import (
    AgentSchema,
    SystemBlock,
    IntegrationBlock,
    GovernanceBlock,
    MemoryTopologyBlock,
    MetadataBlock,
    parse_schema,
)
from services.research_factory.schema_validator import (
    SchemaValidator,
    ValidationResult,
    validate_schema,
    validate_schema_yaml,
)
from services.research_factory.glue_resolver import (
    GlueResolver,
    GlueConfig,
    WiringSpec,
    DependencyGraph,
)
from services.research_factory.extractor import (
    UniversalExtractor,
    ExtractionResult,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def minimal_schema_yaml() -> str:
    """Minimal valid schema YAML."""
    return """
system:
  system: Test Agent
  module: test
  name: TestAgent
  role: A test agent for unit testing.
  rootpath: L9/agents/test

integration:
  connectto:
    - L9/core
  shareddomains:
    - TestDomain

governance:
  anchors:
    - Igor
  mode: hybrid
  humanoverride: true
  escalationpolicy: Auto-escalate on errors

memorytopology:
  workingmemory:
    storagetype: redis_cluster
    purpose: Cache for active state

communicationstack:
  input:
    - structuredapi
  output:
    - structuredapi

reasoningengine:
  framework: multimodal_reflective
  model: gpt-4o

collaborationnetwork:
  collaborators: []
  protocol: PacketEnvelope

learningsystem:
  architecture: continuous_metalearning
  modules: []
  feedbackchannels: []

worldmodelintegration:
  enabled: true
  sources:
    - entity_graph

cursorinstructions:
  createifmissing:
    - L9/agents/test
  generatefiles:
    - controller.py
    - __init__.py
  generatedocs:
    - README.md

deployment:
  runtime: python_3.11_async
  endpoints:
    - /agent/test/status
  replicas: 1

metadata:
  version: "6.0.0"
  status: draft
  owner: Test Owner
  tags:
    - test
"""


@pytest.fixture
def complete_schema_yaml() -> str:
    """Complete schema YAML with all sections."""
    return """
title: L9 Complete Test Agent
purpose: Full-featured test agent for integration testing.
summary: A test agent that exercises all schema features.

system:
  system: L9 Complete Test Agent
  module: complete_test
  name: CompleteTestAgent
  role: >
    A comprehensive test agent that exercises all schema features
    for integration testing of the Research Factory.
  rootpath: L9/agents/complete_test

integration:
  connectto:
    - L9/core
    - L9/worldmodel
    - L9/governance
  shareddomains:
    - TestDomain
    - AnotherDomain

governance:
  anchors:
    - Igor
    - Test Anchor
  mode: hybrid
  humanoverride: true
  complianceauditor: L9/governance/test_auditor.py
  escalationpolicy: >
    Auto-escalate if confidence < 0.7 or error rate > 5%
  performancereporting: L9/monitoring/test_dashboard.py
  auditscope:
    - request_processing
    - decision_making
    - error_handling

memorytopology:
  workingmemory:
    storagetype: redis_cluster
    purpose: Active state and cache
    keyspace: testagent:working:*
  episodicmemory:
    storagetype: postgres + pgvector
    purpose: Decision logs and history
    retention: 90 days
    indexby:
      - timestamp
      - request_id
  semanticmemory:
    storagetype: neo4j_auradb
    purpose: Entity relationships
  crossagentsharing:
    enabled: true
    layer: cognition_bus

communicationstack:
  input:
    - structuredapi
    - messagesqueue
  output:
    - structuredapi
    - eventstream
  channels:
    slack: true
    email: false
    api: true

reasoningengine:
  framework: multimodal_reflective
  model: gpt-4o
  secondarymodels:
    - gpt-3.5-turbo
  strategymodes:
    - causal_inference
    - pattern_matching
  temporalscope: rolling_180_days

collaborationnetwork:
  collaborators:
    - name: HelperAgent
      role: Assistant
      interaction: bidirectional
  protocol: PacketEnvelope

learningsystem:
  architecture: continuous_metalearning
  modules:
    - drift_detector
    - pattern_extractor
  feedbackchannels:
    - governance_bus
    - user_feedback

worldmodelintegration:
  enabled: true
  sources:
    - entity_graph
    - market_data
  updatefrequency: realtime

cursorinstructions:
  createifmissing:
    - L9/agents/complete_test
    - L9/agents/complete_test/modules
    - L9/tests/agents/complete_test
  generatefiles:
    - controller.py
    - __init__.py
    - processor.py
    - utils.py
  linkexisting:
    - L9/core/governance.py
  generatedocs:
    - README.md
    - API_SPEC.md

deployment:
  runtime: python_3.11_async
  endpoints:
    - /agent/complete_test/status
    - /agent/complete_test/process
  healthcheck: /agent/complete_test/health
  telemetry:
    metrics: true
    tracing: true
    logging: true
  replicas: 2
  resources:
    cpu: 2
    memory: 4Gi

metadata:
  version: "6.1.0"
  created: "2025-01-15"
  updated: "2025-01-15"
  status: production
  owner: Test Team
  tags:
    - test
    - complete
    - integration
"""


@pytest.fixture
def invalid_schema_yaml() -> str:
    """Schema YAML with validation errors."""
    return """
system:
  system: Invalid Agent
  module: invalid
  name: invalidAgent  # Not PascalCase
  role: Short
  rootpath: L9/agents/invalid

governance:
  mode: invalid_mode  # Invalid mode

deployment:
  endpoints:
    - no_slash_endpoint  # Should start with /
  replicas: 0  # Should be >= 1

metadata:
  version: "5.0.0"  # Below minimum version
  status: unknown_status  # Invalid status
"""


@pytest.fixture
def glue_config_yaml() -> str:
    """Sample glue configuration YAML."""
    return """
wirings:
  - from_agent: MainAgent
    to_agent: TensorAIOS
    connection_type: api_call
    import_path: L9/core/tensoraios/tensor_scorer.py
    method_names:
      - score_candidates
      - generate_embeddings

  - from_agent: PlastOSAdapter
    to_agent: MainAgent
    connection_type: packet_send
    import_path: L9/agents/main/packet_router.py
    packet_types:
      - transaction_batch
      - query

memory_harmonization:
  shared_backends:
    redis: redis://localhost:6379
    postgres: postgresql://localhost:5432/l9

governance_harmonization:
  anchors:
    - Igor
    - Compliance Officer
  shared_escalation_triggers:
    - confidence_drop
    - governance_override

communication_harmonization:
  protocol: PacketEnvelope
  auth: JWT
  encryption: TLS 1.3
"""


# =============================================================================
# Schema Parser Tests
# =============================================================================

class TestSchemaParser:
    """Tests for schema parsing."""
    
    def test_parse_minimal_schema(self, minimal_schema_yaml):
        """Test parsing a minimal valid schema."""
        schema = parse_schema(minimal_schema_yaml)
        
        assert schema is not None
        assert schema.system.name == "TestAgent"
        assert schema.system.module == "test"
        assert schema.governance.mode == "hybrid"
        assert schema.metadata.version == "6.0.0"
    
    def test_parse_complete_schema(self, complete_schema_yaml):
        """Test parsing a complete schema."""
        schema = parse_schema(complete_schema_yaml)
        
        assert schema is not None
        assert schema.system.name == "CompleteTestAgent"
        assert len(schema.integration.connectto) == 3
        assert len(schema.governance.anchors) == 2
        assert schema.memorytopology.workingmemory is not None
        assert schema.memorytopology.episodicmemory is not None
    
    def test_parse_from_dict(self, minimal_schema_yaml):
        """Test parsing from a dictionary."""
        import yaml
        # Use the minimal schema fixture as a dict to ensure all required fields
        data = yaml.safe_load(minimal_schema_yaml)
        
        schema = parse_schema(data)
        
        assert schema is not None
        assert schema.system.name == "TestAgent"
    
    def test_get_agent_id(self, minimal_schema_yaml):
        """Test agent ID generation."""
        schema = parse_schema(minimal_schema_yaml)
        agent_id = schema.get_agent_id()
        
        assert "testagent" in agent_id.lower()
        assert "v6-0-0" in agent_id
    
    def test_parse_invalid_yaml_raises(self):
        """Test that invalid YAML raises an error."""
        import yaml
        with pytest.raises((ValueError, yaml.YAMLError)):
            parse_schema("not: valid: yaml: ::::")


# =============================================================================
# Schema Validator Tests
# =============================================================================

class TestSchemaValidator:
    """Tests for schema validation."""
    
    def test_validate_valid_schema(self, minimal_schema_yaml):
        """Test validating a valid schema."""
        result = validate_schema_yaml(minimal_schema_yaml)
        
        assert result.valid is True
        assert result.error_count == 0
    
    def test_validate_complete_schema(self, complete_schema_yaml):
        """Test validating a complete schema."""
        result = validate_schema_yaml(complete_schema_yaml)
        
        assert result.valid is True
        assert result.error_count == 0
    
    def test_validate_invalid_schema(self, invalid_schema_yaml):
        """Test validating an invalid schema."""
        result = validate_schema_yaml(invalid_schema_yaml)
        
        # Should have validation errors
        assert result.valid is False
        assert result.error_count > 0
    
    def test_version_constraint(self, minimal_schema_yaml):
        """Test version constraint validation."""
        # Modify to use old version
        old_version_yaml = minimal_schema_yaml.replace(
            'version: "6.0.0"',
            'version: "5.0.0"'
        )
        
        result = validate_schema_yaml(old_version_yaml)
        
        # Should fail version check
        assert result.valid is False
        assert any("VERSION" in e.code for e in result.errors)
    
    def test_strict_mode(self, minimal_schema_yaml):
        """Test strict validation mode."""
        validator = SchemaValidator(strict=True)
        schema = parse_schema(minimal_schema_yaml)
        result = validator.validate(schema)
        
        # In strict mode, warnings become errors
        # The minimal schema might have warnings
        if result.warnings:
            assert result.valid is False
    
    def test_validation_result_to_dict(self, minimal_schema_yaml):
        """Test ValidationResult to_dict conversion."""
        result = validate_schema_yaml(minimal_schema_yaml)
        result_dict = result.to_dict()
        
        assert "valid" in result_dict
        assert "errors" in result_dict
        assert "warnings" in result_dict


# =============================================================================
# Glue Resolver Tests
# =============================================================================

class TestGlueResolver:
    """Tests for glue layer resolution."""
    
    def test_parse_glue_config(self, glue_config_yaml):
        """Test parsing glue configuration."""
        resolver = GlueResolver.from_yaml(glue_config_yaml)
        
        assert resolver is not None
        assert len(resolver.config.wirings) == 2
    
    def test_resolve_imports(self, glue_config_yaml):
        """Test resolving imports for an agent."""
        resolver = GlueResolver.from_yaml(glue_config_yaml)
        
        imports = resolver.resolve_imports("MainAgent")
        
        assert len(imports) == 1
        assert "tensor_scorer" in imports[0].module_path
    
    def test_resolve_wirings(self, glue_config_yaml):
        """Test resolving wirings for an agent."""
        resolver = GlueResolver.from_yaml(glue_config_yaml)
        
        wirings = resolver.resolve_wirings("MainAgent")
        
        assert len(wirings) == 1
        assert wirings[0].to_agent == "TensorAIOS"
    
    def test_dependency_order(self, glue_config_yaml):
        """Test getting dependency order."""
        resolver = GlueResolver.from_yaml(glue_config_yaml)
        
        agents = ["MainAgent", "TensorAIOS", "PlastOSAdapter"]
        order = resolver.get_dependency_order(agents)
        
        # TensorAIOS should come before MainAgent
        assert order.index("TensorAIOS") < order.index("MainAgent")
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        graph = DependencyGraph()
        graph.add_dependency("A", "B")
        graph.add_dependency("B", "C")
        graph.add_dependency("C", "A")  # Creates cycle
        
        has_cycle, cycle = graph.has_circular_dependency()
        
        assert has_cycle is True
        assert cycle is not None
        assert len(cycle) >= 3
    
    def test_parallel_groups(self, glue_config_yaml):
        """Test getting parallel extraction groups."""
        resolver = GlueResolver.from_yaml(glue_config_yaml)
        
        agents = ["MainAgent", "TensorAIOS", "PlastOSAdapter"]
        groups = resolver.get_parallel_extraction_groups(agents)
        
        assert len(groups) > 0
        # TensorAIOS should be in an early group
        assert any("TensorAIOS" in group for group in groups)


# =============================================================================
# Extractor Tests
# =============================================================================

class TestUniversalExtractor:
    """Tests for the universal extractor."""
    
    def test_create_extractor(self):
        """Test creating an extractor."""
        extractor = UniversalExtractor()
        
        assert extractor is not None
    
    def test_list_templates(self):
        """Test listing available templates."""
        extractor = UniversalExtractor()
        templates = extractor.list_templates()
        
        assert len(templates) > 0
        assert "controller.py.j2" in templates
    
    @pytest.mark.asyncio
    async def test_extract_dry_run(self, minimal_schema_yaml):
        """Test extraction in dry run mode."""
        extractor = UniversalExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=minimal_schema_yaml,
                output_dir=tmpdir,
                dry_run=True,
            )
            
            assert result.success is True
            assert len(result.generated_files) > 0
            
            # Dry run should not create files
            assert not Path(tmpdir).joinpath("controller.py").exists()
    
    @pytest.mark.asyncio
    async def test_extract_writes_files(self, minimal_schema_yaml):
        """Test that extraction writes files."""
        extractor = UniversalExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=minimal_schema_yaml,
                output_dir=tmpdir,
                dry_run=False,
            )
            
            assert result.success is True
            
            # Files should be created
            assert Path(tmpdir).joinpath("controller.py").exists()
            assert Path(tmpdir).joinpath("__init__.py").exists()
            assert Path(tmpdir).joinpath("README.md").exists()
    
    @pytest.mark.asyncio
    async def test_extract_creates_manifest(self, minimal_schema_yaml):
        """Test that extraction creates a manifest."""
        extractor = UniversalExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=minimal_schema_yaml,
                output_dir=tmpdir,
                dry_run=False,
            )
            
            assert result.manifest is not None
            assert result.manifest.agent_name == "TestAgent"
            
            # Manifest file should be created
            assert Path(tmpdir).joinpath("manifest.json").exists()
    
    @pytest.mark.asyncio
    async def test_extract_with_glue(self, complete_schema_yaml, glue_config_yaml):
        """Test extraction with glue configuration."""
        from services.research_factory.glue_resolver import load_glue_config
        import yaml
        
        extractor = UniversalExtractor()
        
        glue_data = yaml.safe_load(glue_config_yaml)
        glue = GlueConfig.model_validate(glue_data)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=complete_schema_yaml,
                output_dir=tmpdir,
                glue=glue,
                dry_run=True,
            )
            
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_extract_invalid_schema(self, invalid_schema_yaml):
        """Test extraction with invalid schema."""
        extractor = UniversalExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=invalid_schema_yaml,
                output_dir=tmpdir,
                dry_run=True,
            )
            
            # Should fail validation
            assert result.success is False
            assert len(result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_extract_overwrite_protection(self, minimal_schema_yaml):
        """Test that overwrite protection works."""
        extractor = UniversalExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # First extraction
            await extractor.extract(
                schema=minimal_schema_yaml,
                output_dir=tmpdir,
                dry_run=False,
            )
            
            # Second extraction without overwrite should warn
            result = await extractor.extract(
                schema=minimal_schema_yaml,
                output_dir=tmpdir,
                dry_run=False,
                overwrite=False,
            )
            
            # Should have warnings about existing files
            assert len(result.warnings) > 0
    
    @pytest.mark.asyncio
    async def test_validate_only(self, minimal_schema_yaml):
        """Test validation-only mode."""
        extractor = UniversalExtractor()
        
        result = await extractor.validate_only(minimal_schema_yaml)
        
        assert result is not None
        assert result.valid is True


# =============================================================================
# Integration Tests
# =============================================================================

class TestFullPipeline:
    """Integration tests for the full extraction pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, complete_schema_yaml, glue_config_yaml):
        """Test the complete extraction pipeline."""
        import yaml
        
        # Step 1: Parse schema
        schema = parse_schema(complete_schema_yaml)
        assert schema is not None
        
        # Step 2: Validate schema
        validation = validate_schema(schema)
        assert validation.valid is True
        
        # Step 3: Parse glue config
        glue_data = yaml.safe_load(glue_config_yaml)
        glue = GlueConfig.model_validate(glue_data)
        assert glue is not None
        
        # Step 4: Extract
        extractor = UniversalExtractor()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=schema,
                output_dir=tmpdir,
                glue=glue,
                dry_run=False,
            )
            
            # Step 5: Verify results
            assert result.success is True
            assert len(result.generated_files) >= 3  # controller, init, readme
            assert result.manifest is not None
            
            # Check files exist
            output_path = Path(tmpdir)
            assert (output_path / "controller.py").exists()
            assert (output_path / "__init__.py").exists()
            assert (output_path / "README.md").exists()
            assert (output_path / "manifest.json").exists()
            
            # Check controller content
            controller_content = (output_path / "controller.py").read_text()
            assert "CompleteTestAgent" in controller_content
            assert "class CompleteTestAgentController" in controller_content
    
    @pytest.mark.asyncio
    async def test_generated_code_is_valid_python(self, minimal_schema_yaml):
        """Test that generated Python code is syntactically valid."""
        import ast
        
        extractor = UniversalExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await extractor.extract(
                schema=minimal_schema_yaml,
                output_dir=tmpdir,
                dry_run=False,
            )
            
            assert result.success is True
            
            # Check controller.py is valid Python
            controller_path = Path(tmpdir) / "controller.py"
            controller_content = controller_path.read_text()
            
            # This will raise SyntaxError if invalid
            ast.parse(controller_content)
            
            # Check __init__.py is valid Python
            init_path = Path(tmpdir) / "__init__.py"
            init_content = init_path.read_text()
            ast.parse(init_content)

