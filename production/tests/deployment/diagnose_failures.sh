#!/bin/bash
# Diagnostic script to identify which tests are failing and why

set +e  # Don't exit on errors - we want to see all failures

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_KEY="${API_KEY}"
DOMAIN="${DOMAIN}"

# Detect docker-compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

echo -e "${BLUE}🔍 L9 Deployment Failure Diagnostic${NC}"
echo "=========================================="
echo ""

# Test 1: Container Status
echo -e "${BLUE}[TEST 1] Container Status${NC}"
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    $COMPOSE_CMD ps
fi
echo ""

# Test 2: Environment Variables - Detailed
echo -e "${BLUE}[TEST 2] Environment Variables${NC}"
if docker ps | grep -q "l9-runtime"; then
    echo "Checking SUPABASE_URL..."
    SUPABASE_URL=$(docker exec l9-runtime env | grep "^SUPABASE_URL=" | cut -d'=' -f2)
    if [ -z "$SUPABASE_URL" ]; then
        echo -e "${RED}❌ FAIL: SUPABASE_URL is not set${NC}"
    elif [ "$SUPABASE_URL" = "YOUR_SERVICE_ROLE_KEY_HERE" ] || [ "$SUPABASE_URL" = "" ]; then
        echo -e "${RED}❌ FAIL: SUPABASE_URL is empty or placeholder${NC}"
    else
        echo -e "${GREEN}✅ PASS: SUPABASE_URL is set${NC}"
        echo "   Value: ${SUPABASE_URL:0:30}..."
    fi
    
    echo "Checking SUPABASE_SERVICE_ROLE_KEY..."
    SUPABASE_KEY=$(docker exec l9-runtime env | grep "^SUPABASE_SERVICE_ROLE_KEY=" | cut -d'=' -f2)
    if [ -z "$SUPABASE_KEY" ]; then
        echo -e "${RED}❌ FAIL: SUPABASE_SERVICE_ROLE_KEY is not set${NC}"
    elif [ "$SUPABASE_KEY" = "YOUR_SERVICE_ROLE_KEY_HERE" ]; then
        echo -e "${RED}❌ FAIL: SUPABASE_SERVICE_ROLE_KEY is placeholder${NC}"
    else
        echo -e "${GREEN}✅ PASS: SUPABASE_SERVICE_ROLE_KEY is set${NC}"
        echo "   Length: ${#SUPABASE_KEY} characters"
    fi
    
    echo "Checking SUPABASE_ANON_KEY..."
    ANON_KEY=$(docker exec l9-runtime env | grep "^SUPABASE_ANON_KEY=" | cut -d'=' -f2)
    if [ -z "$ANON_KEY" ]; then
        echo -e "${RED}❌ FAIL: SUPABASE_ANON_KEY is not set${NC}"
    else
        echo -e "${GREEN}✅ PASS: SUPABASE_ANON_KEY is set${NC}"
    fi
    
    echo ""
    echo "All environment variables:"
    docker exec l9-runtime env | grep -E "(SUPABASE|REDIS|API)" | sort | sed 's/=.*/=***/'
else
    echo -e "${RED}❌ FAIL: l9-runtime container not running${NC}"
fi
echo ""

# Test 3: Internal Health Endpoint - Detailed
echo -e "${BLUE}[TEST 3] Internal Health Endpoint${NC}"
if docker ps | grep -q "l9-runtime"; then
    echo "Attempting curl to http://localhost:8000/health..."
    HEALTH_OUTPUT=$(docker exec l9-runtime curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/health 2>&1)
    HTTP_CODE=$(echo "$HEALTH_OUTPUT" | grep "HTTP_CODE:" | cut -d':' -f2)
    BODY=$(echo "$HEALTH_OUTPUT" | grep -v "HTTP_CODE:")
    
    if [ -z "$HTTP_CODE" ]; then
        echo -e "${RED}❌ FAIL: Cannot connect to health endpoint${NC}"
        echo "   Full output:"
        echo "$HEALTH_OUTPUT"
        echo ""
        echo "   Checking if uvicorn is running..."
        docker exec l9-runtime ps aux | grep uvicorn || echo "   No uvicorn process found"
        echo ""
        echo "   Checking if port 8000 is listening..."
        docker exec l9-runtime netstat -tlnp 2>/dev/null | grep 8000 || docker exec l9-runtime ss -tlnp 2>/dev/null | grep 8000 || echo "   Port 8000 not listening"
    elif [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ PASS: Health endpoint responding (HTTP $HTTP_CODE)${NC}"
        echo "   Response:"
        echo "$BODY" | head -3 | sed 's/^/   /'
    else
        echo -e "${RED}❌ FAIL: Health endpoint returned HTTP $HTTP_CODE${NC}"
        echo "   Response:"
        echo "$BODY" | head -5
    fi
else
    echo -e "${RED}❌ FAIL: Container not running${NC}"
fi
echo ""

# Test 4: Application Logs - Check for startup errors
echo -e "${BLUE}[TEST 4] Application Startup Logs${NC}"
if docker ps | grep -q "l9-runtime"; then
    echo "Last 30 lines of logs:"
    $COMPOSE_CMD logs --tail=30 l9-runtime 2>&1 | tail -20
    
    echo ""
    echo "Checking for common errors..."
    ERROR_COUNT=$($COMPOSE_CMD logs l9-runtime 2>&1 | grep -iE "error|exception|traceback|failed|cannot|unable" | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Found $ERROR_COUNT potential error(s)${NC}"
        echo "   Recent errors:"
        $COMPOSE_CMD logs l9-runtime 2>&1 | grep -iE "error|exception|traceback|failed|cannot|unable" | tail -5
    else
        echo -e "${GREEN}✅ No obvious errors in logs${NC}"
    fi
else
    echo -e "${RED}❌ FAIL: Cannot check logs - container not running${NC}"
fi
echo ""

# Test 5: Check if main.py exists and is accessible
echo -e "${BLUE}[TEST 5] Application Files${NC}"
if docker ps | grep -q "l9-runtime"; then
    echo "Checking if main.py exists in container..."
    if docker exec l9-runtime test -f /app/main.py; then
        echo -e "${GREEN}✅ PASS: main.py exists${NC}"
        echo "   File size: $(docker exec l9-runtime stat -c%s /app/main.py 2>/dev/null || echo 'unknown') bytes"
        echo "   First few lines:"
        docker exec l9-runtime head -5 /app/main.py | sed 's/^/   /'
    else
        echo -e "${RED}❌ FAIL: main.py not found in /app/${NC}"
        echo "   Files in /app/:"
        docker exec l9-runtime ls -la /app/ 2>/dev/null | head -10
    fi
    
    echo ""
    echo "Checking Python/uvicorn availability..."
    if docker exec l9-runtime which python3 > /dev/null 2>&1; then
        PYTHON_VERSION=$(docker exec l9-runtime python3 --version 2>&1)
        echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ Python3 not found${NC}"
    fi
    
    if docker exec l9-runtime which uvicorn > /dev/null 2>&1; then
        UVICORN_VERSION=$(docker exec l9-runtime uvicorn --version 2>&1)
        echo -e "${GREEN}✅ Uvicorn found: $UVICORN_VERSION${NC}"
    else
        echo -e "${RED}❌ Uvicorn not found${NC}"
    fi
else
    echo -e "${RED}❌ FAIL: Container not running${NC}"
fi
echo ""

# Test 6: External Endpoint - Detailed
echo -e "${BLUE}[TEST 6] External Endpoint (via Traefik)${NC}"
echo "Testing: curl -H 'X-API-Key: ...' https://$DOMAIN/health"
EXTERNAL_OUTPUT=$(curl -s -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}" -H "X-API-Key: $API_KEY" "https://$DOMAIN/health" 2>&1)
EXTERNAL_HTTP=$(echo "$EXTERNAL_OUTPUT" | grep "HTTP_CODE:" | cut -d':' -f2)
EXTERNAL_TIME=$(echo "$EXTERNAL_OUTPUT" | grep "TIME:" | cut -d':' -f2)
EXTERNAL_BODY=$(echo "$EXTERNAL_OUTPUT" | grep -vE "HTTP_CODE|TIME")

if [ -z "$EXTERNAL_HTTP" ]; then
    echo -e "${RED}❌ FAIL: Cannot connect to external endpoint${NC}"
    echo "   Possible issues:"
    echo "   - DNS not pointing to server"
    echo "   - Firewall blocking port 443"
    echo "   - Traefik not routing correctly"
    echo ""
    echo "   Testing DNS resolution..."
    nslookup $DOMAIN 2>&1 | grep -A 2 "Name:" || echo "   DNS lookup failed"
    echo ""
    echo "   Testing if port 443 is open..."
    timeout 3 bash -c "</dev/tcp/$DOMAIN/443" 2>/dev/null && echo "   ✅ Port 443 is open" || echo "   ❌ Port 443 is closed or unreachable"
elif [ "$EXTERNAL_HTTP" = "200" ]; then
    echo -e "${GREEN}✅ PASS: External endpoint responding (HTTP $EXTERNAL_HTTP, ${EXTERNAL_TIME}s)${NC}"
    echo "   Response:"
    echo "$EXTERNAL_BODY" | head -3 | sed 's/^/   /'
elif [ "$EXTERNAL_HTTP" = "404" ]; then
    echo -e "${RED}❌ FAIL: 404 Not Found${NC}"
    echo "   Traefik is not routing to l9-runtime"
    echo "   Checking Traefik logs..."
    $COMPOSE_CMD logs --tail=20 traefik | grep -i "l9\|error\|404" || echo "   No relevant Traefik logs"
elif [ "$EXTERNAL_HTTP" = "401" ] || [ "$EXTERNAL_HTTP" = "403" ]; then
    echo -e "${RED}❌ FAIL: HTTP $EXTERNAL_HTTP (Authentication failed)${NC}"
    echo "   API key middleware may not be working"
    echo "   Response:"
    echo "$EXTERNAL_BODY" | head -3
else
    echo -e "${YELLOW}⚠️  Unexpected HTTP code: $EXTERNAL_HTTP${NC}"
    echo "   Response:"
    echo "$EXTERNAL_BODY" | head -5
fi
echo ""

# Test 7: Traefik Configuration
echo -e "${BLUE}[TEST 7] Traefik Configuration${NC}"
if docker ps | grep -q "traefik"; then
    echo "Checking Traefik labels on l9-runtime..."
    LABELS=$(docker inspect l9-runtime --format '{{range $k, $v := .Config.Labels}}{{$k}}={{$v}}{{"\n"}}{{end}}' 2>/dev/null | grep traefik)
    if echo "$LABELS" | grep -q "traefik.enable=true"; then
        echo -e "${GREEN}✅ Traefik enabled on l9-runtime${NC}"
    else
        echo -e "${RED}❌ Traefik not enabled on l9-runtime${NC}"
    fi
    
    if echo "$LABELS" | grep -q "traefik.http.routers.l9.rule"; then
        echo -e "${GREEN}✅ Router rule configured${NC}"
        echo "$LABELS" | grep "traefik.http.routers.l9.rule" | sed 's/^/   /'
    else
        echo -e "${RED}❌ Router rule not configured${NC}"
    fi
    
    echo ""
    echo "All Traefik labels on l9-runtime:"
    echo "$LABELS" | sed 's/^/   /' || echo "   No Traefik labels found"
else
    echo -e "${RED}❌ FAIL: Traefik container not running${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo -e "${BLUE}📊 Diagnostic Summary${NC}"
echo "=========================================="
echo ""
echo "Run this command to see full test results:"
echo "  bash TEST_DEPLOYMENT.sh"
echo ""
echo "Common fixes:"
echo "  1. If env vars missing: Check .env file exists and has correct values"
echo "  2. If health endpoint fails: Check main.py exists and uvicorn is running"
echo "  3. If external endpoint fails: Check Traefik labels and DNS"
echo ""

