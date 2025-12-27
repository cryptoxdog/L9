#!/usr/bin/env python3
"""
Test connection to the MCP Memory Server database and verify schema.

Usage:
    python -m mcp-memory.scripts.test_connection
"""

import asyncio
import os
import sys

import asyncpg
from dotenv import load_dotenv


async def test_connection():
    load_dotenv()
    dsn = os.getenv("MEMORY_DSN")

    if not dsn:
        print("ERROR: MEMORY_DSN environment variable not set")
        sys.exit(1)

    print(f"Testing connection to: {dsn.split('@')[-1]}")

    try:
        conn = await asyncpg.connect(dsn)

        # Check pgvector
        result = await conn.fetchval("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        if result:
            print("✓ pgvector extension: installed")
        else:
            print("✗ pgvector extension: NOT installed")
            sys.exit(1)

        # Check tables
        tables = ["memory.shortterm", "memory.mediumterm", "memory.longterm", "memory.auditlog"]
        for table in tables:
            schema, name = table.split(".")
            result = await conn.fetchval(
                "SELECT 1 FROM information_schema.tables WHERE table_schema = $1 AND table_name = $2",
                schema,
                name,
            )
            if result:
                print(f"✓ Table {table}: exists")
            else:
                print(f"✗ Table {table}: NOT found")
                sys.exit(1)

        # Check indexes (sample check)
        result = await conn.fetchval(
            "SELECT 1 FROM pg_indexes WHERE indexname = 'idx_longterm_embedding'"
        )
        if result:
            print("✓ Vector indexes: created")
        else:
            print("⚠ Vector indexes: may be missing (run migration)")

        # Quick insert/read test
        test_embedding = [0.1] * 1536
        await conn.execute(
            "INSERT INTO memory.shortterm (userid, kind, content, embedding, importance, metadata, expiresat) "
            "VALUES ($1, $2, $3, $4::vector, $5, $6, CURRENT_TIMESTAMP + INTERVAL '1 hour')",
            "_test_user_",
            "fact",
            "Test memory entry",
            test_embedding,
            1.0,
            {},
        )
        await conn.execute("DELETE FROM memory.shortterm WHERE userid = '_test_user_'")
        print("✓ Insert/delete test: passed")

        await conn.close()
        print("\n✅ All connection tests passed!")
    except Exception as exc:
        print(f"ERROR: Connection test failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_connection())

