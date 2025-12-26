# 🔬 L9 VPS MRI Analysis

## 🧩 BLOCK 1: Objective
**Task:** Identify why L9 API is down on VPS and determine root cause blockers
**Success:** Port 8000 responding, Slack webhooks working, health checks passing

---

## 🌐 BLOCK 2: Context Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Caddy** | ✅ Running | Active for 6 days, proxying to 127.0.0.1:8000 |
| **PostgreSQL** | ✅ Running | Port 5432 listening, `l9_memory` database exists |
| **Docker Daemon** | ✅ Running | v29.1.1 active |
| **l9-api Container** | ❌ EXITED | Exit code 128, stopped 9+ mins ago |
| **Port 8000** | ❌ NOT LISTENING | No process bound |
| **systemd l9.service** | ⚪ Disabled | Dead (correctly disabled) |
| **Redis** | ❌ Not deployed | Port 6379 not listening |
| **Neo4j** | ❌ Not deployed | Port 7687 not listening |

---

## 🔬 BLOCK 3: Decomposition - The Blockers

### ❌ BLOCKER 1: Docker Container Stopped (IMMEDIATE CAUSE)
```
l9-api    Exited (128) 9 minutes ago
```
- **Exit code 128** = Container was killed/stopped (not a crash)
- Last logs show clean shutdown, not an error
- The container WAS working (health checks passing before shutdown)

### ❌ BLOCKER 2: Configuration Mismatch (ROOT CAUSE)
**VPS docker-compose.yml:**
```yaml
dockerfile: docker/Dockerfile  # ← VPS path
```

**Repo docker-compose.yml:**
```yaml
dockerfile: runtime/Dockerfile  # ← Repo path
```

The VPS never received the updated `docker-compose.yml` from the repo - it's using an old local version.

### ❌ BLOCKER 3: Entrypoint Divergence
**VPS Dockerfile (`docker/Dockerfile`):**
```dockerfile
CMD ["bash","-lc","uvicorn api.server_memory:app --host 0.0.0.0 --port 8000"]
```

**Repo Dockerfile (`runtime/Dockerfile`):**
```dockerfile
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

The VPS uses `api.server_memory:app`, repo uses `api.server:app`.

---

## 🧠 BLOCK 5: Strategy - Abductive Analysis (Why Did This Happen?)

### Hypothesis Chain:

1. **We attempted to sync repo → VPS** via `git pull`
2. **Docker build failed** due to corrupted overlay filesystem
3. **Cleanup commands were run** (`docker system prune -af`, etc.)
4. **The existing container was killed** during cleanup (exit 128)
5. **Container was never restarted** after cleanup
6. **The OLD docker-compose.yml remains** because:
   - It was in `.gitignore` at some point
   - Even after removing from `.gitignore`, the VPS has a local modified version
   - `git pull` doesn't overwrite untracked/modified local files

### Confidence: 0.92
Evidence:
- Exit code 128 = external kill, not app crash
- Container logs show clean health checks before shutdown
- VPS docker-compose.yml differs from repo version

---

## ⚙️ BLOCK 6: Execution - Two Recovery Paths

### 🅰️ PATH A: Quick Recovery (Restart Existing)
**Goal:** Get running FAST with existing VPS config

```bash
docker start l9-api
```

**Pros:** Immediate (seconds), uses known-working config  
**Cons:** Uses old `api.server_memory:app`, not repo-aligned

---

### 🅱️ PATH B: Full Sync (Repo-Aligned)
**Goal:** Fully align VPS with repo

**Step 1 - Force sync docker-compose.yml:**
```bash
# Backup VPS version
cp docker-compose.yml docker-compose.yml.vps-backup

# Force checkout from git (overwrites local)
git checkout HEAD -- docker-compose.yml
```

**Step 2 - Check if `runtime/Dockerfile` exists:**
```bash
ls -la runtime/Dockerfile
```

**Step 3 - Rebuild and start:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

**Step 4 - Verify:**
```bash
docker ps
curl http://127.0.0.1:8000/health
```

---

## 🧵 BLOCK 7: Synthesis - Strategic Position

### The Fundamental Issue:
> **VPS has a "forked" configuration** that diverged from the repo.
> The cleanup killed the container, but no rebuild was successful because Docker's overlay filesystem was corrupted.

### Immediate Fix (< 1 minute):
```bash
docker start l9-api
```
This restarts the existing (old) container. Slack will work again.

### Proper Fix (5-10 minutes):
1. Force-sync `docker-compose.yml` from repo
2. Verify `runtime/Dockerfile` exists on VPS
3. Rebuild container with new config
4. Restart

### What's Blocking the Rebuild?
The overlay filesystem error from earlier:
```
failed to solve: ... overlay ... no such file or directory
```

Need to confirm this is resolved. Run:
```bash
docker info | grep -i storage
docker info | grep -i overlay
```

If still broken, the nuclear option:
```bash
sudo systemctl stop docker containerd
sudo rm -rf /var/lib/docker
sudo systemctl start docker
```
⚠️ This deletes ALL Docker data (images, volumes, containers).

---

## 📊 Confidence Assessment

| Analysis | Score | Notes |
|----------|-------|-------|
| Container stopped (not crashed) | 0.95 | Exit 128 + clean logs |
| Config mismatch is root cause | 0.88 | VPS vs repo diff confirmed |
| Quick restart will work | 0.90 | Container was healthy before |
| Full rebuild needs overlay fix | 0.85 | Uncertain if cleanup resolved it |
| **Overall Confidence** | **0.89** | High |

---

## ✅ Recommended Next Action

**Fastest path to working Slack:**
```bash
docker start l9-api && sleep 5 && curl http://127.0.0.1:8000/health
```

**Expected output:**
```json
{"status": "healthy", "service": "L9 Phase 2 Memory System", ...}
```

Once confirmed working, you can plan a proper VPS ↔ Repo sync during a maintenance window.
