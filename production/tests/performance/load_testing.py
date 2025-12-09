"""
L9 Performance and Load Testing Framework
Comprehensive performance testing for all L9 components under various load conditions
"""

import asyncio
import time
import statistics
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for load testing"""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    total_duration: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_rate: float
    
    def __post_init__(self):
        self.success_rate = (self.successful_requests / max(1, self.total_requests)) * 100
        self.error_rate = (self.failed_requests / max(1, self.total_requests)) * 100

@dataclass
class LoadTestConfig:
    """Configuration for load testing"""
    concurrent_users: int = 10
    requests_per_user: int = 10
    ramp_up_time: float = 5.0
    test_duration: int = 60
    think_time: float = 1.0
    timeout: float = 30.0
    
class SystemMonitor:
    """System resource monitoring during tests"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics: List[Dict[str, Any]] = []
    
    async def start_monitoring(self, interval: float = 1.0):
        """Start system monitoring"""
        self.monitoring = True
        self.metrics = []
        
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                metric = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_mb': memory.used / (1024 * 1024),
                    'memory_available_mb': memory.available / (1024 * 1024),
                    'disk_percent': disk.percent,
                    'disk_used_gb': disk.used / (1024 * 1024 * 1024)
                }
                
                self.metrics.append(metric)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                break
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average system metrics"""
        if not self.metrics:
            return {}
        
        return {
            'avg_cpu_percent': statistics.mean(m['cpu_percent'] for m in self.metrics),
            'avg_memory_percent': statistics.mean(m['memory_percent'] for m in self.metrics),
            'avg_memory_used_mb': statistics.mean(m['memory_used_mb'] for m in self.metrics),
            'max_memory_used_mb': max(m['memory_used_mb'] for m in self.metrics),
            'avg_disk_percent': statistics.mean(m['disk_percent'] for m in self.metrics)
        }

class LoadTestRunner:
    """Main load testing framework"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.test_results: List[PerformanceMetrics] = []
    
    async def run_load_test(
        self,
        test_name: str,
        test_function: Callable,
        config: LoadTestConfig,
        test_data: Optional[List[Any]] = None
    ) -> PerformanceMetrics:
        """Run a load test with specified configuration"""
        
        logger.info(f"Starting load test: {test_name}")
        logger.info(f"Config: {config.concurrent_users} users, {config.requests_per_user} requests each")
        
        # Start system monitoring
        monitor_task = asyncio.create_task(self.system_monitor.start_monitoring())
        
        # Prepare test data
        if test_data is None:
            test_data = [f"test_data_{i}" for i in range(config.concurrent_users * config.requests_per_user)]
        
        # Track response times and results
        response_times: List[float] = []
        successful_requests = 0
        failed_requests = 0
        
        start_time = time.time()
        
        try:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(config.concurrent_users)
            
            # Create tasks for all requests
            tasks = []
            for i in range(config.concurrent_users):
                for j in range(config.requests_per_user):
                    data_index = (i * config.requests_per_user + j) % len(test_data)
                    task = self._execute_request(
                        semaphore,
                        test_function,
                        test_data[data_index],
                        config.timeout,
                        config.think_time,
                        i * (config.ramp_up_time / config.concurrent_users)  # Stagger start times
                    )
                    tasks.append(task)
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    failed_requests += 1
                    logger.error(f"Request failed: {result}")
                else:
                    response_time, success = result
                    response_times.append(response_time)
                    if success:
                        successful_requests += 1
                    else:
                        failed_requests += 1
            
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            raise
        finally:
            # Stop monitoring
            self.system_monitor.stop_monitoring()
            monitor_task.cancel()
            
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p50_response_time = sorted_times[int(len(sorted_times) * 0.5)]
            p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_response_time = 0.0
            min_response_time = 0.0
            max_response_time = 0.0
            p50_response_time = 0.0
            p95_response_time = 0.0
            p99_response_time = 0.0
        
        # Get system metrics
        system_metrics = self.system_monitor.get_average_metrics()
        
        # Create performance metrics
        metrics = PerformanceMetrics(
            test_name=test_name,
            total_requests=len(tasks),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=len(tasks) / total_duration if total_duration > 0 else 0,
            total_duration=total_duration,
            memory_usage_mb=system_metrics.get('avg_memory_used_mb', 0),
            cpu_usage_percent=system_metrics.get('avg_cpu_percent', 0),
            error_rate=0.0  # Will be calculated in __post_init__
        )
        
        self.test_results.append(metrics)
        
        logger.info(f"Load test completed: {test_name}")
        logger.info(f"Results: {successful_requests}/{len(tasks)} successful, "
                   f"avg response time: {avg_response_time:.2f}s, "
                   f"RPS: {metrics.requests_per_second:.2f}")
        
        return metrics
    
    async def _execute_request(
        self,
        semaphore: asyncio.Semaphore,
        test_function: Callable,
        test_data: Any,
        timeout: float,
        think_time: float,
        delay: float
    ) -> tuple[float, bool]:
        """Execute a single request with timing"""
        
        # Apply ramp-up delay
        if delay > 0:
            await asyncio.sleep(delay)
        
        async with semaphore:
            start_time = time.time()
            success = False
            
            try:
                # Execute the test function
                if asyncio.iscoroutinefunction(test_function):
                    result = await asyncio.wait_for(test_function(test_data), timeout=timeout)
                else:
                    result = test_function(test_data)
                
                success = True
                
            except asyncio.TimeoutError:
                logger.warning(f"Request timed out after {timeout}s")
            except Exception as e:
                logger.error(f"Request failed: {e}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Apply think time
            if think_time > 0:
                await asyncio.sleep(think_time)
            
            return response_time, success
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate performance test report"""
        
        if not self.test_results:
            return {"error": "No test results available"}
        
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "test_timestamp": datetime.now().isoformat(),
                "overall_success_rate": statistics.mean(m.success_rate for m in self.test_results)
            },
            "test_results": [asdict(result) for result in self.test_results],
            "performance_analysis": self._analyze_performance()
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Performance report saved to {output_file}")
        
        return report
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance across all tests"""
        
        if not self.test_results:
            return {}
        
        analysis = {
            "response_time_analysis": {
                "avg_across_tests": statistics.mean(m.avg_response_time for m in self.test_results),
                "min_across_tests": min(m.min_response_time for m in self.test_results),
                "max_across_tests": max(m.max_response_time for m in self.test_results),
                "p95_across_tests": statistics.mean(m.p95_response_time for m in self.test_results)
            },
            "throughput_analysis": {
                "avg_rps": statistics.mean(m.requests_per_second for m in self.test_results),
                "max_rps": max(m.requests_per_second for m in self.test_results),
                "total_requests": sum(m.total_requests for m in self.test_results)
            },
            "resource_usage": {
                "avg_memory_mb": statistics.mean(m.memory_usage_mb for m in self.test_results),
                "max_memory_mb": max(m.memory_usage_mb for m in self.test_results),
                "avg_cpu_percent": statistics.mean(m.cpu_usage_percent for m in self.test_results)
            },
            "reliability": {
                "overall_success_rate": statistics.mean(m.success_rate for m in self.test_results),
                "overall_error_rate": statistics.mean(m.error_rate for m in self.test_results),
                "total_failures": sum(m.failed_requests for m in self.test_results)
            }
        }
        
        return analysis

# Specific Load Tests for L9 Components

class L9ComponentLoadTests:
    """Load tests for specific L9 components"""
    
    def __init__(self):
        self.load_runner = LoadTestRunner()
    
    async def test_toth_reasoning_load(self) -> PerformanceMetrics:
        """Load test for ToTh reasoning engine"""
        
        # Import ToTh engine
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from toth_integration.production_toth_engine import ProductionToThEngine, ToThConfig, ModelProvider, ReasoningMode
        
        # Create engine
        config = ToThConfig(model_provider=ModelProvider.MOCK)
        engine = ProductionToThEngine(config)
        
        # Test function
        async def reasoning_test(query_data):
            query, mode = query_data
            result = await engine.reason(query, mode)
            return result.overall_confidence > 0.5
        
        # Test data
        test_queries = [
            ("Analyze system performance bottlenecks", ReasoningMode.ABDUCTIVE),
            ("If all services use JWT tokens, what authentication method should we use?", ReasoningMode.DEDUCTIVE),
            ("Based on these error patterns, what can we generalize?", ReasoningMode.INDUCTIVE),
            ("Design a scalable microservices architecture", ReasoningMode.HYBRID)
        ] * 25  # 100 total queries
        
        # Load test configuration
        config = LoadTestConfig(
            concurrent_users=20,
            requests_per_user=5,
            ramp_up_time=10.0,
            think_time=0.5
        )
        
        return await self.load_runner.run_load_test(
            "ToTh Reasoning Load Test",
            reasoning_test,
            config,
            test_queries
        )
    
    async def test_pipeline_deployment_load(self) -> PerformanceMetrics:
        """Load test for pipeline deployment system"""
        
        # Import pipeline components
        from pipeline.orchestration_engine import ProductionOrchestrator, DeploymentConfig, DeploymentStrategy
        
        # Mock orchestrator
        class MockOrchestrator:
            async def deploy(self, config, context=None):
                # Simulate deployment time
                await asyncio.sleep(0.1)
                from unittest.mock import Mock
                return Mock(
                    deployment_id=f"deploy-{int(time.time() * 1000)}",
                    status="SUCCESS",
                    version=config.version
                )
        
        orchestrator = MockOrchestrator()
        
        # Test function
        async def deployment_test(deployment_data):
            env, version, strategy = deployment_data
            config = Mock(
                environment=env,
                version=version,
                strategy=strategy
            )
            result = await orchestrator.deploy(config)
            return result.status == "SUCCESS"
        
        # Test data
        test_deployments = [
            ("staging", "v1.0.0", DeploymentStrategy.BLUE_GREEN),
            ("production", "v1.0.1", DeploymentStrategy.CANARY),
            ("development", "v1.0.2", DeploymentStrategy.ROLLING),
            ("testing", "v1.0.3", DeploymentStrategy.DIRECT)
        ] * 25  # 100 total deployments
        
        # Load test configuration
        config = LoadTestConfig(
            concurrent_users=15,
            requests_per_user=7,
            ramp_up_time=5.0,
            think_time=1.0
        )
        
        return await self.load_runner.run_load_test(
            "Pipeline Deployment Load Test",
            deployment_test,
            config,
            test_deployments
        )
    
    async def test_optimization_cache_load(self) -> PerformanceMetrics:
        """Load test for optimization and caching system"""
        
        # Import optimization components
        from toth_integration.optimization import ToThOptimizer, OptimizationConfig
        
        # Create optimizer
        opt_config = OptimizationConfig(
            max_cache_size_mb=50,
            enable_query_optimization=True,
            enable_batch_processing=True
        )
        optimizer = ToThOptimizer(opt_config)
        
        # Test function
        async def optimization_test(query_data):
            query, mode = query_data
            result, opt_info = await optimizer.optimize_reasoning_request(query, mode)
            return result is not None
        
        # Test data with repeated queries to test caching
        base_queries = [
            "What are microservices best practices?",
            "How to implement API rate limiting?",
            "Database optimization techniques",
            "Security patterns for web applications",
            "Monitoring and alerting strategies"
        ]
        
        test_queries = []
        for i in range(20):
            for query in base_queries:
                test_queries.append((f"{query} - variation {i % 3}", "hybrid"))
        
        # Load test configuration
        config = LoadTestConfig(
            concurrent_users=25,
            requests_per_user=4,
            ramp_up_time=8.0,
            think_time=0.2
        )
        
        return await self.load_runner.run_load_test(
            "Optimization Cache Load Test",
            optimization_test,
            config,
            test_queries
        )
    
    async def test_environment_sync_load(self) -> PerformanceMetrics:
        """Load test for environment synchronization"""
        
        # Import environment sync components
        from pipeline.environment_sync import EnvironmentSynchronizer, ConfigType
        
        # Mock synchronizer
        class MockSynchronizer:
            async def sync_environments(self, source, target, config_types=None):
                # Simulate sync time
                await asyncio.sleep(0.05)
                from unittest.mock import Mock
                return Mock(
                    source_environment=source,
                    target_environment=target,
                    status="IN_SYNC",
                    changes=[f"synced_{len(config_types or [])}"]
                )
        
        synchronizer = MockSynchronizer()
        
        # Test function
        async def sync_test(sync_data):
            source, target, config_types = sync_data
            result = await synchronizer.sync_environments(source, target, config_types)
            return result.status == "IN_SYNC"
        
        # Test data
        environments = ["dev", "staging", "prod", "test"]
        config_types_combinations = [
            [ConfigType.ENVIRONMENT_VARIABLES],
            [ConfigType.SECRETS],
            [ConfigType.CONFIG_FILES],
            [ConfigType.DEPENDENCIES],
            [ConfigType.ENVIRONMENT_VARIABLES, ConfigType.SECRETS]
        ]
        
        test_syncs = []
        for i in range(50):
            source = environments[i % len(environments)]
            target = environments[(i + 1) % len(environments)]
            config_types = config_types_combinations[i % len(config_types_combinations)]
            test_syncs.append((source, target, config_types))
        
        # Load test configuration
        config = LoadTestConfig(
            concurrent_users=10,
            requests_per_user=10,
            ramp_up_time=3.0,
            think_time=0.1
        )
        
        return await self.load_runner.run_load_test(
            "Environment Sync Load Test",
            sync_test,
            config,
            test_syncs
        )
    
    async def test_rollback_system_load(self) -> PerformanceMetrics:
        """Load test for rollback system"""
        
        # Mock rollback system
        class MockRollbackSystem:
            async def execute_rollback(self, environment, trigger, metrics):
                # Simulate rollback time
                await asyncio.sleep(0.2)
                from unittest.mock import Mock
                return Mock(
                    environment=environment,
                    status="completed",
                    target_version="v1.0.0"
                )
        
        rollback_system = MockRollbackSystem()
        
        # Test function
        async def rollback_test(rollback_data):
            env, trigger, metrics = rollback_data
            result = await rollback_system.execute_rollback(env, trigger, metrics)
            return result.status == "completed"
        
        # Test data
        from pipeline.rollback_system import RollbackTrigger
        
        test_rollbacks = []
        environments = ["staging", "production", "test"]
        triggers = [RollbackTrigger.ERROR_RATE_THRESHOLD, RollbackTrigger.HEALTH_CHECK_FAILURE, RollbackTrigger.PERFORMANCE_DEGRADATION]
        
        for i in range(30):
            env = environments[i % len(environments)]
            trigger = triggers[i % len(triggers)]
            metrics = {"error_rate": 0.1, "response_time": 5.0}
            test_rollbacks.append((env, trigger, metrics))
        
        # Load test configuration
        config = LoadTestConfig(
            concurrent_users=5,
            requests_per_user=6,
            ramp_up_time=2.0,
            think_time=0.5
        )
        
        return await self.load_runner.run_load_test(
            "Rollback System Load Test",
            rollback_test,
            config,
            test_rollbacks
        )
    
    async def run_all_load_tests(self) -> Dict[str, PerformanceMetrics]:
        """Run all load tests and return results"""
        
        logger.info("Starting comprehensive L9 load testing suite")
        
        results = {}
        
        # Run individual component tests
        test_methods = [
            ("toth_reasoning", self.test_toth_reasoning_load),
            ("pipeline_deployment", self.test_pipeline_deployment_load),
            ("optimization_cache", self.test_optimization_cache_load),
            ("environment_sync", self.test_environment_sync_load),
            ("rollback_system", self.test_rollback_system_load)
        ]
        
        for test_name, test_method in test_methods:
            try:
                logger.info(f"Running {test_name} load test...")
                result = await test_method()
                results[test_name] = result
                
                # Force garbage collection between tests
                gc.collect()
                
                # Brief pause between tests
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logger.error(f"Load test {test_name} failed: {e}")
                results[test_name] = None
        
        logger.info("All load tests completed")
        return results

# Stress Testing
class StressTestRunner:
    """Stress testing with gradually increasing load"""
    
    def __init__(self):
        self.load_runner = LoadTestRunner()
    
    async def run_stress_test(
        self,
        test_name: str,
        test_function: Callable,
        max_users: int = 100,
        step_size: int = 10,
        step_duration: int = 30
    ) -> List[PerformanceMetrics]:
        """Run stress test with increasing load"""
        
        logger.info(f"Starting stress test: {test_name}")
        logger.info(f"Ramping up to {max_users} users in steps of {step_size}")
        
        results = []
        
        for users in range(step_size, max_users + 1, step_size):
            config = LoadTestConfig(
                concurrent_users=users,
                requests_per_user=5,
                ramp_up_time=5.0,
                test_duration=step_duration
            )
            
            try:
                result = await self.load_runner.run_load_test(
                    f"{test_name} - {users} users",
                    test_function,
                    config
                )
                results.append(result)
                
                # Check if system is degrading
                if result.error_rate > 50 or result.avg_response_time > 30:
                    logger.warning(f"System degradation detected at {users} users")
                    break
                
            except Exception as e:
                logger.error(f"Stress test failed at {users} users: {e}")
                break
            
            # Brief pause between steps
            await asyncio.sleep(5.0)
        
        return results

# CLI Interface
async def main():
    """CLI interface for load testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='L9 Performance Load Testing')
    parser.add_argument('--test', choices=['all', 'toth', 'pipeline', 'optimization', 'sync', 'rollback', 'stress'], 
                       default='all', help='Test to run')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--requests', type=int, default=10, help='Requests per user')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    # Initialize test runner
    component_tests = L9ComponentLoadTests()
    
    try:
        if args.test == 'all':
            results = await component_tests.run_all_load_tests()
            
            # Generate comprehensive report
            report = component_tests.load_runner.generate_report(args.output)
            
            print("\n=== L9 Load Testing Results ===")
            for test_name, result in results.items():
                if result:
                    print(f"\n{test_name.upper()}:")
                    print(f"  Success Rate: {result.success_rate:.1f}%")
                    print(f"  Avg Response Time: {result.avg_response_time:.2f}s")
                    print(f"  Requests/sec: {result.requests_per_second:.2f}")
                    print(f"  P95 Response Time: {result.p95_response_time:.2f}s")
                else:
                    print(f"\n{test_name.upper()}: FAILED")
        
        elif args.test == 'toth':
            result = await component_tests.test_toth_reasoning_load()
            print(f"ToTh Reasoning Test: {result.success_rate:.1f}% success, {result.avg_response_time:.2f}s avg")
        
        elif args.test == 'pipeline':
            result = await component_tests.test_pipeline_deployment_load()
            print(f"Pipeline Test: {result.success_rate:.1f}% success, {result.avg_response_time:.2f}s avg")
        
        elif args.test == 'optimization':
            result = await component_tests.test_optimization_cache_load()
            print(f"Optimization Test: {result.success_rate:.1f}% success, {result.avg_response_time:.2f}s avg")
        
        elif args.test == 'sync':
            result = await component_tests.test_environment_sync_load()
            print(f"Environment Sync Test: {result.success_rate:.1f}% success, {result.avg_response_time:.2f}s avg")
        
        elif args.test == 'rollback':
            result = await component_tests.test_rollback_system_load()
            print(f"Rollback Test: {result.success_rate:.1f}% success, {result.avg_response_time:.2f}s avg")
        
        elif args.test == 'stress':
            stress_runner = StressTestRunner()
            
            # Simple stress test function
            async def simple_test(data):
                await asyncio.sleep(0.1)
                return True
            
            results = await stress_runner.run_stress_test(
                "L9 System Stress Test",
                simple_test,
                max_users=args.users
            )
            
            print(f"\nStress Test Results ({len(results)} steps):")
            for i, result in enumerate(results):
                users = (i + 1) * 10
                print(f"  {users} users: {result.success_rate:.1f}% success, {result.avg_response_time:.2f}s avg")
        
    except Exception as e:
        print(f"Load testing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
