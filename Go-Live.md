# L9 Go-Live Checklist

> **Target:** VPS Production Node  
> **Script:** `ops/vps_release_gate.sh`

---

## Pre-Flight (Local)

Run locally before deploying:

```bash
cd /Users/ib-mac/Projects/L9
venv/bin/python -m compileall -q -x "venv|__pycache__|\.git" .
venv/bin/python tests/smoke_test_root.py
venv/bin/python tests/smoke_email.py
git push origin main
```

---

## VPS Deployment

### 1. SSH into VPS

```bash
ssh your-vps-alias
```

### 2. Run Release Gate

```bash
cd /opt/l9
sudo bash ops/vps_release_gate.sh
```

### 3. Expected Output

```
═══════════════════════════════════════════════════════════════════════════
  RELEASE GATE VERDICT
═══════════════════════════════════════════════════════════════════════════

  PASSED: 14
  FAILED: 0
  COMMIT: abc1234

  RELEASE_STATUS: PASS
  BLOCKERS: NONE
  SAFE_TO_PROCEED: YES

═══════════════════════════════════════════════════════════════════════════
```

---

## Manual Verification

After script passes, verify manually:

```bash
# Health check
curl -sS http://127.0.0.1:8000/health | jq .

# OpenAPI routes
curl -sS http://127.0.0.1:8000/openapi.json | jq '.paths | keys'

# Service status
systemctl status l9 --no-pager
systemctl status l9-agent --no-pager

# Recent logs
journalctl -u l9 -n 50 --no-pager
```

---

## Reboot Survival Test

```bash
# Reboot
sudo reboot

# After reconnect (wait ~60s)
ssh your-vps-alias
systemctl is-active l9 l9-agent
curl -sS http://127.0.0.1:8000/health
```

**Expected:** Both services `active`, health returns `healthy`.

---

## Rollback

If deployment fails:

```bash
cd /opt/l9
git checkout HEAD~1
sudo systemctl restart l9 l9-agent
curl -sS http://127.0.0.1:8000/health
```

---

## Gate Summary

| Gate | Description |
|------|-------------|
| 1 | `git pull --ff-only` |
| 2 | venv activation + Python version |
| 3 | `pip install -e .` + `pip check` |
| 4 | `compileall` (scoped) |
| 5 | `smoke_test_root.py` + `smoke_email.py` |
| 6 | `systemctl restart l9 l9-agent` |
| 7 | Service health + import error scan |
| 8 | `/health` + `/openapi.json` verification |
| 9 | Journal tail (info) |

---

*Last updated: 2024-12-14*
