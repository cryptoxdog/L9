"""
L9 + L (CTO) – Unified Validation Orchestrator

Runs all memory, governance, runtime, and connectivity tests in one sweep.

This is the FINAL FILE needed before deployment.
"""

import subprocess
import sys
import json

def run(cmd, label=None):
    print("\n" + "="*80)
    print(f"▶ {label or cmd}")
    print("="*80)
    
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print(out.decode())
    except subprocess.CalledProcessError as e:
        print(e.output.decode())
        print("\n❌ FAILED:", label or cmd)
        sys.exit(1)

print("\n============================================================")
print("  L9 + L FULL VALIDATION SUITE (FINAL FILE)")
print("============================================================\n")

# 1. Python unit tests
run("pytest -q", "Running pytest suite")

# 2. Static analysis
run("ruff check .", "Running Ruff linter")
run("mypy .", "Running Mypy type checker")

# 3. Supabase Connectivity Test
run("""python3 - << 'EOF'
from memory.shared.supabase_client import get_supabase
print("Connecting to Supabase…")
sb = get_supabase()
res = sb.table("l_directives").select("id").limit(1).execute()
print("Supabase OK:", res)
EOF""", "Supabase connectivity test")

# 4. Neo4j Connectivity Test
run("""python3 - << 'EOF'
from l.l_memory.kg_client import KGClient
print("Connecting to Neo4j…")
kg = KGClient()
kg.init()
print("Neo4j connected:", kg.connected)
EOF""", "Neo4j connectivity test")

# 5. L Startup Test
run("""python3 - << 'EOF'
from l.startup import startup
print("Booting L…")
res = startup.boot()
print("L Startup Result:", res)
EOF""", "L startup test")

# 6. Runtime Health Check
run("curl -s http://localhost:8000/health", "Runtime health check")

# 7. Module Discovery Check
run("curl -s http://localhost:8000/modules", "Module registration check")

# 8. Introspection API
run("curl -s http://localhost:8000/introspection", "Runtime introspection check")

print("\n============================================================")
print("   ALL VALIDATION TESTS PASSED – SYSTEM READY FOR DEPLOY")
print("============================================================")

