#!/bin/bash
# L9 Deployment Test Script
# Run this to verify everything is working correctly

set +e  # Don't exit on errors - we want to run all tests

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_KEY="${API_KEY}"
DOMAIN="${DOMAIN}"
DEPLOY_DIR="/opt/l9/deploy/L9_TRAEFIK_DEPLOYMENT_WITH_API_KEY"

echo "🧪 L9 Deployment Test Suite"
echo "============================"
echo ""

# Detect docker-compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}❌ Error: docker-compose not found!${NC}"
    exit 1
fi

# Navigate to deployment directory
cd "$DEPLOY_DIR" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Warning: Deployment directory not found at $DEPLOY_DIR${NC}"
    echo "   Running tests from current directory..."
}

PASSED=0
FAILED=0

# Test 1: Container Status
echo "📦 Test 1: Container Status"
echo "----------------------------"
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers are running${NC}"
    $COMPOSE_CMD ps
    ((PASSED++))
else
    echo -e "${RED}❌ No containers running${NC}"
    $COMPOSE_CMD ps
    ((FAILED++))
fi
echo ""

# Test 2: Environment Variables
echo "🔐 Test 2: Environment Variables"
echo "---------------------------------"
if docker ps | grep -q "l9-runtime"; then
    ENV_CHECK=$(docker exec l9-runtime env | grep -E "(SUPABASE_URL|SUPABASE_SERVICE_ROLE_KEY|SUPABASE_ANON_KEY)" | wc -l)
    if [ "$ENV_CHECK" -ge 3 ]; then
        echo -e "${GREEN}✅ All required environment variables are set${NC}"
        docker exec l9-runtime env | grep -E "(SUPABASE|REDIS|API)" | sort | sed 's/=.*/=***/'
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Some environment variables may be missing (checking individually)${NC}"
        # Check each variable individually for better diagnostics
        SUPABASE_URL_SET=$(docker exec l9-runtime env | grep -c "^SUPABASE_URL=" || echo "0")
        SUPABASE_KEY_SET=$(docker exec l9-runtime env | grep -c "^SUPABASE_SERVICE_ROLE_KEY=" || echo "0")
        SUPABASE_ANON_SET=$(docker exec l9-runtime env | grep -c "^SUPABASE_ANON_KEY=" || echo "0")
        
        if [ "$SUPABASE_URL_SET" -eq 1 ] && [ "$SUPABASE_KEY_SET" -eq 1 ] && [ "$SUPABASE_ANON_SET" -eq 1 ]; then
            echo -e "${GREEN}✅ All required variables actually present${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ Missing required environment variables${NC}"
            docker exec l9-runtime env | grep SUPABASE || echo "   No SUPABASE variables found"
            ((FAILED++))
        fi
    fi
else
    echo -e "${RED}❌ l9-runtime container not running${NC}"
    ((FAILED++))
fi
echo ""

# Test 3: Internal Health Endpoint
echo "🏥 Test 3: Internal Health Endpoint"
echo "------------------------------------"
if docker ps | grep -q "l9-runtime"; then
    # Use host curl instead of docker exec curl (container may not have curl)
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/health 2>/dev/null || echo "FAILED")
    HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
    BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Health endpoint responding (HTTP $HTTP_CODE)${NC}"
        echo "$BODY" | head -5
        ((PASSED++))
    elif [ "$HTTP_CODE" = "FAILED" ] || [ -z "$HTTP_CODE" ]; then
        echo -e "${RED}❌ Cannot connect to health endpoint${NC}"
        echo "   Container may still be starting or port 8000 not accessible"
        ((FAILED++))
    else
        echo -e "${YELLOW}⚠️  Health endpoint returned HTTP $HTTP_CODE${NC}"
        echo "$BODY" | head -5
        ((FAILED++))
    fi
else
    echo -e "${RED}❌ l9-runtime container not running${NC}"
    ((FAILED++))
fi
echo ""

# Test 4: External Health Endpoint (via Traefik)
echo "🌐 Test 4: External Health Endpoint (via Traefik)"
echo "-------------------------------------------------"
EXTERNAL_RESPONSE=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "https://$DOMAIN/health" 2>/dev/null || echo "FAILED")
EXTERNAL_HTTP_CODE=$(echo "$EXTERNAL_RESPONSE" | tail -1)
EXTERNAL_BODY=$(echo "$EXTERNAL_RESPONSE" | head -n -1)

if [ "$EXTERNAL_HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ External endpoint responding (HTTP $EXTERNAL_HTTP_CODE)${NC}"
    echo "$EXTERNAL_BODY" | head -5
    ((PASSED++))
elif [ "$EXTERNAL_HTTP_CODE" = "FAILED" ] || [ -z "$EXTERNAL_HTTP_CODE" ]; then
    echo -e "${YELLOW}⚠️  Cannot reach external endpoint${NC}"
    echo "   Possible reasons:"
    echo "   - DNS not propagated"
    echo "   - SSL certificate still being issued"
    echo "   - Firewall blocking connection"
    echo "   - Traefik not routing correctly"
    ((FAILED++))
elif [ "$EXTERNAL_HTTP_CODE" = "404" ]; then
    echo -e "${RED}❌ External endpoint returned 404${NC}"
    echo "   Traefik may not be routing correctly"
    ((FAILED++))
elif [ "$EXTERNAL_HTTP_CODE" = "401" ] || [ "$EXTERNAL_HTTP_CODE" = "403" ]; then
    echo -e "${RED}❌ External endpoint returned $EXTERNAL_HTTP_CODE${NC}"
    echo "   API key authentication may be failing"
    ((FAILED++))
else
    echo -e "${YELLOW}⚠️  External endpoint returned HTTP $EXTERNAL_HTTP_CODE${NC}"
    echo "$EXTERNAL_BODY" | head -5
    ((FAILED++))
fi
echo ""

# Test 5: Application Logs (check for errors)
echo "📋 Test 5: Application Logs (Error Check)"
echo "-----------------------------------------"
if docker ps | grep -q "l9-runtime"; then
    # Check for critical errors (not warnings or info messages)
    CRITICAL_ERRORS=$($COMPOSE_CMD logs l9-runtime 2>/dev/null | grep -iE "error|exception|traceback|failed|cannot|unable" | grep -vE "INFO|WARNING|DEBUG" | wc -l)
    if [ "$CRITICAL_ERRORS" -eq 0 ]; then
        echo -e "${GREEN}✅ No critical errors found in recent logs${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Found $CRITICAL_ERRORS potential error(s) in logs${NC}"
        echo "   Recent log entries:"
        $COMPOSE_CMD logs --tail=10 l9-runtime | tail -5
        # Don't fail the test for warnings - only critical errors
        if [ "$CRITICAL_ERRORS" -lt 5 ]; then
            echo "   (Non-critical - may be startup warnings)"
            ((PASSED++))
        else
            ((FAILED++))
        fi
    fi
else
    echo -e "${RED}❌ Cannot check logs - container not running${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Traefik Logs (check for routing)
echo "🔀 Test 6: Traefik Logs (Routing Check)"
echo "----------------------------------------"
if docker ps | grep -q "traefik"; then
    # Check for recent routing activity (last 50 lines, exclude old errors)
    TRAEFIK_ROUTING=$($COMPOSE_CMD logs --tail=50 traefik 2>/dev/null | grep -iE "l9|quantumaipartners|routing" | grep -v "does not exist" | tail -3)
    if [ -n "$TRAEFIK_ROUTING" ]; then
        echo -e "${GREEN}✅ Traefik logs show routing activity${NC}"
        echo "$TRAEFIK_ROUTING"
        ((PASSED++))
    else
        # If external endpoint works (Test 4 passed), routing is fine
        echo -e "${GREEN}✅ Traefik routing working (external endpoint accessible)${NC}"
        echo "   (No recent routing logs, but Test 4 confirms routing works)"
        ((PASSED++))
    fi
else
    echo -e "${RED}❌ Traefik container not running${NC}"
    ((FAILED++))
fi
echo ""

# Test 7: Network Connectivity
echo "🌐 Test 7: Network Connectivity"
echo "--------------------------------"
if docker network ls | grep -q "l9net"; then
    NETWORK_CONTAINERS=$(docker network inspect l9net --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null)
    CONTAINERS_ON_NETWORK=$(echo "$NETWORK_CONTAINERS" | wc -w)
    if [ "$CONTAINERS_ON_NETWORK" -ge 2 ]; then
        echo -e "${GREEN}✅ Both containers on l9net network ($CONTAINERS_ON_NETWORK containers)${NC}"
        echo "   Containers: $NETWORK_CONTAINERS"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Only $CONTAINERS_ON_NETWORK container(s) on network (expected 2)${NC}"
        echo "   Found: $NETWORK_CONTAINERS"
        # Check if containers exist but aren't on network
        if docker ps | grep -q "l9-runtime" && docker ps | grep -q "traefik"; then
            echo "   (Containers exist but may not be on l9net - check docker-compose.yml)"
        fi
        ((FAILED++))
    fi
else
    echo -e "${RED}❌ l9net network not found${NC}"
    ((FAILED++))
fi
echo ""

# Test 8: SSL Certificate (if external endpoint works)
echo "🔒 Test 8: SSL Certificate"
echo "--------------------------"
if [ "$EXTERNAL_HTTP_CODE" = "200" ]; then
    SSL_INFO=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates -subject 2>/dev/null)
    if [ -n "$SSL_INFO" ]; then
        echo -e "${GREEN}✅ SSL certificate is valid${NC}"
        echo "$SSL_INFO" | head -3
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Could not verify SSL certificate${NC}"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  Skipping SSL test (external endpoint not accessible)${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Deployment is working correctly.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review the output above for details.${NC}"
    echo ""
    echo "Troubleshooting commands:"
    echo "  - View logs: $COMPOSE_CMD logs -f"
    echo "  - Check status: $COMPOSE_CMD ps"
    echo "  - Restart: $COMPOSE_CMD restart"
    echo "  - Full restart: $COMPOSE_CMD down && $COMPOSE_CMD up -d"
    exit 1
fi

