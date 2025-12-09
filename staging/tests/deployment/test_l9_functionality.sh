#!/bin/bash
# Test L9 Functionality on Server
# Tests actual L9 reasoning capabilities

set -e

L9_API_KEY="${L9_API_KEY:-${API_KEY}}"
DOMAIN="${DOMAIN}"

echo "🧪 Testing L9 Functionality"
echo "============================"
echo ""

# Test 1: Tree-of-Thoughts Expansion
echo "1️⃣ Testing Tree-of-Thoughts Expansion..."
echo "----------------------------------------"
curl -sS -X POST \
  -H "X-API-Key: $L9_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "proposal": {
      "type": "market_expansion",
      "expected_roi": 0.20,
      "risk_score": 6.0,
      "description": "Expand into new market segment"
    },
    "k_branches": 3,
    "top_m": 2
  }' \
  "https://$DOMAIN/api/tot/expand" | python3 -m json.tool || echo "❌ Failed"
echo ""

# Test 2: Full Reasoning Endpoint
echo "2️⃣ Testing Full Reasoning..."
echo "----------------------------"
curl -sS -X POST \
  -H "X-API-Key: $L9_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Should we expand into the European market?",
    "reasoning_mode": "abductive"
  }' \
  "https://$DOMAIN/api/reason" | python3 -m json.tool || echo "❌ Failed"
echo ""

# Test 3: Knowledge Graph Query
echo "3️⃣ Testing Knowledge Graph Query..."
echo "------------------------------------"
curl -sS -X POST \
  -H "X-API-Key: $L9_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (n) RETURN count(n) as node_count"
  }' \
  "https://$DOMAIN/api/knowledge/query" | python3 -m json.tool || echo "❌ Failed"
echo ""

echo "✅ Testing complete!"

