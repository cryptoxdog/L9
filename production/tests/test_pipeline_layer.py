"""
Comprehensive Test Suite for L9 Pipeline Layer
Tests orchestration engine, deployment automation, rollback system, and environment sync
"""

import pytest
import asyncio
import json
import logging
import tempfile
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import L9 Pipeline Layer components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from pipeline.orchestration_engine import (
    ProductionOrchestrator, DeploymentConfig, DeploymentStrategy,
    DeploymentStatus, DeploymentResult, HealthChecker,
    BlueGreenDeployment, CanaryDeployment, RollingDeployment
)
from pipeline.deployment_automation import (
    MultiEnvironmentDeployer, EnvironmentConfig, Environment,
    DeploymentType, ArtifactManager, DeploymentValidator
)
from pipeline.rollback_system import (
    AutomatedRollbackSystem, RollbackConfig, RollbackTrigger, 
    MetricsCollector, RollbackDecisionEngine
)
from pipeline.environment_sync import (
    EnvironmentSynchronizer, ConfigType, SyncStatus, 
    ConfigurationManager, SecretsManager
)

class TestOrchestrationEngine:
    """Test production orchestration engine"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "orchestrator.yaml"
            config_data = {
                'deployment_strategies': ['blue_green', 'canary', 'rolling'],
                'health_check_timeout': 300,
                'rollback_on_failure': True
            }
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            yield str(config_path)
    
    @pytest.fixture
    def mock_orchestrator(self, temp_config_dir):
        """Mock production orchestrator"""
        return ProductionOrchestrator(temp_config_dir)
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_orchestrator):
        """Test orchestrator initialization"""
        assert mock_orchestrator is not None
        assert hasattr(mock_orchestrator, 'deployment_strategies')
        assert DeploymentStrategy.BLUE_GREEN in mock_orchestrator.deployment_strategies
        assert DeploymentStrategy.CANARY in mock_orchestrator.deployment_strategies
        assert DeploymentStrategy.ROLLING in mock_orchestrator.deployment_strategies
    
    @pytest.mark.asyncio
    async def test_blue_green_deployment(self, mock_orchestrator):
        """Test blue-green deployment strategy"""
        deployment_config = DeploymentConfig(
            strategy=DeploymentStrategy.BLUE_GREEN,
            environment="staging",
            version="v1.2.0",
            health_check_url="http://staging.example.com/health"
        )
        
        deployment_context = {
            'artifact_path': '/tmp/artifacts/v1.2.0',
            'instances': ['instance-1', 'instance-2']
        }
        
        # Mock the deployment execution
        with patch.object(BlueGreenDeployment, 'deploy', new_callable=AsyncMock) as mock_deploy:
            mock_deploy.return_value = Mock(
                deployment_id="bg-123456",
                status=DeploymentStatus.SUCCESS,
                strategy=DeploymentStrategy.BLUE_GREEN,
                environment="staging",
                version="v1.2.0",
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=None
            )
            
            result = await mock_orchestrator.deploy(deployment_config, deployment_context)
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.strategy == DeploymentStrategy.BLUE_GREEN
            assert result.version == "v1.2.0"
            mock_deploy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_canary_deployment(self, mock_orchestrator):
        """Test canary deployment strategy"""
        deployment_config = DeploymentConfig(
            strategy=DeploymentStrategy.CANARY,
            environment="production",
            version="v1.2.1",
            health_check_url="http://prod.example.com/health"
        )
        
        with patch.object(CanaryDeployment, 'deploy', new_callable=AsyncMock) as mock_deploy:
            mock_deploy.return_value = Mock(
                deployment_id="canary-789012",
                status=DeploymentStatus.SUCCESS,
                strategy=DeploymentStrategy.CANARY,
                environment="production",
                version="v1.2.1"
            )
            
            result = await mock_orchestrator.deploy(deployment_config)
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.strategy == DeploymentStrategy.CANARY
            mock_deploy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rolling_deployment(self, mock_orchestrator):
        """Test rolling deployment strategy"""
        deployment_config = DeploymentConfig(
            strategy=DeploymentStrategy.ROLLING,
            environment="production",
            version="v1.2.2"
        )
        
        deployment_context = {
            'instances': ['prod-1', 'prod-2', 'prod-3', 'prod-4']
        }
        
        with patch.object(RollingDeployment, 'deploy', new_callable=AsyncMock) as mock_deploy:
            mock_deploy.return_value = Mock(
                deployment_id="rolling-345678",
                status=DeploymentStatus.SUCCESS,
                strategy=DeploymentStrategy.ROLLING,
                environment="production",
                version="v1.2.2"
            )
            
            result = await mock_orchestrator.deploy(deployment_config, deployment_context)
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.strategy == DeploymentStrategy.ROLLING
            mock_deploy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deployment_rollback(self, mock_orchestrator):
        """Test deployment rollback functionality"""
        # Add a successful deployment to history
        successful_deployment = Mock(
            deployment_id="success-123",
            status=DeploymentStatus.SUCCESS,
            environment="staging",
            version="v1.1.0",
            start_time=datetime.now() - timedelta(hours=1)
        )
        mock_orchestrator.deployment_history.append(successful_deployment)
        
        # Mock rollback execution
        with patch.object(mock_orchestrator, 'deploy', new_callable=AsyncMock) as mock_deploy:
            mock_deploy.return_value = Mock(
                deployment_id="rollback-456",
                status=DeploymentStatus.SUCCESS,
                strategy=DeploymentStrategy.DIRECT,
                environment="staging",
                version="v1.1.0"
            )
            
            result = await mock_orchestrator.rollback("staging")
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.version == "v1.1.0"
            mock_deploy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deployment_status_tracking(self, mock_orchestrator):
        """Test deployment status tracking"""
        # Add deployment to history
        deployment = Mock(
            deployment_id="test-deployment-123",
            status=DeploymentStatus.SUCCESS,
            environment="test",
            version="v1.0.0"
        )
        mock_orchestrator.deployment_history.append(deployment)
        
        # Test status retrieval
        status = await mock_orchestrator.get_deployment_status("test-deployment-123")
        
        assert status is not None
        assert status.deployment_id == "test-deployment-123"
        assert status.status == DeploymentStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_deployment_history_listing(self, mock_orchestrator):
        """Test deployment history listing"""
        # Add multiple deployments
        for i in range(5):
            deployment = Mock(
                deployment_id=f"deploy-{i}",
                status=DeploymentStatus.SUCCESS,
                environment="test",
                version=f"v1.0.{i}"
            )
            mock_orchestrator.deployment_history.append(deployment)
        
        # Test history retrieval
        history = await mock_orchestrator.list_deployments("test", limit=3)
        
        assert len(history) == 3
        assert all(d.environment == "test" for d in history)

class TestDeploymentAutomation:
    """Test multi-environment deployment automation"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Create environment configs
            env_dir = config_dir / "environments"
            env_dir.mkdir(parents=True)
            
            # Development environment
            dev_config = {
                'name': 'development',
                'type': 'development',
                'base_url': 'http://dev.example.com',
                'health_check_endpoint': '/health',
                'deployment_strategy': 'direct',
                'auto_promote': True
            }
            with open(env_dir / "development.yaml", 'w') as f:
                yaml.dump(dev_config, f)
            
            # Production environment
            prod_config = {
                'name': 'production',
                'type': 'production',
                'base_url': 'http://prod.example.com',
                'health_check_endpoint': '/health',
                'deployment_strategy': 'blue_green',
                'approval_required': True
            }
            with open(env_dir / "production.yaml", 'w') as f:
                yaml.dump(prod_config, f)
            
            yield str(config_dir)
    
    @pytest.fixture
    def mock_deployer(self, temp_config_dir):
        """Mock multi-environment deployer"""
        return MultiEnvironmentDeployer(temp_config_dir, str(Path(temp_config_dir) / "artifacts"))
    
    @pytest.mark.asyncio
    async def test_environment_deployment(self, mock_deployer):
        """Test deployment to specific environment"""
        # Mock artifact creation
        with patch.object(mock_deployer.artifact_manager, 'get_artifact', new_callable=AsyncMock) as mock_artifact:
            mock_artifact.return_value = "/tmp/artifacts/v1.0.0"
            
            # Mock orchestrator deployment
            with patch.object(mock_deployer, '_get_orchestrator') as mock_get_orchestrator:
                mock_orchestrator = Mock()
                mock_orchestrator.deploy = AsyncMock(return_value=Mock(
                    deployment_id="env-deploy-123",
                    status=DeploymentStatus.SUCCESS,
                    environment="development",
                    version="v1.0.0"
                ))
                mock_get_orchestrator.return_value = mock_orchestrator
                
                result = await mock_deployer.deploy_to_environment("development", "v1.0.0")
                
                assert result.status == DeploymentStatus.SUCCESS
                assert result.environment == "development"
                assert result.version == "v1.0.0"
    
    @pytest.mark.asyncio
    async def test_pipeline_deployment(self, mock_deployer):
        """Test deployment through pipeline"""
        # Mock environment configurations
        dev_env = EnvironmentConfig(
            name="development",
            type=Environment.DEVELOPMENT,
            base_url="http://dev.example.com",
            health_check_endpoint="/health",
            deployment_strategy=DeploymentStrategy.DIRECT,
            auto_promote=True
        )
        
        staging_env = EnvironmentConfig(
            name="staging",
            type=Environment.STAGING,
            base_url="http://staging.example.com",
            health_check_endpoint="/health",
            deployment_strategy=DeploymentStrategy.BLUE_GREEN,
            auto_promote=True
        )
        
        # Mock pipeline
        mock_deployer.env_manager.pipelines["test-pipeline"] = Mock(
            name="test-pipeline",
            environments=[dev_env, staging_env],
            promotion_rules={"staging": ["development"]}
        )
        
        # Mock successful deployments
        with patch.object(mock_deployer, 'deploy_to_environment', new_callable=AsyncMock) as mock_deploy:
            mock_deploy.side_effect = [
                Mock(deployment_id="dev-123", status=DeploymentStatus.SUCCESS, environment="development"),
                Mock(deployment_id="staging-456", status=DeploymentStatus.SUCCESS, environment="staging")
            ]
            
            results = await mock_deployer.deploy_pipeline("test-pipeline", "v1.0.0", auto_promote=True)
            
            assert len(results) == 2
            assert "development" in results
            assert "staging" in results
            assert results["development"].status == DeploymentStatus.SUCCESS
            assert results["staging"].status == DeploymentStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_version_promotion(self, mock_deployer):
        """Test version promotion between environments"""
        # Add deployment history
        dev_deployment = Mock(
            deployment_id="dev-promote-test",
            status=DeploymentStatus.SUCCESS,
            environment="development",
            version="v1.0.0"
        )
        mock_deployer.deployment_history.append(dev_deployment)
        
        # Mock promotion deployment
        with patch.object(mock_deployer, 'deploy_to_environment', new_callable=AsyncMock) as mock_deploy:
            mock_deploy.return_value = Mock(
                deployment_id="staging-promoted",
                status=DeploymentStatus.SUCCESS,
                environment="staging",
                version="v1.0.0"
            )
            
            result = await mock_deployer.promote_version("development", "staging")
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.environment == "staging"
            assert result.version == "v1.0.0"
            mock_deploy.assert_called_once_with("staging", "v1.0.0")
    
    @pytest.mark.asyncio
    async def test_environment_status(self, mock_deployer):
        """Test environment status retrieval"""
        # Add deployment history
        deployment = Mock(
            deployment_id="status-test",
            status=DeploymentStatus.SUCCESS,
            environment="development",
            version="v1.0.0"
        )
        mock_deployer.deployment_history.append(deployment)
        
        # Mock health check
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            status = await mock_deployer.get_environment_status("development")
            
            assert status["environment"] == "development"
            assert status["current_version"] == "v1.0.0"
            assert status["health_status"] == "healthy"

class TestRollbackSystem:
    """Test automated rollback system"""
    
    @pytest.fixture
    def mock_rollback_config(self):
        """Mock rollback configuration"""
        return RollbackConfig(
            enabled=True,
            health_check_failures_threshold=3,
            error_rate_threshold=0.05,
            performance_degradation_threshold=0.3,
            monitoring_window_minutes=10
        )
    
    @pytest.fixture
    def mock_rollback_system(self, mock_rollback_config):
        """Mock automated rollback system"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(mock_rollback_config.__dict__, f)
            config_path = f.name
        
        return AutomatedRollbackSystem(config_path)
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, mock_rollback_system):
        """Test metrics collection for rollback decisions"""
        metrics_collector = MetricsCollector()
        
        # Test metrics collection
        metrics = await metrics_collector.collect_metrics(
            "test-env", 
            "http://test.example.com/health"
        )
        
        assert 'timestamp' in metrics
        assert 'environment' in metrics
        assert 'health_status' in metrics
        assert 'error_rate' in metrics
        assert 'response_time' in metrics
        assert metrics['environment'] == "test-env"
    
    @pytest.mark.asyncio
    async def test_rollback_decision_engine(self, mock_rollback_system):
        """Test rollback decision making"""
        decision_engine = mock_rollback_system.decision_engine
        
        # Test with high error rate (should trigger rollback)
        with patch.object(decision_engine.metrics_collector, 'collect_metrics', new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = {
                'health_status': True,
                'error_rate': 0.15,  # Above threshold
                'response_time': 2.0,
                'cpu_usage': 50.0,
                'memory_usage': 60.0
            }
            
            should_rollback, trigger, metrics = await decision_engine.should_rollback(
                "test-env", "http://test.example.com/health"
            )
            
            assert should_rollback == True
            assert trigger == RollbackTrigger.ERROR_RATE_THRESHOLD
            assert metrics['error_rate'] == 0.15
    
    @pytest.mark.asyncio
    async def test_rollback_execution(self, mock_rollback_system):
        """Test rollback execution"""
        # Mock active deployment
        active_deployment = Mock(
            deployment_id="active-123",
            status=DeploymentStatus.SUCCESS,
            environment="test-env",
            version="v1.2.0"
        )
        mock_rollback_system.active_deployments["test-env"] = active_deployment
        
        # Mock orchestrator rollback
        with patch.object(mock_rollback_system.orchestrator, 'rollback', new_callable=AsyncMock) as mock_rollback:
            mock_rollback.return_value = Mock(
                deployment_id="rollback-456",
                status=DeploymentStatus.SUCCESS,
                environment="test-env",
                version="v1.1.0"
            )
            
            # Mock finding rollback target
            with patch.object(mock_rollback_system, '_find_rollback_target', new_callable=AsyncMock) as mock_find:
                mock_find.return_value = "v1.1.0"
                
                rollback_event = await mock_rollback_system.execute_rollback(
                    "test-env",
                    RollbackTrigger.ERROR_RATE_THRESHOLD,
                    {'error_rate': 0.15}
                )
                
                assert rollback_event.trigger == RollbackTrigger.ERROR_RATE_THRESHOLD
                assert rollback_event.environment == "test-env"
                assert rollback_event.target_version == "v1.1.0"
                assert rollback_event.status == "completed"
    
    @pytest.mark.asyncio
    async def test_deployment_monitoring(self, mock_rollback_system):
        """Test deployment monitoring for rollback conditions"""
        deployment_result = Mock(
            deployment_id="monitor-test",
            status=DeploymentStatus.SUCCESS,
            environment="test-env",
            version="v1.0.0"
        )
        
        # Mock monitoring task
        with patch.object(mock_rollback_system, '_monitor_environment', new_callable=AsyncMock) as mock_monitor:
            await mock_rollback_system.monitor_deployment(
                deployment_result, 
                "http://test.example.com/health"
            )
            
            # Verify monitoring was started
            assert "test-env" in mock_rollback_system.active_deployments
            assert mock_rollback_system.active_deployments["test-env"] == deployment_result

class TestEnvironmentSync:
    """Test environment synchronization system"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Create environment directories
            env_dir = config_dir / "environments"
            env_dir.mkdir(parents=True)
            
            # Create source environment
            source_env_dir = env_dir / "source"
            source_env_dir.mkdir()
            
            source_config = {
                'environment': 'source',
                'version': '1.0.0',
                'database_url': 'postgres://source-db:5432/app',
                'api_key': 'source-api-key'
            }
            with open(source_env_dir / "config.yaml", 'w') as f:
                yaml.dump(source_config, f)
            
            # Create target environment
            target_env_dir = env_dir / "target"
            target_env_dir.mkdir()
            
            target_config = {
                'environment': 'target',
                'version': '0.9.0',
                'database_url': 'postgres://target-db:5432/app'
            }
            with open(target_env_dir / "config.yaml", 'w') as f:
                yaml.dump(target_config, f)
            
            yield str(config_dir)
    
    @pytest.fixture
    def mock_synchronizer(self, temp_config_dir):
        """Mock environment synchronizer"""
        return EnvironmentSynchronizer(temp_config_dir)
    
    @pytest.mark.asyncio
    async def test_environment_state_collection(self, mock_synchronizer):
        """Test environment state collection"""
        # Mock configuration loading
        with patch.object(mock_synchronizer.config_manager, 'load_environment_config', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = {
                'environment': 'test',
                'version': '1.0.0',
                'config_data': 'test_data'
            }
            
            state = await mock_synchronizer.get_environment_state("test")
            
            assert state.name == "test"
            assert state.version == "1.0.0"
            assert state.status == SyncStatus.IN_SYNC
            assert len(state.config_hash) > 0
    
    @pytest.mark.asyncio
    async def test_environment_comparison(self, mock_synchronizer):
        """Test environment comparison"""
        # Mock environment states
        with patch.object(mock_synchronizer, 'get_environment_state', new_callable=AsyncMock) as mock_get_state:
            mock_get_state.side_effect = [
                Mock(
                    name="env1",
                    config_hash="hash1",
                    secrets_hash="secret_hash1",
                    files_hash="files_hash1",
                    dependencies_hash="deps_hash1",
                    version="1.0.0"
                ),
                Mock(
                    name="env2",
                    config_hash="hash2",  # Different
                    secrets_hash="secret_hash1",  # Same
                    files_hash="files_hash1",  # Same
                    dependencies_hash="deps_hash2",  # Different
                    version="1.1.0"  # Different
                )
            ]
            
            differences = await mock_synchronizer.compare_environments("env1", "env2")
            
            assert differences['config_match'] == False
            assert differences['secrets_match'] == True
            assert differences['files_match'] == True
            assert differences['dependencies_match'] == False
            assert differences['version_match'] == False
    
    @pytest.mark.asyncio
    async def test_environment_synchronization(self, mock_synchronizer):
        """Test environment synchronization"""
        # Mock configuration and secrets managers
        with patch.object(mock_synchronizer.config_manager, 'load_environment_config', new_callable=AsyncMock) as mock_load_config:
            with patch.object(mock_synchronizer.config_manager, 'save_environment_config', new_callable=AsyncMock) as mock_save_config:
                with patch.object(mock_synchronizer.secrets_manager, 'sync_secrets', new_callable=AsyncMock) as mock_sync_secrets:
                    
                    mock_load_config.return_value = {'config': 'source_config'}
                    mock_sync_secrets.return_value = ['secret1', 'secret2']
                    
                    sync_operation = await mock_synchronizer.sync_environments(
                        "source_env",
                        "target_env",
                        [ConfigType.ENVIRONMENT_VARIABLES, ConfigType.SECRETS]
                    )
                    
                    assert sync_operation.source_environment == "source_env"
                    assert sync_operation.target_environment == "target_env"
                    assert sync_operation.status == SyncStatus.IN_SYNC
                    assert len(sync_operation.changes) > 0
                    
                    # Verify methods were called
                    mock_load_config.assert_called_with("source_env")
                    mock_save_config.assert_called_once()
                    mock_sync_secrets.assert_called_with("source_env", "target_env")
    
    @pytest.mark.asyncio
    async def test_environment_validation(self, mock_synchronizer):
        """Test environment configuration validation"""
        # Mock valid configuration
        with patch.object(mock_synchronizer.config_manager, 'load_environment_config', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = {
                'environment': 'test_env',
                'version': '1.0.0',
                'database_url': 'postgres://localhost:5432/test'
            }
            
            with patch.object(mock_synchronizer.secrets_manager, 'list_secrets', new_callable=AsyncMock) as mock_list_secrets:
                mock_list_secrets.return_value = ['api_key', 'db_password']
                
                validation_result = await mock_synchronizer.validate_environment("test_env")
                
                assert validation_result['valid'] == True
                assert validation_result['environment'] == "test_env"
                assert len(validation_result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_environment_snapshot_creation(self, mock_synchronizer):
        """Test environment snapshot creation"""
        # Mock environment state
        with patch.object(mock_synchronizer, 'get_environment_state', new_callable=AsyncMock) as mock_get_state:
            mock_get_state.return_value = Mock(
                name="snapshot_test",
                version="1.0.0",
                config_hash="test_hash",
                last_sync=datetime.now()
            )
            
            # Mock file operations
            with patch('shutil.copytree') as mock_copytree:
                snapshot_path = await mock_synchronizer.create_environment_snapshot("snapshot_test")
                
                assert "snapshot_test" in snapshot_path
                assert Path(snapshot_path).exists()

class TestPipelineLayerIntegration:
    """Test integration between pipeline layer components"""
    
    @pytest.mark.asyncio
    async def test_full_deployment_pipeline(self):
        """Test complete deployment pipeline integration"""
        # Mock all pipeline components
        orchestrator = Mock()
        deployer = Mock()
        rollback_system = Mock()
        env_sync = Mock()
        
        # Configure mock behaviors
        orchestrator.deploy = AsyncMock(return_value=Mock(
            deployment_id="integration-test",
            status=DeploymentStatus.SUCCESS,
            environment="staging",
            version="v1.0.0"
        ))
        
        deployer.deploy_to_environment = AsyncMock(return_value=Mock(
            deployment_id="env-deploy",
            status=DeploymentStatus.SUCCESS
        ))
        
        rollback_system.monitor_deployment = AsyncMock()
        env_sync.sync_environments = AsyncMock(return_value=Mock(
            status=SyncStatus.IN_SYNC,
            changes=['config_updated']
        ))
        
        # Simulate full pipeline
        # 1. Environment sync
        sync_result = await env_sync.sync_environments("source", "target")
        
        # 2. Deployment
        deployment_result = await deployer.deploy_to_environment("staging", "v1.0.0")
        
        # 3. Rollback monitoring
        await rollback_system.monitor_deployment(deployment_result, "http://staging/health")
        
        # Verify all components were called
        env_sync.sync_environments.assert_called_once_with("source", "target")
        deployer.deploy_to_environment.assert_called_once_with("staging", "v1.0.0")
        rollback_system.monitor_deployment.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pipeline_failure_handling(self):
        """Test pipeline failure handling and recovery"""
        orchestrator = Mock()
        rollback_system = Mock()
        
        # Simulate deployment failure
        orchestrator.deploy = AsyncMock(return_value=Mock(
            deployment_id="failed-deploy",
            status=DeploymentStatus.FAILED,
            error_message="Health check failed"
        ))
        
        # Simulate rollback execution
        rollback_system.execute_rollback = AsyncMock(return_value=Mock(
            event_id="rollback-event",
            status="completed",
            target_version="v0.9.0"
        ))
        
        # Execute failure scenario
        deployment_result = await orchestrator.deploy(Mock())
        
        if deployment_result.status == DeploymentStatus.FAILED:
            rollback_result = await rollback_system.execute_rollback(
                "staging",
                RollbackTrigger.MANUAL_TRIGGER,
                {}
            )
            
            assert rollback_result.status == "completed"
            rollback_system.execute_rollback.assert_called_once()

# Performance Tests for Pipeline Layer
class TestPipelineLayerPerformance:
    """Performance tests for pipeline layer"""
    
    @pytest.mark.asyncio
    async def test_concurrent_deployments(self):
        """Test handling of concurrent deployments"""
        orchestrator = Mock()
        orchestrator.deploy = AsyncMock(return_value=Mock(
            status=DeploymentStatus.SUCCESS,
            deployment_id="concurrent-test"
        ))
        
        # Simulate concurrent deployments
        tasks = []
        for i in range(10):
            config = Mock(
                strategy=DeploymentStrategy.ROLLING,
                environment=f"env-{i}",
                version="v1.0.0"
            )
            task = orchestrator.deploy(config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All deployments should succeed
        assert len(results) == 10
        assert all(r.status == DeploymentStatus.SUCCESS for r in results)
        assert orchestrator.deploy.call_count == 10
    
    @pytest.mark.asyncio
    async def test_rollback_system_performance(self):
        """Test rollback system performance under load"""
        rollback_system = Mock()
        rollback_system.execute_rollback = AsyncMock(return_value=Mock(
            status="completed",
            execution_time=0.5
        ))
        
        # Simulate multiple rollback scenarios
        start_time = asyncio.get_event_loop().time()
        
        tasks = []
        for i in range(50):
            task = rollback_system.execute_rollback(
                f"env-{i}",
                RollbackTrigger.ERROR_RATE_THRESHOLD,
                {'error_rate': 0.1}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert total_time < 10.0  # Should complete within 10 seconds
        assert len(results) == 50
        assert rollback_system.execute_rollback.call_count == 50


@pytest.mark.asyncio
async def test_deployment_validator_handles_missing_aiohttp(monkeypatch):
    monkeypatch.setattr('pipeline.deployment_automation.aiohttp', None, raising=False)

    config = EnvironmentConfig(
        name="dev",
        type=Environment.DEVELOPMENT,
        base_url="http://localhost",
        health_check_endpoint="/health",
        deployment_strategy=DeploymentStrategy.BLUE_GREEN
    )

    issues = await DeploymentValidator.validate_pre_deployment(config, "1.0.0")
    assert any("aiohttp" in issue for issue in issues)


@pytest.mark.asyncio
async def test_post_deployment_validation_reports_missing_aiohttp(monkeypatch):
    monkeypatch.setattr('pipeline.deployment_automation.aiohttp', None, raising=False)

    config = EnvironmentConfig(
        name="dev",
        type=Environment.DEVELOPMENT,
        base_url="http://localhost",
        health_check_endpoint="/health",
        deployment_strategy=DeploymentStrategy.BLUE_GREEN
    )

    deployment_result = DeploymentResult(
        deployment_id="deploy-1",
        status=DeploymentStatus.SUCCESS,
        strategy=DeploymentStrategy.BLUE_GREEN,
        environment="dev",
        version="1.0.0",
        start_time=datetime.now()
    )

    issues = await DeploymentValidator.validate_post_deployment(config, deployment_result)
    assert any("aiohttp" in issue for issue in issues)


@pytest.mark.asyncio
async def test_health_checker_warns_when_aiohttp_missing(monkeypatch, caplog):
    monkeypatch.setattr('pipeline.orchestration_engine.aiohttp', None, raising=False)

    with caplog.at_level(logging.WARNING):
        result = await HealthChecker.check_endpoint("http://example.com/status")

    assert result is False
    assert any("aiohttp is not installed" in record.getMessage() for record in caplog.records)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
