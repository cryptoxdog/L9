# Emma Agent Module — Production Deployment Guide

## Module Overview

**Emma** is a production-grade L9 Secure AI OS agent module with:

- **Unified Memory Backend**: Redis (working), PostgreSQL (episodic), Neo4j (semantic)
- **Governed Execution**: Autonomy gates, escalation workflows, compliance audit
- **Multi-Channel Integration**: Slack, Twilio, WhatsApp Business API
- **Enterprise Infrastructure**: Connection pooling, circuit breakers, health checks
- **Observability**: Prometheus metrics, structured JSON logging, correlation IDs
- **Quality Assurance**: 80%+ test coverage, MyPy strict, zero circular dependencies

## Architecture

```
EmmaController (Core Orchestration)
├── MemoryManager (Redis + PostgreSQL + Neo4j)
├── GovernanceHandler (Policy enforcement)
├── EscalationManager (Approval workflows)
├── DatabasePool (Postgres connection pooling)
├── CacheManager (Redis client)
├── MetricsCollector (Prometheus)
└── HealthChecker (Health status)

API Layer (FastAPI)
├── agent_routes.py (Task execution)
├── memory_routes.py (Memory operations)
└── os_routes.py (System status)

Webhook Handlers
├── slack.py (Slack integration)
├── twilio.py (Voice/SMS)
└── waba.py (WhatsApp Business)
```

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ with pgvector extension
- Redis 6.0+
- Neo4j 4.4+
- Docker & Docker Compose

### Setup

```bash
# Clone repository
git clone <repo_url>
cd emma_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Run migrations
python -m alembic upgrade head

# Run tests
pytest tests/ -v --cov=emma_agent --cov-report=term-missing
```

## Configuration

All configuration via environment variables:

```bash
# Database
POSTGRES_URL=postgresql://user:pass@localhost/emma
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20

REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=20

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Governance
AUTONOMY_LEVEL=semi_autonomous  # restricted, supervised, semi_autonomous, autonomous
ESCALATION_RECIPIENT=igor@company.com  # Compliance officer

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Observability
LOG_LEVEL=INFO
METRICS_PORT=9000
CORRELATION_ID_HEADER=X-Correlation-ID

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...

# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...

# WhatsApp Business API
WABA_PHONE_ID=...
WABA_ACCESS_TOKEN=...
```

## Running the Agent

### Local Development

```bash
# Start containers
docker-compose up -d

# Run agent
python -m emma_agent.server

# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:9000/metrics
```

### Production Deployment

#### Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

#### Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Systemd

```bash
sudo cp emma_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable emma_agent
sudo systemctl start emma_agent
sudo systemctl status emma_agent
```

## API Reference

### Health Check

```
GET /health
```

Returns system status and subsystem health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "memory": "ok",
    "governance": "ok",
    "escalation": "ok"
  }
}
```

### Submit Task

```
POST /api/tasks
Authorization: Bearer <JWT>

{
  "task_type": "research",
  "description": "Analyze market trends",
  "parameters": {"domain": "finance"},
  "priority": 7,
  "estimated_cost": 50.0
}
```

**Response:**
```json
{
  "task_id": "task_abc123",
  "status": "accepted",
  "correlation_id": "corr_xyz789"
}
```

### Get Task Status

```
GET /api/tasks/{task_id}
Authorization: Bearer <JWT>
```

### Memory Operations

```
POST /api/memory/store
{
  "content": "...",
  "source": "slack",
  "metadata": {}
}

GET /api/memory/search?query=...&limit=10

POST /api/memory/embeddings
{
  "content": "...",
  "embedding": [...]
}
```

## Webhook Integration

### Slack

Set webhook URL in Slack app settings:
```
https://your-domain.com/webhooks/slack/events
```

Slash command:
```
/emma <task_description>
```

### Twilio

```
POST https://your-domain.com/webhooks/twilio/sms
```

### WhatsApp Business API

```
POST https://your-domain.com/webhooks/waba/messages
```

## Monitoring & Observability

### Prometheus Metrics

```
# Task metrics
emma_tasks_submitted{type="research"} 42
emma_task_duration_seconds_bucket{type="research", le=1.0} 10
emma_task_duration_seconds_sum{type="research"} 150.5
emma_task_duration_seconds_count{type="research"} 42

# Memory metrics
emma_memory_store_duration_seconds_bucket{operation="write", le=0.1} 80
emma_memory_query_duration_seconds_bucket{operation="search", le=0.5} 150

# Database metrics
emma_db_connections_active 8
emma_db_connection_pool_size 10
```

### Health Checks

```bash
# Service health
curl http://localhost:8000/health

# Kubernetes liveness
curl http://localhost:8000/health/live

# Kubernetes readiness
curl http://localhost:8000/health/ready
```

### Structured Logging

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "emma_agent.controller",
  "message": "Task completed",
  "task_id": "task_abc123",
  "correlation_id": "corr_xyz789",
  "duration_ms": 1234,
  "metadata": {}
}
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=emma_agent --cov-report=html

# Specific module
pytest tests/test_controller.py -v

# Unit tests only
pytest tests/ -k "not integration"

# Integration tests
pytest tests/ -k "integration"
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL
psql postgresql://user:pass@localhost/emma -c "SELECT 1"

# Check connection pool
curl http://localhost:8000/health | jq '.checks.database'

# Check logs
docker logs emma_agent_db
```

### Cache Issues

```bash
# Check Redis
redis-cli ping

# Check pool
curl http://localhost:8000/health | jq '.checks.cache'

# Flush cache (dev only)
redis-cli FLUSHDB
```

### Task Escalation

```bash
# List escalations
curl http://localhost:8000/api/escalations/active

# Approve escalation
curl -X POST http://localhost:8000/api/escalations/{id}/approve \
  -H "Authorization: Bearer <JWT>" \
  -d '{"reason": "Approved by compliance"}'

# Reject escalation
curl -X POST http://localhost:8000/api/escalations/{id}/reject \
  -H "Authorization: Bearer <JWT>" \
  -d '{"reason": "Does not meet criteria"}'
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple instances with load balancer
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# Or use Kubernetes HPA
kubectl autoscale deployment emma-agent --min=2 --max=10 --cpu-percent=80
```

### Database Scaling

- **PostgreSQL**: Use read replicas for scaling queries
- **Redis**: Use Redis Cluster for distributed caching
- **Neo4j**: Use Neo4j Enterprise clustering

## Security

### Authentication

All API endpoints require Bearer token (JWT):

```bash
curl -H "Authorization: Bearer <JWT>" http://localhost:8000/api/tasks
```

Generate tokens via:
```python
from emma_agent.security import generate_token
token = generate_token(user_id="user123", expires_in=3600)
```

### TLS/SSL

Configure in production:
```nginx
upstream emma_agent {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.3 TLSv1.2;
    
    location / {
        proxy_pass http://emma_agent;
    }
}
```

### Environment Secrets

Use `.env` file (NEVER in git):
```bash
cp .env.example .env
# Edit .env with real values
chmod 600 .env
```

In production, use secret management (Vault, AWS Secrets Manager, etc.):
```python
from emma_agent.config import load_secrets
secrets = load_secrets()  # Loads from Vault or environment
```

## Support & Maintenance

### Regular Maintenance

```bash
# Weekly: Run migrations
python -m alembic upgrade head

# Weekly: Prune old logs
python -m emma_agent.maintenance cleanup-logs --days=30

# Monthly: Vacuum PostgreSQL
psql postgresql://... -c "VACUUM ANALYZE"

# Monthly: Rebuild Neo4j indexes
# Use Neo4j admin tools
```

### Version Upgrades

```bash
# Check current version
curl http://localhost:8000/version

# Backup before upgrade
python -m emma_agent.maintenance backup-database

# Upgrade
pip install --upgrade emma_agent

# Run migrations
python -m alembic upgrade head

# Verify health
curl http://localhost:8000/health
```

## Contact & Support

- **Issues**: https://github.com/l9/emma_agent/issues
- **Email**: emma-support@l9.ai
- **Slack**: #emma-agent-support
