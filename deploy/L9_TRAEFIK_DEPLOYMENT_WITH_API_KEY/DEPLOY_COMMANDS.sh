#!/bin/bash
# L9 VPS Deployment - Complete Command Sequence
# Run these commands in order on your VPS

set -e  # Exit on error

echo "🚀 Starting L9 Deployment Fix Sequence..."
echo ""

# ============================================================================
# STEP 1: Navigate to deployment directory
# ============================================================================
echo "📁 Step 1: Navigating to deployment directory..."
cd /opt/l9/deploy/L9_TRAEFIK_DEPLOYMENT_WITH_API_KEY || {
    echo "❌ Error: Deployment directory not found!"
    echo "   Creating directory structure..."
    sudo mkdir -p /opt/l9/deploy/L9_TRAEFIK_DEPLOYMENT_WITH_API_KEY
    cd /opt/l9/deploy/L9_TRAEFIK_DEPLOYMENT_WITH_API_KEY
}
echo "✅ Current directory: $(pwd)"
echo ""

# ============================================================================
# STEP 2: Backup existing configuration
# ============================================================================
echo "💾 Step 2: Backing up existing configuration..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
[ -f docker-compose.yml ] && cp docker-compose.yml "$BACKUP_DIR/" && echo "✅ Backed up docker-compose.yml"
[ -f traefik.yml ] && cp traefik.yml "$BACKUP_DIR/" && echo "✅ Backed up traefik.yml"
[ -f .env ] && cp .env "$BACKUP_DIR/" && echo "✅ Backed up .env"
echo "📁 Backup location: $BACKUP_DIR"
echo ""

# ============================================================================
# STEP 3: Verify .env file exists and has required variables
# ============================================================================
echo "🔍 Step 3: Checking .env file..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "   Creating .env from template..."
    cat > .env << 'ENVEOF'
# L9 Runtime Environment Variables
SUPABASE_URL=https://ijqgklesxtukbhbkosxg.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY_HERE
SUPABASE_ANON_KEY=YOUR_ANON_KEY_HERE
REDIS_ENABLED=false
API_KEY=16a2376cfc93bc9acc2bb78c8c0a53ade7c1ef26ab0842a0140bfa7ac67508ba
ENVEOF
    echo "⚠️  IMPORTANT: Edit .env file and add your actual Supabase keys!"
    echo "   Run: nano .env"
    read -p "   Press Enter after you've updated .env file..."
else
    echo "✅ .env file exists"
    # Check for required variables
    if grep -q "SUPABASE_URL=" .env && grep -q "SUPABASE_SERVICE_ROLE_KEY=" .env && grep -q "SUPABASE_ANON_KEY=" .env; then
        echo "✅ All required environment variables found in .env"
    else
        echo "⚠️  Warning: Some required variables may be missing in .env"
        echo "   Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY"
    fi
fi
echo ""

# ============================================================================
# STEP 4: Detect docker-compose command
# ============================================================================
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Error: docker-compose not found!"
    exit 1
fi
echo "✅ Using: $COMPOSE_CMD"
echo ""

# ============================================================================
# STEP 5: Stop existing containers
# ============================================================================
echo "🛑 Step 5: Stopping existing containers..."
$COMPOSE_CMD down 2>/dev/null || echo "   No containers running"
echo "✅ Containers stopped"
echo ""

# ============================================================================
# STEP 6: Verify docker-compose.yml and traefik.yml are updated
# ============================================================================
echo "📝 Step 6: Verifying configuration files..."
if [ ! -f docker-compose.yml ]; then
    echo "❌ docker-compose.yml not found! Please copy it to this directory."
    exit 1
fi

if [ ! -f traefik.yml ]; then
    echo "❌ traefik.yml not found! Please copy it to this directory."
    exit 1
fi

# Check if docker-compose.yml has the fixes
if grep -q "SUPABASE_URL=\${SUPABASE_URL}" docker-compose.yml && grep -q "env_file:" docker-compose.yml; then
    echo "✅ docker-compose.yml has environment variable fixes"
else
    echo "⚠️  Warning: docker-compose.yml may not have all fixes applied"
fi

if grep -q "traefik.http.routers.l9.rule" docker-compose.yml && grep -q "l9-runtime:" docker-compose.yml -A 20 | grep -q "labels:"; then
    echo "✅ docker-compose.yml has Traefik labels on l9-runtime service"
else
    echo "⚠️  Warning: Traefik labels may not be correctly configured"
fi

if grep -q "providers.file.filename" docker-compose.yml; then
    echo "✅ docker-compose.yml has Traefik file provider configured"
else
    echo "⚠️  Warning: Traefik file provider may not be configured"
fi
echo ""

# ============================================================================
# STEP 8: Create letsencrypt directory if it doesn't exist
# ============================================================================
echo "📁 Step 8: Setting up Let's Encrypt directory..."
mkdir -p letsencrypt
chmod 600 letsencrypt 2>/dev/null || sudo chmod 600 letsencrypt
echo "✅ Let's Encrypt directory ready"
echo ""

# ============================================================================
# STEP 9: Validate docker-compose configuration
# ============================================================================
echo "🔍 Step 9: Validating docker-compose configuration..."

# Validate config and show errors if any
CONFIG_OUTPUT=$($COMPOSE_CMD config 2>&1)
CONFIG_EXIT=$?

if [ $CONFIG_EXIT -eq 0 ]; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has errors!"
    echo ""
    echo "$CONFIG_OUTPUT"
    echo ""
    echo "Please fix the errors above and try again."
    exit 1
fi
echo ""

# ============================================================================
# STEP 10: Pull/rebuild images if needed
# ============================================================================
echo "🔨 Step 10: Checking if image needs to be built..."
if docker images | grep -q "l9-runtime"; then
    echo "✅ l9-runtime image exists"
    echo "   To rebuild: docker-compose build --no-cache l9-runtime"
else
    echo "⚠️  l9-runtime image not found"
    echo "   Note: Using pre-built image. If you need to rebuild, run:"
    echo "   docker-compose build --no-cache l9-runtime"
fi
echo ""

# ============================================================================
# STEP 11: Start services
# ============================================================================
echo "🚀 Step 11: Starting services..."
$COMPOSE_CMD up -d
echo "✅ Services started"
echo ""

# ============================================================================
# STEP 12: Wait for services to be ready
# ============================================================================
echo "⏳ Step 12: Waiting for services to be ready..."
sleep 5
echo "✅ Wait complete"
echo ""

# ============================================================================
# STEP 13: Check container status
# ============================================================================
echo "📊 Step 13: Checking container status..."
$COMPOSE_CMD ps
echo ""

# ============================================================================
# STEP 12: Verify environment variables are loaded
# ============================================================================
echo "🔍 Step 12: Verifying environment variables..."
if docker ps | grep -q "l9-runtime"; then
    echo "Environment variables in l9-runtime container:"
    docker exec l9-runtime env | grep -E "(SUPABASE|REDIS|API)" | sort
    echo ""
    
    # Check if SUPABASE_URL is set
    if docker exec l9-runtime env | grep -q "SUPABASE_URL="; then
        SUPABASE_VAL=$(docker exec l9-runtime env | grep "SUPABASE_URL=" | cut -d'=' -f2)
        if [ -n "$SUPABASE_VAL" ] && [ "$SUPABASE_VAL" != "YOUR_SERVICE_ROLE_KEY_HERE" ]; then
            echo "✅ SUPABASE_URL is set correctly"
        else
            echo "⚠️  Warning: SUPABASE_URL may not be set correctly"
        fi
    else
        echo "❌ SUPABASE_URL is NOT set!"
    fi
else
    echo "⚠️  l9-runtime container is not running"
fi
echo ""

# ============================================================================
# STEP 15: Check application logs
# ============================================================================
echo "📋 Step 15: Checking application logs (last 20 lines)..."
$COMPOSE_CMD logs --tail=20 l9-runtime
echo ""

# ============================================================================
# STEP 16: Check Traefik logs
# ============================================================================
echo "📋 Step 16: Checking Traefik logs (last 20 lines)..."
$COMPOSE_CMD logs --tail=20 traefik
echo ""

# ============================================================================
# STEP 17: Test health endpoint (internal)
# ============================================================================
echo "🏥 Step 17: Testing health endpoint (internal)..."
if docker ps | grep -q "l9-runtime"; then
    HEALTH_RESPONSE=$(docker exec l9-runtime curl -s http://localhost:8000/health 2>/dev/null || echo "FAILED")
    if [ "$HEALTH_RESPONSE" != "FAILED" ] && echo "$HEALTH_RESPONSE" | grep -q "status"; then
        echo "✅ Health endpoint responding:"
        echo "$HEALTH_RESPONSE" | head -5
    else
        echo "⚠️  Health endpoint not responding or error occurred"
        echo "   Response: $HEALTH_RESPONSE"
    fi
else
    echo "⚠️  Cannot test - l9-runtime container not running"
fi
echo ""

# ============================================================================
# STEP 18: Test external endpoint (via Traefik)
# ============================================================================
echo "🌐 Step 18: Testing external endpoint (via Traefik)..."
API_KEY="16a2376cfc93bc9acc2bb78c8c0a53ade7c1ef26ab0842a0140bfa7ac67508ba"
EXTERNAL_RESPONSE=$(curl -s -i -H "X-API-Key: $API_KEY" https://quantumaipartners.com/health 2>/dev/null || echo "FAILED")
if echo "$EXTERNAL_RESPONSE" | grep -q "200 OK\|status.*ok"; then
    echo "✅ External endpoint responding:"
    echo "$EXTERNAL_RESPONSE" | head -10
else
    echo "⚠️  External endpoint test:"
    echo "$EXTERNAL_RESPONSE" | head -10
    echo ""
    echo "   This may be normal if:"
    echo "   - DNS hasn't propagated"
    echo "   - SSL certificate is still being issued"
    echo "   - Service is still starting"
fi
echo ""

# ============================================================================
# STEP 19: Verify Traefik routing
# ============================================================================
echo "🔀 Step 19: Verifying Traefik routing..."
if docker ps | grep -q "traefik"; then
    echo "Traefik detected services:"
    docker exec traefik wget -qO- http://localhost:8080/api/http/services 2>/dev/null | grep -o '"l9"' || echo "   (Traefik API not accessible or service not registered)"
else
    echo "⚠️  Traefik container not running"
fi
echo ""

# ============================================================================
# STEP 20: Network verification
# ============================================================================
echo "🌐 Step 20: Verifying Docker network..."
if docker network ls | grep -q "l9net"; then
    echo "✅ l9net network exists"
    echo "Containers on l9net:"
    docker network inspect l9net --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null || echo "   (Unable to inspect network)"
else
    echo "⚠️  l9net network not found"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "=========================================="
echo "📊 DEPLOYMENT SUMMARY"
echo "=========================================="
echo ""
echo "Container Status:"
$COMPOSE_CMD ps
echo ""
echo "Next Steps:"
echo "1. Monitor logs: $COMPOSE_CMD logs -f"
echo "2. Check specific service: $COMPOSE_CMD logs -f l9-runtime"
echo "3. Restart if needed: $COMPOSE_CMD restart l9-runtime"
echo "4. Test endpoint: curl -H 'X-API-Key: $API_KEY' https://quantumaipartners.com/health"
echo ""
echo "Troubleshooting:"
echo "- View all logs: $COMPOSE_CMD logs"
echo "- Check env vars: docker exec l9-runtime env | grep SUPABASE"
echo "- Restart services: $COMPOSE_CMD restart"
echo "- Full restart: $COMPOSE_CMD down && $COMPOSE_CMD up -d"
echo ""
echo "✅ Deployment sequence complete!"
echo ""

