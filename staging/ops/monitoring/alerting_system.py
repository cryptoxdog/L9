"""
L9 Intelligent Alerting System
Automated alerting with smart routing and response capabilities
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

try:  # pragma: no cover - import guard is environment dependent
    import aiohttp  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed when dependency missing
    aiohttp = None  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"

class ResponseAction(Enum):
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROLLBACK = "rollback"
    CIRCUIT_BREAKER = "circuit_breaker"
    CLEAR_CACHE = "clear_cache"
    NOTIFY_ONCALL = "notify_oncall"

@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    component: str
    metric: str
    message: str
    current_value: Any
    threshold_value: Any
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AlertRoute:
    """Alert routing configuration"""
    severity_levels: List[AlertSeverity]
    components: List[str]
    channels: List[AlertChannel]
    recipients: List[str]
    response_actions: List[ResponseAction]
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}

@dataclass
class AlertResponse:
    """Alert response record"""
    alert_id: str
    action_taken: ResponseAction
    timestamp: datetime
    success: bool
    details: str
    automated: bool = True

class AlertRouter:
    """Routes alerts to appropriate channels and handlers"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.routes = self._load_routing_config()
        self.channel_handlers = {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.SMS: self._send_sms_alert,
            AlertChannel.PAGERDUTY: self._send_pagerduty_alert
        }
    
    def _load_routing_config(self) -> List[AlertRoute]:
        """Load alert routing configuration"""
        # Default routing configuration
        return [
            AlertRoute(
                severity_levels=[AlertSeverity.EMERGENCY],
                components=["all"],
                channels=[AlertChannel.PAGERDUTY, AlertChannel.SMS, AlertChannel.EMAIL],
                recipients=["oncall@example.com", "+1234567890"],
                response_actions=[ResponseAction.NOTIFY_ONCALL, ResponseAction.CIRCUIT_BREAKER]
            ),
            AlertRoute(
                severity_levels=[AlertSeverity.CRITICAL],
                components=["toth_engine", "pipeline_orchestrator"],
                channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
                recipients=["dev-alerts@example.com", "#critical-alerts"],
                response_actions=[ResponseAction.RESTART_SERVICE, ResponseAction.ROLLBACK]
            ),
            AlertRoute(
                severity_levels=[AlertSeverity.WARNING],
                components=["all"],
                channels=[AlertChannel.SLACK],
                recipients=["#monitoring-alerts"],
                response_actions=[ResponseAction.SCALE_UP]
            ),
            AlertRoute(
                severity_levels=[AlertSeverity.INFO],
                components=["all"],
                channels=[AlertChannel.WEBHOOK],
                recipients=["http://monitoring.example.com/webhook"],
                response_actions=[]
            )
        ]
    
    async def route_alert(self, alert: Alert) -> List[str]:
        """Route alert to appropriate channels"""
        routed_channels = []
        
        for route in self.routes:
            if self._matches_route(alert, route):
                for channel in route.channels:
                    try:
                        await self.channel_handlers[channel](alert, route.recipients)
                        routed_channels.append(channel.value)
                    except Exception as e:
                        logger.error(f"Failed to send alert via {channel.value}: {e}")
        
        return routed_channels
    
    def _matches_route(self, alert: Alert, route: AlertRoute) -> bool:
        """Check if alert matches routing criteria"""
        # Check severity
        if alert.severity not in route.severity_levels:
            return False
        
        # Check component
        if "all" not in route.components and alert.component not in route.components:
            return False
        
        # Check additional conditions
        if route.conditions:
            for key, value in route.conditions.items():
                if key == "metric_pattern" and value not in alert.metric:
                    return False
                elif key == "time_window":
                    # Check if alert is within time window
                    start_hour = value.get("start_hour", 0)
                    end_hour = value.get("end_hour", 24)
                    current_hour = datetime.now().hour
                    if not (start_hour <= current_hour < end_hour):
                        return False
        
        return True
    
    async def _send_email_alert(self, alert: Alert, recipients: List[str]):
        """Send email alert"""
        logger.info(f"Sending email alert to {recipients}")
        
        # In production, implement actual email sending
        # For now, log the alert
        logger.info(f"Email Alert - {alert.severity.value.upper()}: {alert.message}")
    
    async def _send_slack_alert(self, alert: Alert, recipients: List[str]):
        """Send Slack alert"""
        logger.info(f"Sending Slack alert to {recipients}")
        
        # In production, use Slack webhook
        # For now, log the alert
        logger.info(f"Slack Alert - {alert.severity.value.upper()}: {alert.message}")
    
    async def _send_webhook_alert(self, alert: Alert, recipients: List[str]):
        """Send webhook alert"""
        for webhook_url in recipients:
            if aiohttp is None:
                logger.warning(
                    "aiohttp is not installed; skipping webhook delivery to %s. "
                    "Install aiohttp to enable webhook alerts",
                    webhook_url
                )
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    alert_data = asdict(alert)
                    alert_data['timestamp'] = alert.timestamp.isoformat()

                    # Mock webhook call
                    logger.info(f"Webhook Alert sent to {webhook_url}")

            except Exception as e:
                logger.error(f"Webhook alert failed for {webhook_url}: {e}")
    
    async def _send_sms_alert(self, alert: Alert, recipients: List[str]):
        """Send SMS alert"""
        logger.info(f"Sending SMS alert to {recipients}")
        
        # In production, use SMS service like Twilio
        # For now, log the alert
        logger.info(f"SMS Alert - {alert.severity.value.upper()}: {alert.message[:160]}")
    
    async def _send_pagerduty_alert(self, alert: Alert, recipients: List[str]):
        """Send PagerDuty alert"""
        logger.info(f"Triggering PagerDuty alert")
        
        # In production, use PagerDuty API
        # For now, log the alert
        logger.info(f"PagerDuty Alert - {alert.severity.value.upper()}: {alert.message}")

class AutomatedResponder:
    """Executes automated response actions for alerts"""
    
    def __init__(self):
        self.response_handlers = {
            ResponseAction.RESTART_SERVICE: self._restart_service,
            ResponseAction.SCALE_UP: self._scale_up,
            ResponseAction.SCALE_DOWN: self._scale_down,
            ResponseAction.ROLLBACK: self._rollback,
            ResponseAction.CIRCUIT_BREAKER: self._enable_circuit_breaker,
            ResponseAction.CLEAR_CACHE: self._clear_cache,
            ResponseAction.NOTIFY_ONCALL: self._notify_oncall
        }
        self.response_history: List[AlertResponse] = []
    
    async def respond_to_alert(self, alert: Alert, actions: List[ResponseAction]) -> List[AlertResponse]:
        """Execute response actions for alert"""
        responses = []
        
        for action in actions:
            if action in self.response_handlers:
                try:
                    response = await self.response_handlers[action](alert)
                    responses.append(response)
                    self.response_history.append(response)
                    logger.info(f"Executed {action.value} for alert {alert.alert_id}")
                except Exception as e:
                    logger.error(f"Failed to execute {action.value}: {e}")
                    response = AlertResponse(
                        alert_id=alert.alert_id,
                        action_taken=action,
                        timestamp=datetime.now(),
                        success=False,
                        details=str(e)
                    )
                    responses.append(response)
        
        return responses
    
    async def _restart_service(self, alert: Alert) -> AlertResponse:
        """Restart affected service"""
        component = alert.component
        
        # In production, implement actual service restart
        logger.info(f"Restarting service: {component}")
        await asyncio.sleep(2)  # Simulate restart time
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.RESTART_SERVICE,
            timestamp=datetime.now(),
            success=True,
            details=f"Service {component} restarted successfully"
        )
    
    async def _scale_up(self, alert: Alert) -> AlertResponse:
        """Scale up resources"""
        # Determine scaling factor based on severity
        scale_factor = 2 if alert.severity == AlertSeverity.CRITICAL else 1.5
        
        logger.info(f"Scaling up {alert.component} by {scale_factor}x")
        
        # In production, call cloud provider API
        await asyncio.sleep(1)  # Simulate scaling time
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.SCALE_UP,
            timestamp=datetime.now(),
            success=True,
            details=f"Scaled {alert.component} by {scale_factor}x"
        )
    
    async def _scale_down(self, alert: Alert) -> AlertResponse:
        """Scale down resources"""
        logger.info(f"Scaling down {alert.component}")
        
        # In production, implement safe scale-down logic
        await asyncio.sleep(1)
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.SCALE_DOWN,
            timestamp=datetime.now(),
            success=True,
            details=f"Scaled down {alert.component}"
        )
    
    async def _rollback(self, alert: Alert) -> AlertResponse:
        """Trigger deployment rollback"""
        logger.info(f"Triggering rollback for {alert.component}")
        
        # In production, call rollback system
        from pipeline.rollback_system import AutomatedRollbackSystem
        
        # Mock rollback
        await asyncio.sleep(3)
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.ROLLBACK,
            timestamp=datetime.now(),
            success=True,
            details=f"Rolled back {alert.component} to previous stable version"
        )
    
    async def _enable_circuit_breaker(self, alert: Alert) -> AlertResponse:
        """Enable circuit breaker for failing service"""
        logger.info(f"Enabling circuit breaker for {alert.component}")
        
        # In production, configure circuit breaker
        await asyncio.sleep(0.5)
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.CIRCUIT_BREAKER,
            timestamp=datetime.now(),
            success=True,
            details=f"Circuit breaker enabled for {alert.component}"
        )
    
    async def _clear_cache(self, alert: Alert) -> AlertResponse:
        """Clear system caches"""
        logger.info(f"Clearing cache for {alert.component}")
        
        # In production, clear actual caches
        await asyncio.sleep(0.5)
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.CLEAR_CACHE,
            timestamp=datetime.now(),
            success=True,
            details=f"Cache cleared for {alert.component}"
        )
    
    async def _notify_oncall(self, alert: Alert) -> AlertResponse:
        """Notify on-call engineer"""
        logger.info("Notifying on-call engineer")
        
        # In production, page on-call via PagerDuty
        await asyncio.sleep(0.1)
        
        return AlertResponse(
            alert_id=alert.alert_id,
            action_taken=ResponseAction.NOTIFY_ONCALL,
            timestamp=datetime.now(),
            success=True,
            details="On-call engineer notified"
        )

class AlertingSystem:
    """Main alerting system orchestrator"""
    
    def __init__(self, config_dir: str = "config/alerting"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.alert_router = AlertRouter(self.config_dir / "routing.yaml")
        self.automated_responder = AutomatedResponder()
        self.alert_history: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
    
    async def process_alert(self, alert: Alert) -> Dict[str, Any]:
        """Process incoming alert"""
        logger.info(f"Processing alert: {alert.alert_id} - {alert.severity.value} - {alert.message}")
        
        # Store alert
        self.alert_history.append(alert)
        self.active_alerts[alert.alert_id] = alert
        
        # Route alert to channels
        routed_channels = await self.alert_router.route_alert(alert)
        
        # Get applicable response actions
        response_actions = self._get_response_actions(alert)
        
        # Execute automated responses
        responses = await self.automated_responder.respond_to_alert(alert, response_actions)
        
        return {
            'alert_id': alert.alert_id,
            'routed_channels': routed_channels,
            'response_actions': [r.action_taken.value for r in responses],
            'success': all(r.success for r in responses),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_response_actions(self, alert: Alert) -> List[ResponseAction]:
        """Determine response actions for alert"""
        actions = []
        
        # Critical alerts get immediate response
        if alert.severity == AlertSeverity.CRITICAL:
            if "error_rate" in alert.metric:
                actions.extend([ResponseAction.ROLLBACK, ResponseAction.CIRCUIT_BREAKER])
            elif "memory" in alert.metric:
                actions.extend([ResponseAction.RESTART_SERVICE, ResponseAction.CLEAR_CACHE])
            elif "cpu" in alert.metric:
                actions.append(ResponseAction.SCALE_UP)
        
        # Warning alerts get proactive response
        elif alert.severity == AlertSeverity.WARNING:
            if "cpu" in alert.metric or "memory" in alert.metric:
                actions.append(ResponseAction.SCALE_UP)
        
        # Emergency always notifies on-call
        if alert.severity == AlertSeverity.EMERGENCY:
            actions.append(ResponseAction.NOTIFY_ONCALL)
        
        return actions
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.metadata['acknowledged'] = True
            alert.metadata['acknowledged_by'] = acknowledged_by
            alert.metadata['acknowledged_at'] = datetime.now().isoformat()
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str, resolution: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts.pop(alert_id)
            alert.metadata['resolved'] = True
            alert.metadata['resolved_by'] = resolved_by
            alert.metadata['resolved_at'] = datetime.now().isoformat()
            alert.metadata['resolution'] = resolution
            logger.info(f"Alert {alert_id} resolved by {resolved_by}: {resolution}")
            return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alert_history if a.timestamp >= cutoff_time]
        
        stats = {
            'total_alerts': len(recent_alerts),
            'active_alerts': len(self.active_alerts),
            'by_severity': {},
            'by_component': {},
            'response_success_rate': 0.0,
            'mean_time_to_acknowledge': 0.0,
            'mean_time_to_resolve': 0.0
        }
        
        # Count by severity
        for severity in AlertSeverity:
            stats['by_severity'][severity.value] = sum(
                1 for a in recent_alerts if a.severity == severity
            )
        
        # Count by component
        components = set(a.component for a in recent_alerts)
        for component in components:
            stats['by_component'][component] = sum(
                1 for a in recent_alerts if a.component == component
            )
        
        # Calculate response success rate
        recent_responses = [r for r in self.automated_responder.response_history 
                          if r.timestamp >= cutoff_time]
        if recent_responses:
            stats['response_success_rate'] = sum(r.success for r in recent_responses) / len(recent_responses)
        
        return stats

# Example alert creation function
def create_alert(
    component: str,
    metric: str,
    message: str,
    current_value: float,
    threshold_value: float,
    severity: AlertSeverity = AlertSeverity.WARNING
) -> Alert:
    """Create a new alert"""
    return Alert(
        alert_id=f"alert_{component}_{metric}_{int(datetime.now().timestamp())}",
        timestamp=datetime.now(),
        severity=severity,
        component=component,
        metric=metric,
        message=message,
        current_value=current_value,
        threshold_value=threshold_value
    )

# CLI Interface
async def main():
    """CLI interface for alerting system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='L9 Alerting System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Test alert command
    test_parser = subparsers.add_parser('test', help='Send test alert')
    test_parser.add_argument('--severity', choices=['info', 'warning', 'critical', 'emergency'], default='warning')
    test_parser.add_argument('--component', default='test_component')
    test_parser.add_argument('--metric', default='test_metric')
    test_parser.add_argument('--message', default='Test alert message')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show alert statistics')
    stats_parser.add_argument('--hours', type=int, default=24, help='Time period in hours')
    
    # Active alerts command
    active_parser = subparsers.add_parser('active', help='Show active alerts')
    active_parser.add_argument('--severity', choices=['info', 'warning', 'critical', 'emergency'])
    
    args = parser.parse_args()
    
    # Initialize alerting system
    alerting_system = AlertingSystem()
    
    if args.command == 'test':
        # Create and process test alert
        alert = create_alert(
            component=args.component,
            metric=args.metric,
            message=args.message,
            current_value=100.0,
            threshold_value=80.0,
            severity=AlertSeverity(args.severity)
        )
        
        result = await alerting_system.process_alert(alert)
        print(f"Alert processed: {json.dumps(result, indent=2)}")
        
    elif args.command == 'stats':
        stats = alerting_system.get_alert_statistics(hours=args.hours)
        print(f"Alert Statistics (last {args.hours} hours):")
        print(json.dumps(stats, indent=2))
        
    elif args.command == 'active':
        severity = AlertSeverity(args.severity) if args.severity else None
        active_alerts = alerting_system.get_active_alerts(severity)
        
        print(f"Active Alerts: {len(active_alerts)}")
        for alert in active_alerts:
            print(f"  - [{alert.severity.value.upper()}] {alert.component}: {alert.message}")
            print(f"    ID: {alert.alert_id}")
            print(f"    Time: {alert.timestamp.isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
