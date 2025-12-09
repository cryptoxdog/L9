# l/startup_memory.py

from l.memory.l1.l1_router import router as l1
from l.memory.mac.mac_router import router as mac
from l.memory.meta.meta_router import router as meta
from l.memory.shared.connection_validator import validator
from l.memory.shared.schema_cache import get_schema_cache

def initialize_memory_layer():
    env = validator.validate_env()
    if env["missing_env"]:
        print("❌ Missing Supabase env vars:", env["missing_env"])

    tables = validator.validate_tables()
    print("🔍 Table Status:", tables)

    schema = get_schema_cache()
    print("📘 Loaded schema cache:", list(schema.keys()))

    return {
        "l1": l1,
        "mac": mac,
        "meta": meta,
        "schema": schema
    }

