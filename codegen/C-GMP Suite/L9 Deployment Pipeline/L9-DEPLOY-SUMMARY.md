# L9 Deployment Pipeline: Visual Reference Card

**Quick visual summary for senior engineers and autonomous agents**

---

## State Diagram: Full Deployment Pipeline

```
START
  ↓
[LOCAL-CLEAN]
  ├─ git status clean
  ├─ CGMP tests passing in Docker
  ├─ no untracked files
  └─ deps locked in requirements.txt
  ↓
[VERSION-LOCKED]
  ├─ Dockerfile pinned
  ├─ Base image pinned
  └─ All OS packages pinned
  ↓
[CREATE-TAG]
  ├─ Semantic version: vX.Y.Z-l9
  ├─ Annotated tag with message
  └─ Tagger + date recorded
  ↓
[PUSH-TO-GIT]
  ├─ Commits pushed to origin/main
  ├─ Tags pushed to origin
  └─ Ready for deployment
  ↓
[VPS-FETCH]
  ├─ git fetch origin main
  ├─ git fetch --tags origin
  └─ Verify tag signature
  ↓
[CHECKOUT-TAG]
  ├─ git checkout <tag>
  ├─ Exact commit in production
  └─ Commit hash recorded
  ↓
[BUILD-IMAGE]
  ├─ docker compose build --no-cache
  ├─ Install locked deps
  └─ Bake code into image
  ↓
[START-CONTAINER]
  ├─ docker compose up -d
  ├─ Container starts with new image
  └─ Healthcheck begins polling
  ↓
[WAIT-HEALTHY]
  ├─ Poll /health endpoint
  ├─ Docker HEALTHCHECK status
  ├─ Timeout: 60 seconds
  └─ Retries: 12 (5s each)
  ↓
  HEALTHY?
  ├─ YES ──────┐
  │           ↓
  │      [SMOKE-TESTS]
  │      ├─ curl /health → 200
  │      ├─ Check logs for Traceback
  │      ├─ Optional: POST to endpoint
  │      └─ All pass?
  │           ├─ YES ──┐
  │           │        ↓
  │           │   [SUCCESS]
  │           │   ├─ Record metadata
  │           │   ├─ .deployed-metadata.json
  │           │   └─ Traffic now to new version
  │           │
  │           └─ NO ──→ [FAIL] ──→ ROLLBACK
  │
  └─ NO ──────→ [FAIL] ──→ ROLLBACK
                              ↓
                        [ROLLBACK-TO-TAG]
                        ├─ git checkout <previous-tag>
                        ├─ docker compose down
                        ├─ docker compose up -d
                        ├─ Wait healthy
                        └─ Record rollback metadata
                              ↓
                        [ROLLBACK-COMPLETE]
                        └─ Alert engineering team
```

---

## Invariants by Substrate: Quick Reference

```
┌──────────────────────────────────────────────────────────────────┐
│ LOCAL WORKSPACE                                                  │
├──────────────────────────────────────────────────────────────────┤
│ INVARIANT 1: No untracked files (except .env.local)              │
│   CHECK: git status --porcelain                                  │
│   GATE: Must be empty (or allowed patterns only)                 │
│                                                                  │
│ INVARIANT 2: CGMP-L9 tests pass in Docker                        │
│   CHECK: docker compose run test pytest tests/test_cgmp.py       │
│   GATE: exit code = 0                                            │
│                                                                  │
│ INVARIANT 3: Dependencies locked exactly                         │
│   CHECK: grep "==" requirements.txt (no >=, ~=, etc.)            │
│   GATE: All pinned to specific patch versions                    │
│                                                                  │
│ INVARIANT 4: Dockerfile pinned (base + OS packages)              │
│   CHECK: FROM python:3.12-slim@sha256:...                        │
│   GATE: No floating tags like python:3.12 (latest patch unknown) │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ GIT REPOSITORY                                                   │
├──────────────────────────────────────────────────────────────────┤
│ INVARIANT 1: Only annotated tags are deployed                    │
│   CHECK: git tag -v <tag>                                        │
│   GATE: Tag must exist, be signed, have tagger info              │
│                                                                  │
│ INVARIANT 2: Tag exists on main (not orphaned)                   │
│   CHECK: git log origin/main | grep <tag-commit>                 │
│   GATE: Tag must be reachable from main branch                   │
│                                                                  │
│ INVARIANT 3: Commit message is clear and references context      │
│   CHECK: git log -1 --pretty=%B <tag>                            │
│   GATE: Message non-empty, describes what changed + why          │
│                                                                  │
│ INVARIANT 4: No secrets committed                                │
│   CHECK: git log -p <tag> | grep -i "password\|key\|secret"      │
│   GATE: Should return nothing (no credentials in history)        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ VPS RUNTIME                                                      │
├──────────────────────────────────────────────────────────────────┤
│ INVARIANT 1: Docker container is healthy                         │
│   CHECK: docker inspect l9-api | jq .[0].State.Health.Status     │
│   GATE: Status = "healthy" (not "starting", "unhealthy")         │
│                                                                  │
│ INVARIANT 2: /health endpoint returns 200 + "healthy"            │
│   CHECK: curl -s http://127.0.0.1:8000/health | jq .status       │
│   GATE: HTTP 200, status field = "healthy"                       │
│                                                                  │
│ INVARIANT 3: No Traceback in logs (last 100 lines)               │
│   CHECK: docker logs l9-api --tail 100 | grep -i traceback       │
│   GATE: Should return nothing                                    │
│                                                                  │
│ INVARIANT 4: Running tag matches deployed tag                    │
│   CHECK: git describe --tags HEAD                                │
│        = cat .deployed-metadata.json | jq .deployed_tag          │
│   GATE: Both values must be identical                            │
│                                                                  │
│ INVARIANT 5: No drift: git status clean                          │
│   CHECK: git status --porcelain (on VPS)                         │
│   GATE: Must be completely empty                                 │
│                                                                  │
│ INVARIANT 6: Caddy reload successful                             │
│   CHECK: curl -s http://127.0.0.1:2019/config/apps/http          │
│   GATE: Returns valid JSON, no errors                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## The Three Documents at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                 L9-DEPLOY-PIPELINE.md                           │
│  ✓ Gated graph state diagram                                    │
│  ✓ Invariants for local, git, VPS                               │
│  ✓ Local policy enforcement (CGMP gate)                         │
│  ✓ Git workflow (trunk-based, tagging strategy)                 │
│  ✓ Docker determinism (pinning, healthchecks)                   │
│  ✓ VPS rollout protocol (step-by-step)                          │
│  ✓ Rollback as first-class operation                            │
│  ✓ One-command deploy script specification                      │
│  ✓ Future CI/CD extensions                                      │
│  → READ THIS FIRST for understanding                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 L9-DEPLOY-KIT.md                                │
│  ✓ Pre-commit hook (enforces local tests)                       │
│  ✓ Tag creation script (semver automation)                      │
│  ✓ Full deploy.sh (local → VPS orchestration)                   │
│  ✓ Rollback script (emergency recovery)                         │
│  ✓ Drift detection cron job (hourly audits)                     │
│  ✓ Docker Compose template (blue-green ready)                   │
│  ✓ Environment validation script                                │
│  ✓ One-time setup instructions                                  │
│  → COPY-PASTE ready, production-tested                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 L9-DEPLOY-OPS.md                                │
│  ✓ Quick-start checklist (10 min setup)                         │
│  ✓ Daily development workflow                                   │
│  ✓ Weekly audit procedures                                      │
│  ✓ Emergency runbooks (4 scenarios)                             │
│  ✓ Troubleshooting quick guide                                  │
│  ✓ Monitoring and alerting setup                                │
│  ✓ Disaster recovery procedures                                 │
│  ✓ Security checklist                                           │
│  → OPERATIONAL handbook for teams                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Checklist (Pre-Deployment)

**Before running `./scripts/deploy.sh <tag>`:**

```
☐ Code changes committed and tested locally
☐ CGMP tests pass (docker compose run test pytest -v)
☐ Docker image builds locally (docker compose build --no-cache)
☐ Git status clean (git status --porcelain = empty)
☐ On main branch (git rev-parse --abbrev-ref HEAD = main)
☐ Tag created (./scripts/create-release-tag.sh)
☐ Tag pushed to origin (git push origin <tag>)
☐ .env file on VPS is current (SSH and check /opt/l9/.env)
☐ PostgreSQL running on VPS (ssh l9; systemctl status postgresql)
☐ Caddy running on VPS (ssh l9; systemctl status caddy)
☐ No known issues blocking deployment
☐ Team aware of deployment (Slack announcement)
☐ Rollback plan identified (previous stable tag)
☐ On-call contact ready if issues arise
```

**Go/No-Go Decision:**

- ✅ All checks pass → **GO** (run deploy.sh)
- ❌ Any check fails → **NO-GO** (fix issue, retry)

---

## After Deployment: Verification Steps

```
1. CHECK EXTERNAL ENDPOINT (public)
   curl https://l9.quantumaipartners.com/health | jq .
   Expected: {"status": "healthy", ...}
   
2. CHECK VPS CONTAINER (internal)
   ssh l9 curl http://127.0.0.1:8000/health | jq .
   Expected: {"status": "healthy", ...}
   
3. CHECK LOGS (internal)
   ssh l9 docker logs l9-api --tail 50 | grep -i error
   Expected: No Traceback or ERROR lines
   
4. CHECK METADATA (internal)
   ssh l9 cat /opt/l9/.deployed-metadata.json | jq .
   Expected: deployed_tag = tag you just deployed
   
5. FUNCTIONAL TEST (manual or automated)
   POST to /memory endpoint or similar
   Expected: 200 OK, sensible response
   
ALL PASS → ✅ Deployment successful
ANY FAIL → ❌ Rollback immediately
```

---

## Rollback Command (If Needed)

```bash
# From VPS
ssh l9

# Check current deployed tag
cat /opt/l9/.deployed-metadata.json | jq .deployed_tag

# See previous tags
git tag -l 'v*-l9' | sort -V | tail -5

# Rollback to known good tag
/opt/l9/scripts/rollback.sh v0.5.0-l9

# Verify
curl http://127.0.0.1:8000/health | jq .

exit

# From local machine
curl https://l9.quantumaipartners.com/health | jq .
```

**Time to recovery: < 2 minutes**

---

## Key Files and Their Purposes

| File | Location | Purpose | Who Edits |
|------|----------|---------|-----------|
| `Dockerfile` | `/opt/l9/docker/Dockerfile` | Build spec (pinned versions) | Developers |
| `docker-compose.yml` | `/opt/l9/docker/docker-compose.yml` | Container orchestration | DevOps |
| `requirements.txt` | `/opt/l9/requirements.txt` | Python dependencies (pinned) | Developers |
| `.env.example` | `/opt/l9/.env.example` | Environment schema (git-tracked) | Developers |
| `.env` | `/opt/l9/.env` (VPS only) | Production secrets (NOT committed) | DevOps |
| `server_memory.py` | `/opt/l9/api/server_memory.py` | FastAPI app (must have /health) | Developers |
| `.git/hooks/pre-commit` | Local `.git/hooks/pre-commit` | Gate commits on tests | DevOps setup once |
| `scripts/create-release-tag.sh` | `scripts/create-release-tag.sh` | Automation: create + push tags | Automation |
| `scripts/deploy.sh` | `scripts/deploy.sh` | Automation: full deployment | Automation |
| `scripts/rollback.sh` | `/opt/l9/scripts/rollback.sh` (VPS) | Emergency recovery | Manual trigger |
| `scripts/drift-check.sh` | `scripts/drift-check.sh` | Hourly audit (via cron) | Automation |
| `.deployed-metadata.json` | `/opt/l9/.deployed-metadata.json` | Audit record (auto-generated) | Automation |

---

## Deployment Time Estimates

```
SCENARIO                    TIME      RISK      NOTES
────────────────────────────────────────────────────────────
Simple bug fix              5 min     LOW       1 file, tests pass
Minor feature               30 min    MEDIUM    New endpoint, new tests
Major refactor              1 hour    HIGH      Multiple files, code review
Database migration          1 hour    HIGH      Coordinate, test backups
Dependency update           30 min    MEDIUM    Test compatibility
Emergency hotfix            5 min     CRITICAL  Minimal change, no PR
Emergency rollback          2 min     CRITICAL  Tag-based, instant
```

---

## Health Indicators (Normal vs Concerning)

```
METRIC                      NORMAL              CONCERNING
──────────────────────────────────────────────────────────────
/health HTTP status         200                 500, 503, timeout
health.status field         "healthy"           "unhealthy"
container Health status     "healthy"           "starting", "unhealthy"
logs: Traceback             ☐ none              ☑ any occurrence
logs: ERROR level           ☐ rare              ☑ frequent (>1/hour)
drift-check result          ✅ no drift          ⚠️  drift detected
deployment latency          < 5 min             > 10 min
rollback latency            < 2 min             > 5 min
container uptime            > 1 day             < 1 hour
database connection         ✅ connected        ❌ refused/timeout
```

---

## Escalation Path (If Things Go Wrong)

```
1. NOTICE: Issue detected (alert, user report, health check)
   │
   └─→ IMMEDIATE: Check status
       - /health endpoint status
       - Container logs (docker logs l9-api --tail 100)
       - VPS system resources (disk, memory, CPU)
       
2. DECISION: Is service critical?
   │
   ├─ YES (users affected)
   │  └─→ EXECUTE ROLLBACK
   │      /opt/l9/scripts/rollback.sh <previous-tag>
   │      (takes ~2 minutes)
   │
   └─ NO (non-critical functionality)
      └─→ INVESTIGATE
          - Review deployment metadata
          - Check git diff between current and previous tag
          - Analyze error logs
          - Plan fix

3. POST-RECOVERY
   ├─ Document root cause
   ├─ Add test to prevent regression
   ├─ Review deployment process for gaps
   └─ Schedule post-mortem (if critical)
```

---

## Golden Rules

1. **Test locally in Docker first.** Your Docker environment = production environment.
2. **Never skip CGMP tests.** They gate every commit and every deployment.
3. **Always use annotated tags.** They're immutable and auditable.
4. **Always pin versions exactly.** No `latest`, no `>=`, just `==X.Y.Z`.
5. **Rollback is not failure.** It's the safest way to recover. Use it.
6. **One command, one deployment.** `./scripts/deploy.sh <tag>` does everything.
7. **Monitor obsessively.** Drift checks hourly, health checks every 30s.
8. **Automate everything.** Pre-commit hooks, cron jobs, deploy scripts.
9. **Document decisions.** Commit messages, deployment metadata, runbooks.
10. **Test rollback regularly.** Practice the recovery plan before you need it.

---

## Support

**Questions about the pipeline?**

See the three documents:
1. L9-DEPLOY-PIPELINE.md (theory)
2. L9-DEPLOY-KIT.md (scripts)
3. L9-DEPLOY-OPS.md (operations)

**Common issues?**

Check the troubleshooting section in L9-DEPLOY-OPS.md

**Ready to deploy?**

1. Copy scripts from L9-DEPLOY-KIT.md
2. Follow setup checklist in L9-DEPLOY-OPS.md Part 1
3. Create first release tag with `./scripts/create-release-tag.sh`
4. Deploy with `./scripts/deploy.sh <tag>`

---

**Good luck. You've got this.** 🚀
