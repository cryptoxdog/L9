"""
L9 Real-Time Monitoring Dashboard
Comprehensive system monitoring with live metrics and predictive analytics
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import statistics
import logging
from pathlib import Path

try:  # pragma: no cover - import guard is environment dependent
    import aiohttp  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed when dependency missing
    aiohttp = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - hints for static analyzers only
    import aiohttp as aiohttp_types  # noqa: F401

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Real-time system metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_requests: int
    response_time_ms: float
    error_rate: float
    throughput_rps: float
    
@dataclass
class ComponentHealth:
    """Component health status"""
    component_name: str
    status: str  # healthy, warning, critical, offline
    last_heartbeat: datetime
    error_count: int
    response_time: float
    memory_usage_mb: float
    custom_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_metrics is None:
            self.custom_metrics = {}

@dataclass
class PredictiveAlert:
    """Predictive alert based on trend analysis"""
    alert_id: str
    severity: str  # info, warning, critical
    component: str
    metric: str
    current_value: float
    predicted_value: float
    threshold: float
    time_to_threshold: float  # hours
    confidence: float
    recommended_action: str

class MetricsCollector:
    """Collects metrics from all L9 components"""
    
    def __init__(self):
        self.component_endpoints = {
            'toth_engine': 'http://localhost:8001/metrics',
            'pipeline_orchestrator': 'http://localhost:8002/metrics',
            'optimization_service': 'http://localhost:8003/metrics',
            'deployment_manager': 'http://localhost:8004/metrics'
        }
        self.session: Optional["aiohttp.ClientSession"] = None

    async def __aenter__(self):
        if aiohttp is None:
            logger.warning(
                "aiohttp is not installed; HTTP metrics collection is disabled. "
                "Install aiohttp to enable live endpoint polling"
            )
            return self

        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-wide metrics"""
        import psutil
        
        # System resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O
        net_io = psutil.net_io_counters()
        network_io = {
            'bytes_sent_mb': net_io.bytes_sent / (1024 * 1024),
            'bytes_recv_mb': net_io.bytes_recv / (1024 * 1024),
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        # Mock application metrics (in production, collect from actual services)
        active_requests = 42
        response_time_ms = 125.5
        error_rate = 0.002  # 0.2%
        throughput_rps = 350.0
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io=network_io,
            active_requests=active_requests,
            response_time_ms=response_time_ms,
            error_rate=error_rate,
            throughput_rps=throughput_rps
        )
    
    async def collect_component_health(self) -> List[ComponentHealth]:
        """Collect health status from all components"""
        health_statuses = []
        
        for component, endpoint in self.component_endpoints.items():
            try:
                # In production, make actual HTTP calls
                # For now, generate mock data
                health = ComponentHealth(
                    component_name=component,
                    status=self._determine_health_status(),
                    last_heartbeat=datetime.now(),
                    error_count=0,
                    response_time=50.0,
                    memory_usage_mb=256.0,
                    custom_metrics={
                        'queue_depth': 10,
                        'cache_hit_rate': 0.85,
                        'model_confidence': 0.92
                    }
                )
                health_statuses.append(health)
                
            except Exception as e:
                logger.error(f"Failed to collect health from {component}: {e}")
                health_statuses.append(ComponentHealth(
                    component_name=component,
                    status='offline',
                    last_heartbeat=datetime.now(),
                    error_count=1,
                    response_time=0,
                    memory_usage_mb=0
                ))
        
        return health_statuses
    
    def _determine_health_status(self) -> str:
        """Determine health status based on metrics"""
        import random
        # Mock implementation
        rand = random.random()
        if rand > 0.95:
            return 'critical'
        elif rand > 0.85:
            return 'warning'
        else:
            return 'healthy'

class TrendAnalyzer:
    """Analyzes metric trends for predictive insights"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_metric(self, metric_name: str, value: float, timestamp: datetime):
        """Add metric to history"""
        self.metric_history[metric_name].append({
            'value': value,
            'timestamp': timestamp
        })
    
    def calculate_trend(self, metric_name: str) -> Dict[str, Any]:
        """Calculate trend for a metric"""
        if metric_name not in self.metric_history or len(self.metric_history[metric_name]) < 3:
            return {'trend': 'insufficient_data'}
        
        values = [m['value'] for m in self.metric_history[metric_name]]
        timestamps = [m['timestamp'] for m in self.metric_history[metric_name]]
        
        # Calculate linear regression
        n = len(values)
        if n < 2:
            return {'trend': 'insufficient_data'}
        
        # Convert timestamps to seconds from first timestamp
        time_deltas = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # Calculate slope
        mean_x = sum(time_deltas) / n
        mean_y = sum(values) / n
        
        numerator = sum((time_deltas[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((time_deltas[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Calculate R-squared for confidence
        y_pred = [mean_y + slope * (x - mean_x) for x in time_deltas]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - mean_y) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.001:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        return {
            'trend': direction,
            'slope': slope,
            'current_value': values[-1],
            'mean_value': mean_y,
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'confidence': r_squared,
            'data_points': n
        }
    
    def predict_future_value(self, metric_name: str, hours_ahead: float = 1.0) -> Optional[float]:
        """Predict future value based on trend"""
        trend = self.calculate_trend(metric_name)
        
        if trend['trend'] == 'insufficient_data':
            return None
        
        # Simple linear extrapolation
        seconds_ahead = hours_ahead * 3600
        predicted_value = trend['current_value'] + (trend['slope'] * seconds_ahead)
        
        return predicted_value

class AlertGenerator:
    """Generates alerts based on thresholds and predictions"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_usage': {'warning': 70, 'critical': 90},
            'memory_usage': {'warning': 80, 'critical': 95},
            'error_rate': {'warning': 0.01, 'critical': 0.05},
            'response_time_ms': {'warning': 500, 'critical': 1000}
        }
        self.alert_history: List[PredictiveAlert] = []
    
    def check_current_alerts(self, metrics: SystemMetrics) -> List[PredictiveAlert]:
        """Check for immediate alerts based on current metrics"""
        alerts = []
        
        # Check CPU usage
        if metrics.cpu_usage > self.thresholds['cpu_usage']['critical']:
            alerts.append(self._create_alert(
                'cpu_critical',
                'critical',
                'system',
                'cpu_usage',
                metrics.cpu_usage,
                self.thresholds['cpu_usage']['critical'],
                'Scale up compute resources immediately'
            ))
        elif metrics.cpu_usage > self.thresholds['cpu_usage']['warning']:
            alerts.append(self._create_alert(
                'cpu_warning',
                'warning',
                'system',
                'cpu_usage',
                metrics.cpu_usage,
                self.thresholds['cpu_usage']['warning'],
                'Monitor CPU usage, consider scaling'
            ))
        
        # Check memory usage
        if metrics.memory_usage > self.thresholds['memory_usage']['critical']:
            alerts.append(self._create_alert(
                'memory_critical',
                'critical',
                'system',
                'memory_usage',
                metrics.memory_usage,
                self.thresholds['memory_usage']['critical'],
                'Memory exhaustion imminent, scale or restart services'
            ))
        
        # Check error rate
        if metrics.error_rate > self.thresholds['error_rate']['critical']:
            alerts.append(self._create_alert(
                'error_rate_critical',
                'critical',
                'application',
                'error_rate',
                metrics.error_rate,
                self.thresholds['error_rate']['critical'],
                'High error rate detected, investigate immediately'
            ))
        
        return alerts
    
    def generate_predictive_alerts(
        self, 
        trend_analyzer: TrendAnalyzer,
        hours_ahead: float = 1.0
    ) -> List[PredictiveAlert]:
        """Generate predictive alerts based on trends"""
        predictive_alerts = []
        
        for metric_name, thresholds in self.thresholds.items():
            trend = trend_analyzer.calculate_trend(metric_name)
            
            if trend['trend'] == 'insufficient_data':
                continue
            
            predicted_value = trend_analyzer.predict_future_value(metric_name, hours_ahead)
            
            if predicted_value is None:
                continue
            
            # Check if predicted value will exceed thresholds
            for severity, threshold in thresholds.items():
                if trend['trend'] == 'increasing' and predicted_value > threshold:
                    # Calculate time to threshold
                    if trend['slope'] > 0:
                        time_to_threshold = (threshold - trend['current_value']) / (trend['slope'] / 3600)
                    else:
                        time_to_threshold = float('inf')
                    
                    if 0 < time_to_threshold < hours_ahead * 2:  # Alert if within 2x prediction window
                        alert = PredictiveAlert(
                            alert_id=f"predictive_{metric_name}_{severity}_{int(time.time())}",
                            severity=severity,
                            component='system',
                            metric=metric_name,
                            current_value=trend['current_value'],
                            predicted_value=predicted_value,
                            threshold=threshold,
                            time_to_threshold=time_to_threshold,
                            confidence=trend['confidence'],
                            recommended_action=self._get_recommended_action(metric_name, severity)
                        )
                        predictive_alerts.append(alert)
        
        return predictive_alerts
    
    def _create_alert(
        self, 
        alert_id: str, 
        severity: str, 
        component: str,
        metric: str, 
        current_value: float, 
        threshold: float,
        action: str
    ) -> PredictiveAlert:
        """Create an alert"""
        return PredictiveAlert(
            alert_id=f"{alert_id}_{int(time.time())}",
            severity=severity,
            component=component,
            metric=metric,
            current_value=current_value,
            predicted_value=current_value,  # For immediate alerts
            threshold=threshold,
            time_to_threshold=0,  # Immediate
            confidence=1.0,  # Certain for current alerts
            recommended_action=action
        )
    
    def _get_recommended_action(self, metric: str, severity: str) -> str:
        """Get recommended action for metric and severity"""
        actions = {
            'cpu_usage': {
                'warning': 'Monitor CPU usage trends, prepare to scale horizontally',
                'critical': 'Immediately scale compute resources or optimize workload'
            },
            'memory_usage': {
                'warning': 'Investigate memory leaks, prepare to increase memory',
                'critical': 'Urgent: Add memory or restart services to prevent OOM'
            },
            'error_rate': {
                'warning': 'Review error logs, identify error patterns',
                'critical': 'Deploy fixes or rollback to previous stable version'
            },
            'response_time_ms': {
                'warning': 'Optimize slow queries, review caching strategy',
                'critical': 'Enable circuit breakers, scale services immediately'
            }
        }
        
        return actions.get(metric, {}).get(severity, 'Monitor metric closely')

class RealTimeDashboard:
    """Main real-time monitoring dashboard"""
    
    def __init__(self, update_interval: int = 5):
        self.update_interval = update_interval
        self.metrics_collector = MetricsCollector()
        self.trend_analyzer = TrendAnalyzer()
        self.alert_generator = AlertGenerator()
        self.dashboard_state = {
            'system_metrics': None,
            'component_health': [],
            'active_alerts': [],
            'predictive_alerts': [],
            'metric_history': defaultdict(list)
        }
        self.running = False
    
    async def start(self):
        """Start the real-time dashboard"""
        self.running = True
        logger.info("Starting L9 Real-Time Dashboard")
        
        async with self.metrics_collector as collector:
            while self.running:
                try:
                    # Collect metrics
                    system_metrics = await collector.collect_system_metrics()
                    component_health = await collector.collect_component_health()
                    
                    # Update trend analyzer
                    self._update_trends(system_metrics)
                    
                    # Generate alerts
                    current_alerts = self.alert_generator.check_current_alerts(system_metrics)
                    predictive_alerts = self.alert_generator.generate_predictive_alerts(
                        self.trend_analyzer, 
                        hours_ahead=2.0
                    )
                    
                    # Update dashboard state
                    self.dashboard_state['system_metrics'] = system_metrics
                    self.dashboard_state['component_health'] = component_health
                    self.dashboard_state['active_alerts'] = current_alerts
                    self.dashboard_state['predictive_alerts'] = predictive_alerts
                    
                    # Log summary
                    self._log_summary()
                    
                    # Wait for next update
                    await asyncio.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"Dashboard update error: {e}")
                    await asyncio.sleep(self.update_interval)
    
    def stop(self):
        """Stop the dashboard"""
        self.running = False
        logger.info("Stopping L9 Real-Time Dashboard")
    
    def _update_trends(self, metrics: SystemMetrics):
        """Update trend analyzer with new metrics"""
        self.trend_analyzer.add_metric('cpu_usage', metrics.cpu_usage, metrics.timestamp)
        self.trend_analyzer.add_metric('memory_usage', metrics.memory_usage, metrics.timestamp)
        self.trend_analyzer.add_metric('error_rate', metrics.error_rate, metrics.timestamp)
        self.trend_analyzer.add_metric('response_time_ms', metrics.response_time_ms, metrics.timestamp)
        self.trend_analyzer.add_metric('throughput_rps', metrics.throughput_rps, metrics.timestamp)
        
        # Store in history
        for metric_name in ['cpu_usage', 'memory_usage', 'error_rate', 'response_time_ms']:
            self.dashboard_state['metric_history'][metric_name].append({
                'timestamp': metrics.timestamp.isoformat(),
                'value': getattr(metrics, metric_name)
            })
            
            # Keep only last 100 data points
            if len(self.dashboard_state['metric_history'][metric_name]) > 100:
                self.dashboard_state['metric_history'][metric_name] = \
                    self.dashboard_state['metric_history'][metric_name][-100:]
    
    def _log_summary(self):
        """Log dashboard summary"""
        if self.dashboard_state['system_metrics']:
            metrics = self.dashboard_state['system_metrics']
            logger.info(
                f"System Status - CPU: {metrics.cpu_usage:.1f}%, "
                f"Memory: {metrics.memory_usage:.1f}%, "
                f"Requests: {metrics.active_requests}, "
                f"Response Time: {metrics.response_time_ms:.1f}ms, "
                f"Error Rate: {metrics.error_rate:.3%}"
            )
            
            # Log alerts if any
            total_alerts = len(self.dashboard_state['active_alerts']) + \
                          len(self.dashboard_state['predictive_alerts'])
            
            if total_alerts > 0:
                critical_alerts = [a for a in self.dashboard_state['active_alerts'] 
                                 if a.severity == 'critical']
                if critical_alerts:
                    logger.warning(f"CRITICAL ALERTS: {len(critical_alerts)}")
                    for alert in critical_alerts:
                        logger.warning(f"  - {alert.metric}: {alert.current_value:.2f} "
                                     f"(threshold: {alert.threshold})")
    
    def get_dashboard_state(self) -> Dict[str, Any]:
        """Get current dashboard state"""
        # Convert dataclasses to dicts for JSON serialization
        state = self.dashboard_state.copy()
        
        if state['system_metrics']:
            state['system_metrics'] = asdict(state['system_metrics'])
        
        state['component_health'] = [asdict(h) for h in state['component_health']]
        state['active_alerts'] = [asdict(a) for a in state['active_alerts']]
        state['predictive_alerts'] = [asdict(a) for a in state['predictive_alerts']]
        
        return state
    
    async def export_metrics(self, output_path: str):
        """Export metrics history to file"""
        export_data = {
            'export_time': datetime.now().isoformat(),
            'dashboard_state': self.get_dashboard_state(),
            'metric_trends': {}
        }
        
        # Add trend analysis
        for metric_name in self.dashboard_state['metric_history'].keys():
            trend = self.trend_analyzer.calculate_trend(metric_name)
            export_data['metric_trends'][metric_name] = trend
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {output_path}")

# CLI Interface
async def main():
    """CLI interface for real-time dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='L9 Real-Time Monitoring Dashboard')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    parser.add_argument('--export', help='Export metrics to file')
    parser.add_argument('--duration', type=int, help='Run for specified minutes')
    
    args = parser.parse_args()
    
    # Create dashboard
    dashboard = RealTimeDashboard(update_interval=args.interval)
    
    try:
        if args.duration:
            # Run for specified duration
            logger.info(f"Running dashboard for {args.duration} minutes")
            
            async def run_timed():
                dashboard_task = asyncio.create_task(dashboard.start())
                await asyncio.sleep(args.duration * 60)
                dashboard.stop()
                await dashboard_task
            
            await run_timed()
        else:
            # Run until interrupted
            await dashboard.start()
    
    except KeyboardInterrupt:
        logger.info("Dashboard interrupted by user")
    finally:
        dashboard.stop()
        
        # Export metrics if requested
        if args.export:
            await dashboard.export_metrics(args.export)

if __name__ == "__main__":
    asyncio.run(main())
