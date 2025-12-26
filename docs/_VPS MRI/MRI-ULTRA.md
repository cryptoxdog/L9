```bash
#!/bin/bash
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      L9 VPS CONSOLIDATED MRI - COMPLETE SYSTEM DIAGNOSTIC      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo "Generated: $(date)"
echo ""

# ═══════════════════════════════════════════════════════════════
# PART A: SYSTEM-LEVEL DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A1. SYSTEM IDENTITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
hostname
echo "User: $(whoami)"
ip addr show | grep "inet " | grep -v "127.0.0.1"
uname -a
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A2. ALL LISTENING PORTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo ss -tlnp 2>/dev/null || sudo netstat -tlnp 2>/dev/null
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A3. CADDY STATUS & CONFIG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo systemctl status caddy --no-pager 2>/dev/null | head -5 || echo "Caddy not installed"
echo ""
echo "Caddy config:"
cat /etc/caddy/Caddyfile 2>/dev/null | head -30 || echo "No Caddyfile found"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
^C`o "╚════════════════════════════════════════════════════════════════╝"LIC FAIL"ed|Failed" || echo "No C
admin@L9:/opt/l9$ echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      L9 VPS CONSOLIDATED MRI - COMPLETE SYSTEM DIAGNOSTIC      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo "Generated: $(date)"
echo ""

# ═══════════════════════════════════════════════════════════════
# PART A: SYSTEM-LEVEL DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A1. SYSTEM IDENTITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
hostname
echo "User: $(whoami)"
ip addr show | grep "inet " | grep -v "127.0.0.1"
uname -a
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A2. ALL LISTENING PORTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo ss -tlnp 2>/dev/null || sudo netstat -tlnp 2>/dev/null
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A3. CADDY STATUS & CONFIG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo systemctl status caddy --no-pager 2>/dev/null | head -5 || echo "Caddy not installed"
echo ""
echo "Caddy config:"
cat /etc/caddy/Caddyfile 2>/dev/null | head -30 || echo "No Caddyfile found"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "A4. L9 SERVICE STATUS (systemd)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "╚════════════════════════════════════════════════════════════════╝"