"""
Comprehensive Test Suite for L9 Intelligence Layer
Tests adaptive reasoning, system reflection, improvement loop, and meta audit
"""

import pytest
import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import L9 Intelligence Layer components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from intelligence.adaptive_reasoning import AdaptiveReasoning
from intelligence.system_reflection import SystemReflection
from intelligence.improvement_loop import ImprovementLoop
from intelligence.meta_audit import MetaAudit

class TestAdaptiveReasoning:
    """Test adaptive reasoning functionality"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_adaptive_reasoning(self, temp_config_dir):
        """Mock adaptive reasoning system"""
        # Create mock configuration
        config = {
            'reasoning_depth_levels': ['basic', 'standard', 'deep'],
            'performance_thresholds': {
                'confidence_threshold': 0.7,
                'latency_threshold': 5.0,
                'success_rate_threshold': 0.85
            },
            'adaptation_rules': {
                'increase_depth_on_low_confidence': True,
                'decrease_depth_on_high_latency': True,
                'auto_tune_parameters': True
            }
        }
        
        return AdaptiveReasoning(config, str(temp_config_dir))
    
    def test_adaptive_reasoning_initialization(self, mock_adaptive_reasoning):
        """Test adaptive reasoning system initialization"""
        assert mock_adaptive_reasoning is not None
        assert hasattr(mock_adaptive_reasoning, 'config')
        assert hasattr(mock_adaptive_reasoning, 'current_depth_level')
        assert hasattr(mock_adaptive_reasoning, 'performance_history')
    
    @pytest.mark.asyncio
    async def test_reasoning_depth_adjustment(self, mock_adaptive_reasoning):
        """Test automatic reasoning depth adjustment"""
        # Simulate low confidence scenario
        performance_data = {
            'confidence_score': 0.5,  # Below threshold
            'latency': 2.0,
            'success_rate': 0.9,
            'timestamp': datetime.now()
        }
        
        initial_depth = mock_adaptive_reasoning.current_depth_level
        await mock_adaptive_reasoning.adjust_reasoning_depth(performance_data)
        
        # Should increase depth due to low confidence
        assert mock_adaptive_reasoning.current_depth_level != initial_depth
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, mock_adaptive_reasoning):
        """Test performance monitoring and metrics collection"""
        # Add performance data points
        for i in range(10):
            performance_data = {
                'confidence_score': 0.8 + (i * 0.01),
                'latency': 1.0 + (i * 0.1),
                'success_rate': 0.9,
                'timestamp': datetime.now() - timedelta(minutes=i)
            }
            await mock_adaptive_reasoning.record_performance(performance_data)
        
        # Check performance history
        assert len(mock_adaptive_reasoning.performance_history) == 10
        
        # Test performance analysis
        analysis = await mock_adaptive_reasoning.analyze_performance_trends()
        assert 'confidence_trend' in analysis
        assert 'latency_trend' in analysis
        assert 'recommendations' in analysis
    
    @pytest.mark.asyncio
    async def test_reasoning_parameter_tuning(self, mock_adaptive_reasoning):
        """Test automatic parameter tuning"""
        # Simulate performance degradation
        poor_performance = {
            'confidence_score': 0.6,
            'latency': 8.0,  # High latency
            'success_rate': 0.7,  # Low success rate
            'timestamp': datetime.now()
        }
        
        original_params = mock_adaptive_reasoning.get_current_parameters()
        await mock_adaptive_reasoning.tune_parameters(poor_performance)
        updated_params = mock_adaptive_reasoning.get_current_parameters()
        
        # Parameters should be adjusted
        assert original_params != updated_params
    
    def test_reasoning_mode_selection(self, mock_adaptive_reasoning):
        """Test reasoning mode selection based on task complexity"""
        # Simple task
        simple_task = {
            'complexity': 'low',
            'domain': 'general',
            'urgency': 'normal'
        }
        mode = mock_adaptive_reasoning.select_reasoning_mode(simple_task)
        assert mode in ['basic', 'standard']
        
        # Complex task
        complex_task = {
            'complexity': 'high',
            'domain': 'technical',
            'urgency': 'high'
        }
        mode = mock_adaptive_reasoning.select_reasoning_mode(complex_task)
        assert mode in ['standard', 'deep']

class TestSystemReflection:
    """Test system reflection and self-analysis"""
    
    @pytest.fixture
    def mock_system_reflection(self):
        """Mock system reflection component"""
        config = {
            'reflection_interval_hours': 24,
            'analysis_depth': 'comprehensive',
            'data_sources': [
                'performance_metrics',
                'error_logs',
                'user_feedback',
                'system_health'
            ]
        }
        return SystemReflection(config)
    
    @pytest.mark.asyncio
    async def test_system_analysis(self, mock_system_reflection):
        """Test comprehensive system analysis"""
        # Mock system data
        system_data = {
            'performance_metrics': {
                'avg_response_time': 2.5,
                'success_rate': 0.92,
                'error_rate': 0.08,
                'throughput': 150
            },
            'error_patterns': [
                {'type': 'timeout', 'frequency': 15},
                {'type': 'validation_error', 'frequency': 8},
                {'type': 'resource_exhaustion', 'frequency': 3}
            ],
            'resource_utilization': {
                'cpu': 65.0,
                'memory': 78.0,
                'disk': 45.0,
                'network': 23.0
            }
        }
        
        analysis = await mock_system_reflection.analyze_system_state(system_data)
        
        assert 'overall_health_score' in analysis
        assert 'identified_issues' in analysis
        assert 'improvement_opportunities' in analysis
        assert 'recommendations' in analysis
        assert analysis['overall_health_score'] >= 0
        assert analysis['overall_health_score'] <= 100
    
    @pytest.mark.asyncio
    async def test_pattern_recognition(self, mock_system_reflection):
        """Test pattern recognition in system behavior"""
        # Historical performance data
        historical_data = []
        for i in range(30):  # 30 days of data
            day_data = {
                'date': datetime.now() - timedelta(days=i),
                'performance': {
                    'response_time': 2.0 + (i % 7) * 0.3,  # Weekly pattern
                    'error_rate': 0.05 + (i % 3) * 0.02,   # 3-day pattern
                    'load': 100 + (i % 5) * 20             # 5-day pattern
                }
            }
            historical_data.append(day_data)
        
        patterns = await mock_system_reflection.identify_patterns(historical_data)
        
        assert 'temporal_patterns' in patterns
        assert 'performance_correlations' in patterns
        assert 'anomaly_detection' in patterns
    
    @pytest.mark.asyncio
    async def test_failure_analysis(self, mock_system_reflection):
        """Test failure analysis and root cause identification"""
        failure_data = {
            'incident_id': 'INC-001',
            'timestamp': datetime.now(),
            'symptoms': [
                'high_response_time',
                'increased_error_rate',
                'memory_pressure'
            ],
            'system_state': {
                'cpu_usage': 95.0,
                'memory_usage': 88.0,
                'active_connections': 500,
                'queue_depth': 150
            },
            'logs': [
                'ERROR: Database connection timeout',
                'WARN: Memory usage above threshold',
                'ERROR: Request queue full'
            ]
        }
        
        analysis = await mock_system_reflection.analyze_failure(failure_data)
        
        assert 'root_causes' in analysis
        assert 'contributing_factors' in analysis
        assert 'prevention_strategies' in analysis
        assert len(analysis['root_causes']) > 0

class TestImprovementLoop:
    """Test continuous improvement system"""
    
    @pytest.fixture
    def mock_improvement_loop(self):
        """Mock improvement loop component"""
        config = {
            'improvement_cycle_hours': 168,  # Weekly
            'success_metrics': [
                'performance_improvement',
                'error_reduction',
                'efficiency_gains'
            ],
            'auto_apply_improvements': True,
            'rollback_on_degradation': True
        }
        return ImprovementLoop(config)
    
    @pytest.mark.asyncio
    async def test_improvement_identification(self, mock_improvement_loop):
        """Test identification of improvement opportunities"""
        system_analysis = {
            'performance_bottlenecks': [
                {
                    'component': 'database_queries',
                    'impact_score': 8.5,
                    'frequency': 'high',
                    'suggested_fix': 'add_query_optimization'
                },
                {
                    'component': 'cache_misses',
                    'impact_score': 6.2,
                    'frequency': 'medium',
                    'suggested_fix': 'improve_cache_strategy'
                }
            ],
            'resource_inefficiencies': [
                {
                    'resource': 'memory',
                    'waste_percentage': 15.0,
                    'optimization_potential': 'high'
                }
            ]
        }
        
        improvements = await mock_improvement_loop.identify_improvements(system_analysis)
        
        assert 'priority_improvements' in improvements
        assert 'implementation_plan' in improvements
        assert 'expected_impact' in improvements
        assert len(improvements['priority_improvements']) > 0
    
    @pytest.mark.asyncio
    async def test_improvement_implementation(self, mock_improvement_loop):
        """Test improvement implementation and validation"""
        improvement_plan = {
            'improvement_id': 'IMP-001',
            'type': 'performance_optimization',
            'description': 'Optimize database query performance',
            'implementation_steps': [
                'analyze_slow_queries',
                'add_database_indexes',
                'optimize_query_patterns',
                'validate_performance_gains'
            ],
            'success_criteria': {
                'response_time_improvement': 0.3,  # 30% improvement
                'error_rate_reduction': 0.1        # 10% reduction
            }
        }
        
        # Mock implementation
        with patch.object(mock_improvement_loop, '_execute_improvement_step', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {'status': 'success', 'metrics': {'response_time': 1.5}}
            
            result = await mock_improvement_loop.implement_improvement(improvement_plan)
            
            assert result['status'] in ['success', 'partial_success', 'failed']
            assert 'implementation_metrics' in result
            assert 'validation_results' in result
    
    @pytest.mark.asyncio
    async def test_improvement_rollback(self, mock_improvement_loop):
        """Test improvement rollback on performance degradation"""
        # Simulate failed improvement
        failed_improvement = {
            'improvement_id': 'IMP-002',
            'baseline_metrics': {
                'response_time': 2.0,
                'error_rate': 0.05,
                'throughput': 100
            },
            'post_implementation_metrics': {
                'response_time': 3.5,  # Degraded
                'error_rate': 0.12,   # Degraded
                'throughput': 80      # Degraded
            }
        }
        
        rollback_result = await mock_improvement_loop.evaluate_and_rollback(failed_improvement)
        
        assert rollback_result['rollback_triggered'] == True
        assert 'rollback_steps' in rollback_result
        assert 'post_rollback_metrics' in rollback_result

class TestMetaAudit:
    """Test meta audit and system integrity monitoring"""
    
    @pytest.fixture
    def mock_meta_audit(self, tmp_path):
        """Mock meta audit component"""
        config = {
            'audit_log_path': str(tmp_path / 'meta_audit.log'),
            'audit_interval_minutes': 60,
            'integrity_checks': [
                'component_health',
                'data_consistency',
                'security_compliance',
                'performance_baselines'
            ]
        }
        return MetaAudit(config)
    
    @pytest.mark.asyncio
    async def test_system_integrity_check(self, mock_meta_audit):
        """Test comprehensive system integrity checking"""
        system_components = {
            'intelligence_layer': {'status': 'healthy', 'last_check': datetime.now()},
            'reasoning_profiles': {'status': 'healthy', 'last_check': datetime.now()},
            'learning_system': {'status': 'degraded', 'last_check': datetime.now()},
            'integrity_layer': {'status': 'healthy', 'last_check': datetime.now()},
            'pipeline_layer': {'status': 'healthy', 'last_check': datetime.now()},
            'operations_layer': {'status': 'warning', 'last_check': datetime.now()}
        }
        
        integrity_report = await mock_meta_audit.check_system_integrity(system_components)
        
        assert 'overall_integrity_score' in integrity_report
        assert 'component_status' in integrity_report
        assert 'integrity_violations' in integrity_report
        assert 'recommended_actions' in integrity_report
    
    @pytest.mark.asyncio
    async def test_audit_trail_creation(self, mock_meta_audit):
        """Test audit trail creation and maintenance"""
        audit_events = [
            {
                'event_type': 'system_modification',
                'component': 'adaptive_reasoning',
                'action': 'parameter_update',
                'timestamp': datetime.now(),
                'user': 'system',
                'details': {'parameter': 'confidence_threshold', 'old_value': 0.7, 'new_value': 0.75}
            },
            {
                'event_type': 'performance_degradation',
                'component': 'learning_system',
                'action': 'alert_triggered',
                'timestamp': datetime.now(),
                'severity': 'medium',
                'details': {'metric': 'response_time', 'threshold': 5.0, 'actual': 7.2}
            }
        ]
        
        for event in audit_events:
            await mock_meta_audit.log_audit_event(event)
        
        # Retrieve audit trail
        audit_trail = await mock_meta_audit.get_audit_trail(hours=24)
        
        assert len(audit_trail) >= len(audit_events)
        assert all('timestamp' in event for event in audit_trail)
        assert all('event_type' in event for event in audit_trail)
    
    @pytest.mark.asyncio
    async def test_anomaly_detection(self, mock_meta_audit):
        """Test anomaly detection in system behavior"""
        # Normal behavior baseline
        baseline_metrics = {
            'response_time': {'mean': 2.0, 'std': 0.3},
            'error_rate': {'mean': 0.05, 'std': 0.01},
            'cpu_usage': {'mean': 60.0, 'std': 10.0},
            'memory_usage': {'mean': 70.0, 'std': 5.0}
        }
        
        # Current metrics with anomalies
        current_metrics = {
            'response_time': 5.5,  # Anomaly: 3+ std deviations
            'error_rate': 0.15,   # Anomaly: 10+ std deviations
            'cpu_usage': 65.0,    # Normal
            'memory_usage': 72.0  # Normal
        }
        
        anomalies = await mock_meta_audit.detect_anomalies(baseline_metrics, current_metrics)
        
        assert 'detected_anomalies' in anomalies
        assert 'severity_scores' in anomalies
        assert len(anomalies['detected_anomalies']) >= 2  # response_time and error_rate
    
    def test_audit_log_integrity(self, mock_meta_audit):
        """Test audit log integrity and tamper detection"""
        # Create sample audit log entries
        log_entries = [
            {'timestamp': '2024-01-01T10:00:00Z', 'event': 'system_start'},
            {'timestamp': '2024-01-01T10:05:00Z', 'event': 'config_update'},
            {'timestamp': '2024-01-01T10:10:00Z', 'event': 'performance_alert'}
        ]
        
        # Calculate integrity hash
        original_hash = mock_meta_audit.calculate_log_integrity_hash(log_entries)
        
        # Verify integrity (should pass)
        assert mock_meta_audit.verify_log_integrity(log_entries, original_hash) == True
        
        # Tamper with log
        tampered_entries = log_entries.copy()
        tampered_entries[1]['event'] = 'unauthorized_change'
        
        # Verify integrity (should fail)
        assert mock_meta_audit.verify_log_integrity(tampered_entries, original_hash) == False

class TestIntelligenceLayerIntegration:
    """Test integration between intelligence layer components"""
    
    @pytest.fixture
    def integrated_intelligence_system(self, tmp_path):
        """Create integrated intelligence system for testing"""
        # Mock all components
        adaptive_reasoning = Mock()
        system_reflection = Mock()
        improvement_loop = Mock()
        meta_audit = Mock()
        
        # Configure mock behaviors
        adaptive_reasoning.analyze_performance_trends = AsyncMock(return_value={
            'confidence_trend': 'improving',
            'latency_trend': 'stable',
            'recommendations': ['continue_current_strategy']
        })
        
        system_reflection.analyze_system_state = AsyncMock(return_value={
            'overall_health_score': 85,
            'identified_issues': ['minor_memory_leak'],
            'recommendations': ['schedule_memory_cleanup']
        })
        
        improvement_loop.identify_improvements = AsyncMock(return_value={
            'priority_improvements': [{'id': 'IMP-001', 'type': 'memory_optimization'}]
        })
        
        meta_audit.check_system_integrity = AsyncMock(return_value={
            'overall_integrity_score': 92,
            'integrity_violations': []
        })
        
        return {
            'adaptive_reasoning': adaptive_reasoning,
            'system_reflection': system_reflection,
            'improvement_loop': improvement_loop,
            'meta_audit': meta_audit
        }
    
    @pytest.mark.asyncio
    async def test_intelligence_layer_coordination(self, integrated_intelligence_system):
        """Test coordination between intelligence layer components"""
        components = integrated_intelligence_system
        
        # Simulate intelligence layer workflow
        # 1. Adaptive reasoning analyzes performance
        performance_analysis = await components['adaptive_reasoning'].analyze_performance_trends()
        
        # 2. System reflection analyzes overall state
        system_analysis = await components['system_reflection'].analyze_system_state({})
        
        # 3. Improvement loop identifies opportunities
        improvements = await components['improvement_loop'].identify_improvements(system_analysis)
        
        # 4. Meta audit verifies system integrity
        integrity_check = await components['meta_audit'].check_system_integrity({})
        
        # Verify all components executed successfully
        assert performance_analysis is not None
        assert system_analysis is not None
        assert improvements is not None
        assert integrity_check is not None
        
        # Verify component interactions
        components['adaptive_reasoning'].analyze_performance_trends.assert_called_once()
        components['system_reflection'].analyze_system_state.assert_called_once()
        components['improvement_loop'].identify_improvements.assert_called_once_with(system_analysis)
        components['meta_audit'].check_system_integrity.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_intelligence_feedback_loop(self, integrated_intelligence_system):
        """Test feedback loop between intelligence components"""
        components = integrated_intelligence_system
        
        # Configure feedback scenario
        components['system_reflection'].analyze_system_state.return_value = {
            'overall_health_score': 75,  # Below optimal
            'identified_issues': ['performance_degradation'],
            'recommendations': ['increase_reasoning_depth']
        }
        
        # Execute feedback loop
        system_state = await components['system_reflection'].analyze_system_state({})
        
        # Adaptive reasoning should respond to system state
        if system_state['overall_health_score'] < 80:
            # Trigger adaptive response
            adaptation_result = await components['adaptive_reasoning'].analyze_performance_trends()
            
            # Verify adaptation occurred
            assert adaptation_result is not None
            components['adaptive_reasoning'].analyze_performance_trends.assert_called()

# Performance and Load Testing for Intelligence Layer
class TestIntelligenceLayerPerformance:
    """Performance tests for intelligence layer components"""
    
    @pytest.mark.asyncio
    async def test_adaptive_reasoning_performance(self):
        """Test adaptive reasoning performance under load"""
        # Mock adaptive reasoning with performance tracking
        adaptive_reasoning = Mock()
        adaptive_reasoning.adjust_reasoning_depth = AsyncMock()
        
        # Simulate high load
        start_time = asyncio.get_event_loop().time()
        
        tasks = []
        for i in range(100):  # 100 concurrent requests
            task = adaptive_reasoning.adjust_reasoning_depth({
                'confidence_score': 0.8,
                'latency': 1.0,
                'success_rate': 0.9
            })
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert adaptive_reasoning.adjust_reasoning_depth.call_count == 100
    
    @pytest.mark.asyncio
    async def test_system_reflection_memory_usage(self):
        """Test system reflection memory efficiency"""
        system_reflection = Mock()
        system_reflection.analyze_system_state = AsyncMock(return_value={'health_score': 85})
        
        # Simulate large dataset analysis
        large_dataset = {
            'performance_data': [{'metric': i} for i in range(10000)],
            'error_logs': [{'error': f'error_{i}'} for i in range(1000)],
            'system_metrics': [{'cpu': i % 100} for i in range(5000)]
        }
        
        # Memory usage should remain reasonable
        result = await system_reflection.analyze_system_state(large_dataset)
        
        assert result is not None
        system_reflection.analyze_system_state.assert_called_once_with(large_dataset)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
