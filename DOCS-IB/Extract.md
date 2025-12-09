Understood, Boss.
Here is the **full “Make Deployments Boring” package** — everything you asked for:

* **docker-compose.yml** (production-grade, resource-capped, health-checked)
* **systemd service** (auto-restart, logs, PID mgmt)
* **Caddyfile** (WS + HTTPS + auto-TLS + health endpoints)
* **One-command deploy scripts**
* **Swap + resource-cap enforcement**
* **Boring, deterministic, repeatable**

This is optimized for your **Hetzner CX23** target (2 vCPU / 4GB RAM).

---

# ✅ 1. **docker-compose.yml (Production)**

This is the full L9 stack, WS-ready, resource-capped, restart-safe.

```yaml
version: "3.9"

services:

  api:
    build: .
    container_name: l9_api
    restart: always
    environment:
      - L9_ENV=production
      - L9_WS_URL=wss://l9.quantumaipartners.com/ws/agent
      - PYTHONUNBUFFERED=1
    ports:
      - "8000:8000"
    command: uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 1
    healthcheck:
      test: ["CMD-SHELL", "curl -fs http://localhost:8000/health || exit 1"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: "1.5"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M

  qdrant:
    image: qdrant/qdrant:v1.12.3
    container_name: l9_qdrant
    restart: always
    volumes:
      - ./data/qdrant:/qdrant/storage
    ports:
      - "6333:6333"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G

  postgres:
    image: postgres:16
    container_name: l9_postgres
    restart: always
    environment:
      POSTGRES_DB: l9
      POSTGRES_USER: l9
      POSTGRES_PASSWORD: l9_password
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U l9 -d l9"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G

  redis:
    image: redis:7
    container_name: l9_redis
    restart: always
    command: ["redis-server", "--save", "", "--appendonly", "no"]
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          memory: 256M

networks:
  default:
    driver: bridge
```

---

# ✅ 2. **Caddyfile (WS + TLS + Reverse Proxy)**

This enables WebSockets **correctly**.

```caddy
l9.quantumaipartners.com {
    encode zstd gzip

    reverse_proxy /ws/* api:8000 {
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }

    reverse_proxy api:8000

    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }

    handle_path /health {
        respond "ok" 200
    }
}
```

---

# ✅ 3. **systemd Unit File (api.service)**

Create:

`/etc/systemd/system/l9.service`

```ini
[Unit]
Description=L9 AI-OS API
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/l9
ExecStart=/usr/bin/docker compose -f docker-compose.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.yml down
TimeoutStartSec=30
TimeoutStopSec=30
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable + start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable l9
sudo systemctl start l9
```

---

# ✅ 4. **ONE-COMMAND DEPLOY (deploy.sh)**

Put in repo root:

```bash
#!/usr/bin/env bash
set -e

echo "[1/6] Pulling latest repo..."
git pull

echo "[2/6] Building containers..."
docker compose build --no-cache

echo "[3/6] Stopping old services..."
docker compose down

echo "[4/6] Starting new services..."
docker compose up -d

echo "[5/6] Checking health..."
sleep 5
curl -fs https://l9.quantumaipartners.com/health && echo "API healthy"

echo "[6/6] Done."
```

Make executable:

```bash
chmod +x deploy.sh
```

Now deployment is:

```bash
./deploy.sh
```

---

# ✅ 5. **ONE-COMMAND FULL SERVER INSTALL (bootstrap.sh)**

```bash
#!/usr/bin/env bash
set -e

apt update
apt install -y docker.io docker-compose-plugin ufw fail2ban

ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

systemctl enable docker
systemctl start docker

echo "Server bootstrap complete."
```

---

# ✅ 6. **Swap + Resource Caps (CX23-Safe)**

### Create swap:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo "/swapfile swap swap defaults 0 0" | sudo tee -a /etc/fstab
```

### Check swap is working:

```bash
free -h
```

### Enforce memory OOM limits:

Docker compose already has:

```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

This prevents **OOM kill syndrome**, which is common on CX23.

---

# 🔥 Deployment Summary

**After you add these files to the repo:**

```
./bootstrap.sh       # first time only
./deploy.sh          # every deploy
```

And Caddy + systemd make everything run automatically after reboot.

This makes deployments:

* **boring**
* **predictable**
* **repeatable**
* **ops-safe**
* **one-command**
* **no drama**

---

# If you want, I can now generate:

### **A) Folder structure update**

To place these files in the correct repo paths.

### **B) Cursor God Mode reorganizer**

To actually add these files into your repo automatically.

Just say:

**“Generate the Cursor deploy-integration prompt”**
