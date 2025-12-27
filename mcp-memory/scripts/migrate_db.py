#!/usr/bin/env python3
"""
Database migration script for MCP Memory Server.

Usage:
    python -m mcp-memory.scripts.migrate_db

Reads MEMORY_DSN from environment or .env file.
"""

import asyncio
import structlog
import os
import sys
from pathlib import Path

import asyncpg
from dotenv import load_dotenv



logger = structlog.get_logger(__name__)
async def run_migration():
    # Load environment
    load_dotenv()
    dsn = os.getenv("MEMORY_DSN")

    if not dsn:
        logger.error("ERROR: MEMORY_DSN environment variable not set")
        sys.exit(1)

    # Find schema file
    schema_path = Path(__file__).parent.parent / "schema" / "init.sql"
    if not schema_path.exists():
        logger.error(f"ERROR: Schema file not found at {schema_path}")
        sys.exit(1)

    schema_sql = schema_path.read_text()

    logger.info(f"Connecting to: {dsn.split('@')[-1]}")

    try:
        conn = await asyncpg.connect(dsn)

        # Execute schema
        await conn.execute(schema_sql)

        logger.info("✓ Schema migration completed successfully")
        logger.info("  Tables: memory.shortterm, memory.mediumterm, memory.longterm, memory.auditlog")
        logger.info("  Indexes: created")
        logger.info("  Functions: memory.cleanup_expired(), memory.update_updatedat()")

        await conn.close()
    except Exception as exc:
        logger.error(f"ERROR: Migration failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_migration())

