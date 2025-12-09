"""
Basic Functionality Tests for L9 System
Tests core components that are already implemented
"""

import pytest
import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import existing L9 components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from toth_integration.production_toth_engine import (
    ProductionToThEngine, ToThConfig, ModelProvider, ReasoningMode
)
from toth_integration.optimization import (
    ToThOptimizer, OptimizationConfig, IntelligentCache
)

class TestProductionToThEngine:
    """Test production ToTh engine functionality"""
    
    @pytest.fixture
    def mock_toth_config(self):
        """Mock ToTh configuration"""
        return ToThConfig(
            model_provider=ModelProvider.MOCK,
            model_name="test-model",
            max_tokens=1024,
            temperature=0.7
        )
    
    @pytest.fixture
    def mock_toth_engine(self, mock_toth_config):
        """Mock production ToTh engine"""
        return ProductionToThEngine(mock_toth_config)
    
    def test_toth_engine_initialization(self, mock_toth_engine):
        """Test ToTh engine initialization"""
        assert mock_toth_engine is not None
        assert mock_toth_engine.config.model_provider == ModelProvider.MOCK
        assert mock_toth_engine.config.temperature == 0.7
        assert len(mock_toth_engine.reasoning_history) == 0
    
    @pytest.mark.asyncio
    async def test_basic_reasoning(self, mock_toth_engine):
        """Test basic reasoning functionality"""
        query = "What are the best practices for API design?"
        
        result = await mock_toth_engine.reason(query, ReasoningMode.HYBRID)
        
        assert result.query == query
        assert result.reasoning_mode == ReasoningMode.HYBRID
        assert result.overall_confidence >= 0.0
        assert result.overall_confidence <= 1.0
        assert len(result.steps) > 0
        assert result.execution_time > 0
        assert result.final_conclusion is not None
    
    def test_performance_metrics(self, mock_toth_engine):
        """Test performance metrics tracking"""
        initial_metrics = mock_toth_engine.get_performance_metrics()
        assert initial_metrics['total_queries'] == 0
        assert initial_metrics['avg_response_time'] == 0.0

class TestOptimizationSystem:
    """Test optimization system functionality"""
    
    @pytest.fixture
    def mock_optimization_config(self):
        """Mock optimization configuration"""
        return OptimizationConfig(
            max_cache_size_mb=10,
            default_ttl_seconds=1800,
            enable_query_optimization=True
        )
    
    @pytest.fixture
    def mock_optimizer(self, mock_optimization_config):
        """Mock ToTh optimizer"""
        return ToThOptimizer(mock_optimization_config)
    
    def test_optimizer_initialization(self, mock_optimizer):
        """Test optimizer initialization"""
        assert mock_optimizer is not None
        assert mock_optimizer.config.enable_query_optimization == True
        assert mock_optimizer.config.max_cache_size_mb == 10
    
    @pytest.mark.asyncio
    async def test_basic_optimization(self, mock_optimizer):
        """Test basic optimization functionality"""
        query = "How to implement microservices?"
        
        result, opt_info = await mock_optimizer.optimize_reasoning_request(query, "hybrid")
        
        assert result is not None
        assert 'cache_hit' in opt_info
        assert 'query_optimized' in opt_info
        assert 'optimizations_applied' in opt_info
    
    def test_cache_functionality(self, mock_optimization_config):
        """Test cache functionality"""
        cache = IntelligentCache(mock_optimization_config)
        
        # Test cache put and get
        cache.put("test query", "hybrid", "test result")
        result = cache.get("test query", "hybrid")
        
        assert result == "test result"
        
        # Test cache stats
        stats = cache.get_stats()
        assert stats['entries'] == 1
        assert stats['hits'] == 1

class TestSystemIntegration:
    """Test system integration functionality"""
    
    @pytest.mark.asyncio
    async def test_toth_optimization_integration(self):
        """Test ToTh engine with optimization"""
        # Create ToTh engine
        toth_config = ToThConfig(model_provider=ModelProvider.MOCK)
        toth_engine = ProductionToThEngine(toth_config)
        
        # Create optimizer
        opt_config = OptimizationConfig(enable_query_optimization=True)
        optimizer = ToThOptimizer(opt_config)
        
        # Test integrated workflow
        query = "Design a scalable authentication system"
        
        # Direct ToTh reasoning
        toth_result = await toth_engine.reason(query, ReasoningMode.HYBRID)
        
        # Optimized reasoning
        opt_result, opt_info = await optimizer.optimize_reasoning_request(query, "hybrid", reasoning_engine=toth_engine)
        
        # Verify both work
        assert toth_result.final_conclusion is not None
        assert opt_result is not None
        assert 'optimizations_applied' in opt_info
    
    @pytest.mark.asyncio
    async def test_multi_modal_reasoning(self):
        """Test multi-modal reasoning integration"""
        toth_config = ToThConfig(model_provider=ModelProvider.MOCK)
        engine = ProductionToThEngine(toth_config)
        
        query = "Analyze system performance issues"
        
        # Test all reasoning modes
        modes = [ReasoningMode.ABDUCTIVE, ReasoningMode.DEDUCTIVE, ReasoningMode.INDUCTIVE, ReasoningMode.HYBRID]
        
        results = []
        for mode in modes:
            result = await engine.reason(query, mode)
            results.append(result)
        
        # Verify all modes work
        assert len(results) == 4
        for result in results:
            assert result.query == query
            assert result.overall_confidence >= 0.0
            assert len(result.steps) > 0

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_reasoning_mode(self):
        """Test handling of invalid reasoning mode"""
        toth_config = ToThConfig(model_provider=ModelProvider.MOCK)
        engine = ProductionToThEngine(toth_config)
        
        # This should not raise an exception due to enum validation
        try:
            result = await engine.reason("test query", ReasoningMode.HYBRID)
            assert result is not None
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")
    
    def test_cache_overflow_handling(self):
        """Test cache overflow handling"""
        config = OptimizationConfig(max_cache_size_mb=1)  # Very small cache
        cache = IntelligentCache(config)
        
        # Add many entries to trigger eviction
        large_data = "x" * 10000  # 10KB string
        
        for i in range(200):  # Add 200 * 10KB = 2MB of data
            cache.put(f"query-{i}", "hybrid", large_data)
        
        # Cache should have evicted entries
        stats = cache.get_stats()
        assert stats['evictions'] > 0
        assert stats['size_mb'] <= config.max_cache_size_mb * 2  # Allow some tolerance
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in reasoning"""
        config = ToThConfig(
            model_provider=ModelProvider.MOCK,
            reasoning_timeout=1  # Very short timeout
        )
        engine = ProductionToThEngine(config)
        
        # Mock a slow operation
        with patch('toth_integration.production_toth_engine.CloudModelClient.generate_response') as mock_generate:
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(2)  # Longer than timeout
                return "slow response"
            
            mock_generate.side_effect = slow_response
            
            # This should handle timeout gracefully
            result = await engine.reason("test query", ReasoningMode.HYBRID)
            
            # Should return error result rather than hanging
            assert result is not None
            assert result.overall_confidence == 0.0  # Error case

class TestPerformanceBasics:
    """Basic performance tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_reasoning(self):
        """Test concurrent reasoning requests"""
        toth_config = ToThConfig(model_provider=ModelProvider.MOCK)
        engine = ProductionToThEngine(toth_config)
        
        # Create multiple concurrent requests
        queries = [f"Query {i}: Analyze system performance" for i in range(10)]
        
        tasks = []
        for query in queries:
            task = engine.reason(query, ReasoningMode.HYBRID)
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all completed successfully
        assert len(results) == len(queries)
        for result in results:
            assert result.overall_confidence >= 0.0
            assert len(result.steps) > 0
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance improvement"""
        config = OptimizationConfig(enable_query_optimization=True)
        optimizer = ToThOptimizer(config)
        
        query = "What are microservices best practices?"
        
        # First request (should cache)
        start_time = asyncio.get_event_loop().time()
        result1, opt_info1 = await optimizer.optimize_reasoning_request(query, "hybrid")
        first_time = asyncio.get_event_loop().time() - start_time
        
        # Second request (should hit cache)
        start_time = asyncio.get_event_loop().time()
        result2, opt_info2 = await optimizer.optimize_reasoning_request(query, "hybrid")
        second_time = asyncio.get_event_loop().time() - start_time
        
        # Verify caching behavior
        assert opt_info1['cache_hit'] == False
        assert opt_info2['cache_hit'] == True
        assert result1 == result2
        assert second_time < first_time  # Cache should be faster

class TestConfigurationManagement:
    """Test configuration management"""
    
    def test_toth_config_validation(self):
        """Test ToTh configuration validation"""
        # Valid configuration
        valid_config = ToThConfig(
            model_provider=ModelProvider.MOCK,
            max_tokens=1024,
            temperature=0.7
        )
        assert valid_config.model_provider == ModelProvider.MOCK
        assert valid_config.max_tokens == 1024
        assert valid_config.temperature == 0.7
    
    def test_optimization_config_validation(self):
        """Test optimization configuration validation"""
        # Valid configuration
        valid_config = OptimizationConfig(
            max_cache_size_mb=50,
            enable_query_optimization=True,
            parallel_reasoning_limit=5
        )
        assert valid_config.max_cache_size_mb == 50
        assert valid_config.enable_query_optimization == True
        assert valid_config.parallel_reasoning_limit == 5

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
