# Show the CORRECT Dockerfile content (the one with server_memory)
cat /opt/l9/docker/Dockerfile

# Check docker-compose.yml to see which Dockerfile it references
cat /opt/l9/docker-compose.yml | grep -i dockerfile

# Check container status
sudo docker ps -a | grep l9

# View container logs
sudo docker logs l9-api --tail 100

# Restart container
cd /opt/l9/docker && sudo docker-compose down && sudo docker-compose up -d --build

# Check PostgreSQL
sudo systemctl status postgresql
sudo ss -tlnp | grep 5432

# Check Caddy
sudo systemctl status caddy
sudo cat /etc/caddy/Caddyfile

# Test API locally on VPS
curl http://127.0.0.1:8000/health

# Test API via domain
curl https://l9.quantumaipartners.com/health

# Check what's actually in the docker directory
ls -la /opt/l9/docker/