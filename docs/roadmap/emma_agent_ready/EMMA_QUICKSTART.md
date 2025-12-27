# Emma Agent — Quick Start Guide

## 🚀 5-Minute Setup

### 1. Clone & Setup Environment

```bash
git clone https://github.com/l9/emma_agent.git
cd emma_agent

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure (Docker Compose)

```bash
docker-compose up -d

# Verify services
docker-compose ps
```

### 4. Initialize Database

```bash
# Run migrations
python -m alembic upgrade head

# Verify PostgreSQL
psql postgresql://user:pass@localhost/emma -c "SELECT 1"
```

### 5. Run Tests

```bash
pytest tests/ -v --cov=emma_agent
```

### 6. Start Emma Agent

```bash
python -m emma_agent.server
# or
uvicorn emma_agent.api.app:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify Health

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:9000/metrics

# API docs
open http://localhost:8000/docs
```

---

## 📝 Submit Your First Task

```bash
# Via API
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "research",
    "description": "Analyze Q4 market trends",
    "parameters": {"domain": "finance"},
    "priority": 7,
    "estimated_cost": 50.0
  }'

# Response
{
  "task_id": "task_abc123",
  "status": "accepted",
  "correlation_id": "corr_xyz789"
}

# Check status
curl http://localhost:8000/api/tasks/task_abc123 \
  -H "Authorization: Bearer <your_token>"
```

---

## 💬 Slack Integration

1. **Create Slack App** at https://api.slack.com/apps
2. **Configure webhook URL**: `https://your-domain.com/webhooks/slack/events`
3. **Subscribe to events**: `app_mention`, `message.channels`
4. **Set environment variables**:
   ```bash
   export SLACK_BOT_TOKEN="xoxb-..."
   export SLACK_SIGNING_SECRET="..."
   ```
5. **Use in Slack**:
   ```
   /emma Analyze Q4 market trends
   @emma What should we prioritize?
   ```

---

## 📊 Monitor with Prometheus

```bash
# Add to prometheus.yml
scrape_configs:
  - job_name: 'emma'
    static_configs:
      - targets: ['localhost:9000']

# View metrics
curl http://localhost:9000/metrics
```

---

## 🔐 Generate JWT Token

```python
from emma_agent.security import generate_token

token = generate_token(
    user_id="user@company.com",
    expires_in=3600,  # 1 hour
)
print(f"Bearer {token}")
```

---

## 🛑 Troubleshooting

### Database Connection Refused

```bash
docker-compose logs postgres

# Check PostgreSQL
docker-compose exec postgres psql -U emma -d emma -c "SELECT 1"
```

### Health Check Failing

```bash
curl http://localhost:8000/health -v

# Check logs
docker-compose logs emma_agent
```

### Tests Failing

```bash
# Run specific test
pytest tests/test_controller.py -v

# With verbose logging
pytest tests/ -v --log-cli-level=DEBUG

# Check environment
echo $POSTGRES_URL
echo $REDIS_URL
```

---

## 📚 Full Documentation

- **README.md** - Module overview
- **CONFIG.md** - Configuration reference
- **DEPLOYMENT.md** - Production deployment
- **IMPLEMENTATION_SUMMARY.md** - Architecture
- **SOURCE_CODE_INDEX.md** - Code examples
- **manifest.json** - Module specification

---

## 🎯 Next Steps

1. ✅ Local setup complete
2. 📝 Submit first task
3. 💬 Configure Slack integration
4. 📊 Set up monitoring (Prometheus + Grafana)
5. 🚀 Deploy to production

---

## 📞 Support

- **Slack**: #emma-agent-support
- **Email**: emma-team@l9.ai
- **GitHub Issues**: https://github.com/l9/emma_agent/issues
- **Docs**: https://docs.emma.l9.ai

---

**Ready to go!** 🚀
