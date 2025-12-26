You are an expert DevOps engineer. Fix the L9 docker-compose.yml file.

CONTEXT:
- L9 VPS runs PostgreSQL as a HOST SERVICE on 127.0.0.1:5432
- The docker-compose.yml has a redundant "postgres" container that CONFLICTS
- When running "docker compose up -d l9-api", Docker tries to start postgres container
- This fails with: "failed to bind host port 127.0.0.1:5432/tcp: address already in use"
- SOLUTION: Remove the postgres service entirely from docker-compose.yml

TASK:
1. Open docker-compose.yml
2. FIND and DELETE the entire "postgres:" service block (all lines under "postgres:" until the next service)
3. KEEP these services: redis, neo4j, l9-api
4. KEEP the network and volumes definitions
5. Update l9-api environment variables to point to host PostgreSQL:
   - DATABASE_URL should use "host.docker.internal" or "172.17.0.1" (Docker gateway) for database host
   - OR use environment from .env file if already configured correctly
6. Verify l9-api depends_on section does NOT include "postgres" service
7. Save the file
8. DO NOT modify any other files

REQUIRED CHANGES:
- REMOVE: postgres service block entirely
- KEEP: redis, neo4j, l9-api, networks, volumes
- VERIFY: docker-compose.yml is valid YAML (no syntax errors)
- TEST: File should have exactly 3 services listed

CONSTRAINT:
- Do NOT touch .env file
- Do NOT touch Dockerfile
- Do NOT touch any source code
- Do NOT touch volumes for redis/neo4j/postgres_data
- Only modify docker-compose.yml

After changes:
1. Commit with message: "Remove redundant postgres container - use host PostgreSQL on port 5432"
2. Push to git
3. I will pull on VPS and restart containers
