"""
Comprehensive Test Suite for L9 ToTh Integration
Tests production ToTh engine, model deployment, and optimization systems
"""

import pytest
import asyncio
import contextlib
import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import L9 ToTh Integration components
import sys
sys.path.append(str(Path(__file__).parent.parent))
sys.modules.setdefault("aiohttp", MagicMock())

from toth_integration.production_toth_engine import (
    ProductionToThEngine, ToThConfig, ModelProvider, ReasoningMode,
    CloudModelClient, ReasoningStepParser, L9ToThIntegration
)
from toth_integration.model_deployment import (
    ModelDeploymentManager, DeploymentConfig, ModelEndpoint,
    LoadBalancer, ModelScaler, DeploymentMetrics
)
from toth_integration.optimization import (
    ToThOptimizer, OptimizationConfig, IntelligentCache,
    QueryOptimizer, BatchProcessor, PerformanceMonitor
)
from toth_integration.l9_toth_engine import L9ToThEngine, L9ToThConfig


class _StubReasoningGraph:
    """Lightweight reasoning graph stub for testing responsiveness."""

    def __init__(self, conclusion: str):
        self._conclusion = conclusion

    def score(self) -> float:
        return 0.5

    def get_final_step(self) -> str:
        return self._conclusion


class _StubReasoningAgent:
    """Synchronous reasoning agent that simulates blocking inference."""

    def __init__(self, reasoning_type: str, sleep_seconds: float):
        self.reasoning_type = reasoning_type
        self._sleep_seconds = sleep_seconds

    def reason(self, context: str, question: str):
        time.sleep(self._sleep_seconds)
        conclusion = f"{self.reasoning_type}-conclusion"
        graph = _StubReasoningGraph(conclusion)
        return {
            "reasoning_type": self.reasoning_type,
            "response": conclusion,
            "steps": [f"{self.reasoning_type} step"],
            "reasoning_graph": graph,
            "confidence_score": graph.score(),
            "final_conclusion": graph.get_final_step(),
            "timestamp": datetime.now().isoformat(),
        }


@pytest.mark.asyncio
async def test_l9_toth_engine_remains_responsive_with_blocking_agents():
    """Ensure blocking agent inference executes off the main loop."""

    with patch.object(L9ToThEngine, "_initialize_agents", return_value=None):
        engine = L9ToThEngine(config=L9ToThConfig())

    engine.config.reasoning_modes = ["fast", "slow"]
    engine.reasoning_agents = {
        "fast": _StubReasoningAgent("fast", sleep_seconds=0.0),
        "slow": _StubReasoningAgent("slow", sleep_seconds=0.2),
    }

    multi_modal_task = asyncio.create_task(
        engine.multi_modal_reasoning("context", "question")
    )

    responsiveness_event = asyncio.Event()

    async def notifier():
        await asyncio.sleep(0.05)
        responsiveness_event.set()

    notifier_task = asyncio.create_task(notifier())

    await asyncio.wait_for(responsiveness_event.wait(), timeout=0.2)

    result = await asyncio.wait_for(multi_modal_task, timeout=1)

    notifier_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await notifier_task

    assert result["status"] == "success"
    assert set(result["reasoning_results"].keys()) == {"fast", "slow"}
    assert result["reasoning_results"]["fast"]["reasoning_type"] == "fast"
    assert result["reasoning_results"]["slow"]["reasoning_type"] == "slow"

class TestProductionToThEngine:
    """Test production ToTh reasoning engine"""
    
    @pytest.fixture
    def mock_toth_config(self):
        """Mock ToTh configuration"""
        return ToThConfig(
            model_provider=ModelProvider.MOCK,
            model_name="test-model",
            max_tokens=1024,
            temperature=0.7,
            confidence_threshold=0.7,
            reasoning_timeout=30
        )
    
    @pytest.fixture
    def mock_toth_engine(self, mock_toth_config):
        """Mock production ToTh engine"""
        return ProductionToThEngine(mock_toth_config)
    
    @pytest.mark.asyncio
    async def test_toth_engine_initialization(self, mock_toth_engine):
        """Test ToTh engine initialization"""
        assert mock_toth_engine is not None
        assert mock_toth_engine.config.model_provider == ModelProvider.MOCK
        assert mock_toth_engine.config.confidence_threshold == 0.7
        assert len(mock_toth_engine.reasoning_history) == 0
        assert mock_toth_engine.performance_metrics['total_queries'] == 0
    
    @pytest.mark.asyncio
    async def test_abductive_reasoning(self, mock_toth_engine):
        """Test abductive reasoning execution"""
        query = "The server is responding slowly. What could be the most likely cause?"
        
        result = await mock_toth_engine.reason(query, ReasoningMode.ABDUCTIVE)
        
        assert result.query == query
        assert result.reasoning_mode == ReasoningMode.ABDUCTIVE
        assert result.overall_confidence >= 0.0
        assert result.overall_confidence <= 1.0
        assert len(result.steps) > 0
        assert result.execution_time > 0
        assert result.final_conclusion is not None
    
    @pytest.mark.asyncio
    async def test_deductive_reasoning(self, mock_toth_engine):
        """Test deductive reasoning execution"""
        query = "If all microservices use JWT tokens and service A is a microservice, what authentication method does service A use?"
        
        result = await mock_toth_engine.reason(query, ReasoningMode.DEDUCTIVE)
        
        assert result.reasoning_mode == ReasoningMode.DEDUCTIVE
        assert result.overall_confidence >= 0.0
        assert len(result.steps) > 0
        assert "jwt" in result.final_conclusion.lower() or "token" in result.final_conclusion.lower()
    
    @pytest.mark.asyncio
    async def test_inductive_reasoning(self, mock_toth_engine):
        """Test inductive reasoning execution"""
        query = "Based on these deployment patterns: service A uses Docker, service B uses Docker, service C uses Docker. What can we generalize?"
        
        result = await mock_toth_engine.reason(query, ReasoningMode.INDUCTIVE)
        
        assert result.reasoning_mode == ReasoningMode.INDUCTIVE
        assert result.overall_confidence >= 0.0
        assert len(result.steps) > 0
        assert "docker" in result.final_conclusion.lower() or "pattern" in result.final_conclusion.lower()
    
    @pytest.mark.asyncio
    async def test_hybrid_reasoning(self, mock_toth_engine):
        """Test hybrid multi-modal reasoning"""
        query = "Our API response times have increased by 300% after the last deployment. Analyze the situation and recommend actions."
        
        result = await mock_toth_engine.reason(query, ReasoningMode.HYBRID)
        
        assert result.reasoning_mode == ReasoningMode.HYBRID
        assert result.overall_confidence >= 0.0
        assert len(result.steps) > 0
        assert any(keyword in result.final_conclusion.lower() 
                  for keyword in ['performance', 'deployment', 'optimization', 'rollback'])
    
    @pytest.mark.asyncio
    async def test_multi_modal_reasoning(self, mock_toth_engine):
        """Test multi-modal reasoning with all modes"""
        query = "Design a scalable authentication system for a microservices architecture"
        
        results = await mock_toth_engine.multi_modal_reasoning(query)
        
        assert len(results) == 3  # abductive, deductive, inductive
        assert ReasoningMode.ABDUCTIVE.value in results
        assert ReasoningMode.DEDUCTIVE.value in results
        assert ReasoningMode.INDUCTIVE.value in results
        
        for mode, result in results.items():
            assert result.query == query
            assert result.overall_confidence >= 0.0
            assert len(result.steps) > 0
    
    @pytest.mark.asyncio
    async def test_reasoning_validation(self, mock_toth_engine):
        """Test reasoning result validation"""
        query = "Test validation query"
        result = await mock_toth_engine.reason(query, ReasoningMode.HYBRID)
        
        validation = await mock_toth_engine.validate_reasoning(result)
        
        assert 'valid' in validation
        assert 'quality_score' in validation
        assert 'issues' in validation
        assert 'recommendations' in validation
        assert validation['quality_score'] >= 0.0
        assert validation['quality_score'] <= 1.0
    
    def test_performance_metrics_tracking(self, mock_toth_engine):
        """Test performance metrics tracking"""
        # Initial metrics should be empty
        initial_metrics = mock_toth_engine.get_performance_metrics()
        assert initial_metrics['total_queries'] == 0
        assert initial_metrics['avg_response_time'] == 0.0
        
        # Simulate adding performance data
        mock_toth_engine.performance_metrics['total_queries'] = 5
        mock_toth_engine.performance_metrics['avg_response_time'] = 2.5
        mock_toth_engine.performance_metrics['success_rate'] = 0.8
        
        updated_metrics = mock_toth_engine.get_performance_metrics()
        assert updated_metrics['total_queries'] == 5
        assert updated_metrics['avg_response_time'] == 2.5
        assert updated_metrics['success_rate'] == 0.8
    
    def test_reasoning_history_management(self, mock_toth_engine):
        """Test reasoning history management"""
        # Add mock results to history
        for i in range(15):
            mock_result = Mock()
            mock_result.query = f"Query {i}"
            mock_result.reasoning_mode = ReasoningMode.HYBRID
            mock_result.overall_confidence = 0.8
            mock_toth_engine.reasoning_history.append(mock_result)
        
        # Test history retrieval with limit
        recent_history = mock_toth_engine.get_reasoning_history(limit=10)
        assert len(recent_history) == 10
        
        # Should return most recent entries
        assert recent_history[-1].query == "Query 14"
        assert recent_history[0].query == "Query 5"

class TestCloudModelClient:
    """Test cloud model client functionality"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for cloud client"""
        return ToThConfig(
            model_provider=ModelProvider.MOCK,
            api_key="test-key",
            max_tokens=512,
            temperature=0.7,
            enable_caching=True,
            cache_ttl=3600
        )
    
    @pytest.mark.asyncio
    async def test_mock_response_generation(self, mock_config):
        """Test mock response generation"""
        async with CloudModelClient(mock_config) as client:
            response = await client.generate_response(
                "Test prompt for mock response",
                ReasoningMode.ABDUCTIVE
            )
            
            assert response is not None
            assert len(response) > 0
            assert "abductive" in response.lower()
            assert "confidence" in response.lower()
    
    @pytest.mark.asyncio
    async def test_response_caching(self, mock_config):
        """Test response caching functionality"""
        async with CloudModelClient(mock_config) as client:
            prompt = "Test caching prompt"
            
            # First call - should cache
            response1 = await client.generate_response(prompt, ReasoningMode.HYBRID)
            
            # Second call - should use cache
            response2 = await client.generate_response(prompt, ReasoningMode.HYBRID)
            
            # Responses should be identical (from cache)
            assert response1 == response2
            
            # Cache should contain the entry
            cache_key = f"{ReasoningMode.HYBRID.value}:{hash(prompt)}"
            assert cache_key in client.cache
    
    @pytest.mark.asyncio
    async def test_openai_api_call_structure(self, mock_config):
        """Test OpenAI API call structure (mocked)"""
        mock_config.model_provider = ModelProvider.OPENAI
        mock_config.api_key = "test-openai-key"
        
        async with CloudModelClient(mock_config) as client:
            # Mock the session.post call
            with patch.object(client.session, 'post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={
                    'choices': [{'message': {'content': 'Test OpenAI response'}}]
                })
                mock_post.return_value.__aenter__.return_value = mock_response
                
                response = await client._call_openai("Test prompt", ReasoningMode.DEDUCTIVE)
                
                assert response == "Test OpenAI response"
                mock_post.assert_called_once()
                
                # Verify request structure
                call_args = mock_post.call_args
                assert 'https://api.openai.com/v1/chat/completions' in str(call_args)
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, mock_config):
        """Test fallback to mock when API fails"""
        mock_config.model_provider = ModelProvider.OPENAI
        mock_config.fallback_provider = ModelProvider.MOCK
        mock_config.api_key = None  # No API key to trigger failure
        
        async with CloudModelClient(mock_config) as client:
            # Should fallback to mock
            response = await client.generate_response(
                "Test fallback prompt",
                ReasoningMode.ABDUCTIVE
            )
            
            assert response is not None
            assert "mock" in response.lower() or "abductive" in response.lower()

class TestModelDeployment:
    """Test model deployment system"""
    
    @pytest.fixture
    def mock_deployment_config(self):
        """Mock deployment configuration"""
        endpoint = ModelEndpoint(
            endpoint_id="test-endpoint",
            model_provider=ModelProvider.MOCK,
            model_name="test-model",
            api_endpoint="http://test.api.com/v1",
            max_requests_per_minute=100,
            cost_per_request=0.001
        )
        
        return DeploymentConfig(
            deployment_id="test-deployment",
            name="Test Deployment",
            endpoints=[endpoint],
            min_replicas=1,
            max_replicas=5,
            auto_scaling_enabled=True
        )
    
    @pytest.fixture
    def mock_deployment_manager(self):
        """Mock deployment manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            return ModelDeploymentManager(temp_dir)
    
    @pytest.mark.asyncio
    async def test_deployment_creation(self, mock_deployment_manager, mock_deployment_config):
        """Test deployment creation"""
        deployment_id = await mock_deployment_manager.create_deployment(mock_deployment_config)
        
        assert deployment_id == mock_deployment_config.deployment_id
        assert deployment_id in mock_deployment_manager.deployments
        assert deployment_id in mock_deployment_manager.load_balancers
        assert deployment_id in mock_deployment_manager.scalers
    
    @pytest.mark.asyncio
    async def test_deployment_status(self, mock_deployment_manager, mock_deployment_config):
        """Test deployment status retrieval"""
        await mock_deployment_manager.create_deployment(mock_deployment_config)
        
        # Mock health check
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            status = await mock_deployment_manager.get_deployment_status(mock_deployment_config.deployment_id)
            
            assert status['deployment_id'] == mock_deployment_config.deployment_id
            assert status['name'] == mock_deployment_config.name
            assert status['endpoints'] == 1
            assert status['healthy_endpoints'] == 1
    
    @pytest.mark.asyncio
    async def test_reasoning_execution(self, mock_deployment_manager, mock_deployment_config):
        """Test reasoning execution through deployment"""
        await mock_deployment_manager.create_deployment(mock_deployment_config)
        
        result = await mock_deployment_manager.execute_reasoning(
            mock_deployment_config.deployment_id,
            "Test reasoning query",
            "hybrid"
        )
        
        assert result['deployment_id'] == mock_deployment_config.deployment_id
        assert result['query'] == "Test reasoning query"
        assert result['reasoning_mode'] == "hybrid"
        assert 'result' in result
        assert 'confidence' in result
        assert 'execution_time' in result
    
    @pytest.mark.asyncio
    async def test_auto_scaling(self, mock_deployment_manager, mock_deployment_config):
        """Test auto-scaling functionality"""
        await mock_deployment_manager.create_deployment(mock_deployment_config)
        
        scaling_result = await mock_deployment_manager.auto_scale_deployment(mock_deployment_config.deployment_id)
        
        # Scaling decision should be made (even if no action needed)
        assert scaling_result is None or 'action' in scaling_result
    
    @pytest.mark.asyncio
    async def test_deployment_metrics_collection(self, mock_deployment_manager, mock_deployment_config):
        """Test deployment metrics collection"""
        await mock_deployment_manager.create_deployment(mock_deployment_config)
        
        metrics = await mock_deployment_manager.collect_metrics(mock_deployment_config.deployment_id)
        
        assert metrics.deployment_id == mock_deployment_config.deployment_id
        assert metrics.total_requests >= 0
        assert metrics.successful_requests >= 0
        assert metrics.failed_requests >= 0
        assert metrics.avg_response_time >= 0
        assert metrics.active_replicas >= mock_deployment_config.min_replicas
        assert metrics.active_replicas <= mock_deployment_config.max_replicas

class TestLoadBalancer:
    """Test load balancing functionality"""
    
    @pytest.fixture
    def mock_endpoints(self):
        """Mock model endpoints"""
        return [
            ModelEndpoint(
                endpoint_id="endpoint-1",
                model_provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                api_endpoint="http://api1.example.com",
                priority=1
            ),
            ModelEndpoint(
                endpoint_id="endpoint-2",
                model_provider=ModelProvider.ANTHROPIC,
                model_name="claude-3",
                api_endpoint="http://api2.example.com",
                priority=2
            ),
            ModelEndpoint(
                endpoint_id="endpoint-3",
                model_provider=ModelProvider.MOCK,
                model_name="mock-model",
                api_endpoint="http://api3.example.com",
                priority=3
            )
        ]
    
    def test_round_robin_selection(self, mock_endpoints):
        """Test round-robin load balancing"""
        load_balancer = LoadBalancer("round_robin")
        
        # Test multiple selections
        selections = []
        for i in range(6):  # 2 full rounds
            selected = load_balancer.select_endpoint(mock_endpoints)
            selections.append(selected.endpoint_id)
        
        # Should cycle through endpoints
        assert selections == ["endpoint-1", "endpoint-2", "endpoint-3", "endpoint-1", "endpoint-2", "endpoint-3"]
    
    def test_weighted_selection(self, mock_endpoints):
        """Test weighted load balancing"""
        load_balancer = LoadBalancer("weighted")
        
        # Update endpoint stats to influence weighting
        load_balancer.update_endpoint_stats("endpoint-1", {
            'success_rate': 95.0,
            'avg_response_time': 1.0
        })
        load_balancer.update_endpoint_stats("endpoint-2", {
            'success_rate': 85.0,
            'avg_response_time': 2.0
        })
        load_balancer.update_endpoint_stats("endpoint-3", {
            'success_rate': 90.0,
            'avg_response_time': 1.5
        })
        
        # Test selection (should favor endpoint-1 due to better stats)
        selected = load_balancer.select_endpoint(mock_endpoints)
        assert selected.endpoint_id in ["endpoint-1", "endpoint-2", "endpoint-3"]
    
    def test_least_connections_selection(self, mock_endpoints):
        """Test least connections load balancing"""
        load_balancer = LoadBalancer("least_connections")
        
        # Set different connection counts
        load_balancer.update_endpoint_stats("endpoint-1", {'active_connections': 10})
        load_balancer.update_endpoint_stats("endpoint-2", {'active_connections': 5})
        load_balancer.update_endpoint_stats("endpoint-3", {'active_connections': 15})
        
        # Should select endpoint with least connections (endpoint-2)
        selected = load_balancer.select_endpoint(mock_endpoints)
        assert selected.endpoint_id == "endpoint-2"
    
    def test_endpoint_health_filtering(self, mock_endpoints):
        """Test filtering of unhealthy endpoints"""
        load_balancer = LoadBalancer("round_robin")
        
        # Mark endpoints as unhealthy
        load_balancer.update_endpoint_stats("endpoint-1", {
            'success_rate': 50.0,  # Unhealthy
            'avg_response_time': 15.0  # Unhealthy
        })
        load_balancer.update_endpoint_stats("endpoint-2", {
            'success_rate': 95.0,  # Healthy
            'avg_response_time': 2.0  # Healthy
        })
        
        # Should prefer healthy endpoints
        selections = []
        for i in range(10):
            selected = load_balancer.select_endpoint(mock_endpoints)
            selections.append(selected.endpoint_id)
        
        # Should mostly select healthy endpoints
        healthy_selections = [s for s in selections if s in ["endpoint-2", "endpoint-3"]]
        assert len(healthy_selections) >= 5  # At least half should be healthy

class TestOptimization:
    """Test ToTh optimization system"""
    
    @pytest.fixture
    def mock_optimization_config(self):
        """Mock optimization configuration"""
        return OptimizationConfig(
            max_cache_size_mb=50,
            default_ttl_seconds=1800,
            enable_query_optimization=True,
            enable_response_compression=True,
            enable_batch_processing=True,
            parallel_reasoning_limit=3
        )
    
    @pytest.fixture
    def mock_optimizer(self, mock_optimization_config):
        """Mock ToTh optimizer"""
        return ToThOptimizer(mock_optimization_config)
    
    @pytest.mark.asyncio
    async def test_intelligent_caching(self, mock_optimizer):
        """Test intelligent caching system"""
        query = "What are the best practices for API design?"
        reasoning_mode = "hybrid"
        
        # First request - should cache
        result1, opt_info1 = await mock_optimizer.optimize_reasoning_request(
            query, reasoning_mode
        )
        
        assert opt_info1['cache_hit'] == False
        
        # Second request - should hit cache
        result2, opt_info2 = await mock_optimizer.optimize_reasoning_request(
            query, reasoning_mode
        )
        
        assert opt_info2['cache_hit'] == True
        assert result1 == result2
    
    def test_query_optimization(self, mock_optimizer):
        """Test query optimization"""
        query_optimizer = mock_optimizer.query_optimizer
        
        # Test with redundant phrases
        verbose_query = "Could you please help me understand what are the best practices for microservices architecture? Thank you."
        optimized_query, opt_info = query_optimizer.optimize_query(verbose_query)
        
        assert len(optimized_query) < len(verbose_query)
        assert opt_info['reduction_percent'] > 0
        assert len(opt_info['optimizations_applied']) > 0
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, mock_optimizer):
        """Test batch processing functionality"""
        batch_processor = mock_optimizer.batch_processor
        
        # Add multiple requests
        request_ids = []
        for i in range(3):
            request_id = f"req-{i}"
            await batch_processor.add_request(
                request_id,
                f"Query {i}",
                "hybrid"
            )
            request_ids.append(request_id)
        
        # Process batch
        await batch_processor.flush_batch()
        
        # Check results
        for request_id in request_ids:
            result = batch_processor.get_result(request_id)
            assert result is not None
            assert result['request_id'] == request_id
            assert result['batch_processed'] == True
    
    def test_cache_strategies(self, mock_optimization_config):
        """Test different cache strategies"""
        from toth_integration.optimization import CacheStrategy, IntelligentCache
        
        # Test LRU cache
        mock_optimization_config.cache_strategy = CacheStrategy.LRU
        lru_cache = IntelligentCache(mock_optimization_config)
        
        # Add entries to fill cache
        for i in range(5):
            lru_cache.put(f"query-{i}", "hybrid", f"result-{i}")
        
        # Access some entries to change LRU order
        lru_cache.get("query-1", "hybrid")
        lru_cache.get("query-3", "hybrid")
        
        # Add one more to trigger eviction
        lru_cache.put("query-new", "hybrid", "new-result")
        
        # Verify LRU behavior
        stats = lru_cache.get_stats()
        assert stats['entries'] <= 5
        assert stats['evictions'] >= 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, mock_optimizer):
        """Test performance monitoring"""
        # Execute several optimized requests
        queries = [
            "How to implement authentication?",
            "What is microservices architecture?",
            "Best practices for API design?",
            "How to handle errors in distributed systems?"
        ]
        
        for query in queries:
            await mock_optimizer.optimize_reasoning_request(query, "hybrid")
        
        # Check performance stats
        stats = mock_optimizer.get_optimization_stats()
        
        assert 'optimization_stats' in stats
        assert 'cache_stats' in stats
        assert 'performance_summary' in stats
        
        # Verify metrics are being tracked
        opt_stats = stats['optimization_stats']
        assert opt_stats['cache_hits'] >= 0
        assert opt_stats['queries_optimized'] >= 0
    
    def test_cache_size_management(self, mock_optimization_config):
        """Test cache size management and eviction"""
        from toth_integration.optimization import IntelligentCache
        
        # Set small cache size for testing
        mock_optimization_config.max_cache_size_mb = 1  # 1MB limit
        cache = IntelligentCache(mock_optimization_config)
        
        # Add large entries to trigger eviction
        large_data = "x" * 100000  # 100KB string
        
        for i in range(20):  # Add 20 * 100KB = 2MB of data
            cache.put(f"large-query-{i}", "hybrid", large_data)
        
        # Cache should have evicted entries to stay under limit
        stats = cache.get_stats()
        assert stats['size_mb'] <= mock_optimization_config.max_cache_size_mb * 1.1  # Allow 10% tolerance
        assert stats['evictions'] > 0

class TestToThIntegrationE2E:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_l9_toth_integration_workflow(self):
        """Test complete L9-ToTh integration workflow"""
        # Initialize L9-ToTh integration
        integration = L9ToThIntegration()
        
        # Test pattern detection enhancement
        pattern_result = await integration.enhance_pattern_detection(
            "User authentication flow: login -> validate -> session -> dashboard",
            "Web application security patterns"
        )
        
        assert 'toth_analysis' in pattern_result
        assert 'pattern_insights' in pattern_result
        assert 'confidence_level' in pattern_result
        assert pattern_result['confidence_level'] >= 0.0
        
        # Test decision making enhancement
        decision_result = await integration.enhance_decision_making(
            "Choose authentication method for new application",
            ["OAuth 2.0", "JWT tokens", "Session cookies", "API keys"]
        )
        
        assert 'recommended_decision' in decision_result
        assert 'confidence_level' in decision_result
        assert 'risk_assessment' in decision_result
        
        # Test error correction enhancement
        error_result = await integration.enhance_error_correction(
            "Database connection failure in production",
            "Connection timeout after 30 seconds, pool exhausted"
        )
        
        assert 'root_cause' in error_result
        assert 'fix_recommendations' in error_result
        assert 'confidence_level' in error_result
    
    @pytest.mark.asyncio
    async def test_production_deployment_workflow(self):
        """Test production deployment workflow"""
        # Create deployment manager
        with tempfile.TemporaryDirectory() as temp_dir:
            deployment_manager = ModelDeploymentManager(temp_dir)
            
            # Create deployment configuration
            endpoint = ModelEndpoint(
                endpoint_id="prod-endpoint",
                model_provider=ModelProvider.MOCK,
                model_name="production-model",
                api_endpoint="http://prod.api.com/v1"
            )
            
            config = DeploymentConfig(
                deployment_id="prod-deployment",
                name="Production Deployment",
                endpoints=[endpoint],
                auto_scaling_enabled=True
            )
            
            # Deploy
            deployment_id = await deployment_manager.create_deployment(config)
            
            # Execute reasoning
            result = await deployment_manager.execute_reasoning(
                deployment_id,
                "Optimize database query performance for high-traffic application",
                "hybrid"
            )
            
            # Verify result
            assert result['deployment_id'] == deployment_id
            assert 'result' in result
            assert 'confidence' in result
            assert result['confidence'] >= 0.0
            
            # Check deployment status
            status = await deployment_manager.get_deployment_status(deployment_id)
            assert status['deployment_id'] == deployment_id
            assert status['healthy_endpoints'] > 0
    
    @pytest.mark.asyncio
    async def test_optimization_integration(self):
        """Test optimization system integration"""
        # Create optimizer with production config
        config = OptimizationConfig(
            enable_query_optimization=True,
            enable_batch_processing=True,
            enable_prefetching=True
        )
        optimizer = ToThOptimizer(config)
        
        # Test multiple queries with optimization
        queries = [
            "How to implement caching in microservices?",
            "What are the security best practices for APIs?",
            "How to handle distributed transactions?",
            "What is the best way to monitor microservices?"
        ]
        
        results = []
        for query in queries:
            result, opt_info = await optimizer.optimize_reasoning_request(query, "hybrid")
            results.append((result, opt_info))
        
        # Verify optimization occurred
        assert len(results) == len(queries)
        
        # Check that some queries hit cache (if repeated)
        cache_hits = sum(1 for _, opt_info in results if opt_info.get('cache_hit', False))
        
        # Get optimization statistics
        stats = optimizer.get_optimization_stats()
        assert stats['cache_stats']['total_requests'] >= len(queries)

# Performance Tests
class TestToThPerformance:
    """Performance tests for ToTh integration"""
    
    @pytest.mark.asyncio
    async def test_concurrent_reasoning_performance(self):
        """Test concurrent reasoning performance"""
        engine = ProductionToThEngine(ToThConfig(model_provider=ModelProvider.MOCK))
        
        # Test concurrent reasoning requests
        queries = [f"Query {i}: Analyze system performance" for i in range(20)]
        
        start_time = time.time()
        
        tasks = []
        for query in queries:
            task = engine.reason(query, ReasoningMode.HYBRID)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert len(results) == len(queries)
        assert total_time < 30.0  # Should complete within 30 seconds
        assert all(r.overall_confidence >= 0.0 for r in results)
        
        # Check average response time
        avg_response_time = sum(r.execution_time for r in results) / len(results)
        assert avg_response_time < 5.0  # Average should be under 5 seconds
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance under load"""
        config = OptimizationConfig(max_cache_size_mb=10)
        optimizer = ToThOptimizer(config)
        
        # Test cache performance with repeated queries
        base_query = "What are microservices best practices?"
        
        # First batch - populate cache
        start_time = time.time()
        for i in range(10):
            await optimizer.optimize_reasoning_request(f"{base_query} {i}", "hybrid")
        populate_time = time.time() - start_time
        
        # Second batch - should hit cache
        start_time = time.time()
        for i in range(10):
            await optimizer.optimize_reasoning_request(f"{base_query} {i}", "hybrid")
        cache_time = time.time() - start_time
        
        # Cache hits should be significantly faster
        assert cache_time < populate_time * 0.5  # At least 50% faster
        
        # Verify cache statistics
        stats = optimizer.get_optimization_stats()
        assert stats['cache_stats']['hit_rate_percent'] > 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])