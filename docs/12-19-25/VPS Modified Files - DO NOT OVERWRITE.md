# VPS Modified Files - DO NOT OVERWRITE
# Last checked: 2025-12-16
# These files have VPS-specific config that must be preserved

## Critical Files (12 unique, exclude from sync)

| Last Modified | Path |
|---------------|------|
| 2025-12-16 03:03 | /opt/l9/api/webhook_slack.py |
| 2025-12-16 01:51 | /opt/l9/.env |
| 2025-12-16 00:34 | /opt/l9/docker/docker-compose.yml |
| 2025-12-16 00:18 | /opt/l9/docker/Dockerfile |
| 2025-12-16 00:10 | /opt/l9/api/db.py |
| 2025-12-16 00:07 | /opt/l9/requirements.txt |
| 2025-12-15 23:24 | /opt/l9/docker/.env |
| 2025-12-15 23:20 | /opt/l9/docker/requirements.txt |
| 2025-12-15 22:48 | /opt/l9/runtime/requirements.txt |
| 2025-12-15 22:36 | /opt/l9/runtime/Dockerfile |
| 2025-12-15 22:24 | /opt/l9/runtime/docker-compose.yml |
| 2025-12-15 22:19 | /opt/l9/runtime/entrypoint.sh |
| 2025-12-15 22:05 | /opt/l9/docker/Dockerfile.api |
| 2025-12-15 21:53 | /opt/l9/docker-compose.yml |
| 2025-12-15 14:34 | /opt/l9/api/webhook_mac_agent.py |
| 2025-12-15 14:19 | /opt/l9/api/config.py |

## Excluded (backups/junk)
- .env.backup.* (4 files)
- .env.before-slack-*
- .env.docker
- *.bak
- =0.24.0, =0.104.0 (pip install artifacts)