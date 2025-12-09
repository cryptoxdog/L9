"""
L9 Tasks Debug Utility
Simple debug script to inspect tasks table.
"""

import logging
import os

import psycopg2

logger = logging.getLogger(__name__)

# Database DSN from environment only - no hardcoded fallback
DB_DSN = os.environ.get("DATABASE_URL") or os.environ.get("L9_DB_DSN")


def show_tasks(limit: int = 50):
    """Fetch and log recent tasks from the database."""
    if not DB_DSN:
        logger.error("DATABASE_URL or L9_DB_DSN environment variable not set")
        return
    
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, type, status, created_at, completed_at FROM tasks ORDER BY created_at DESC LIMIT %s;",
            (limit,)
        )
        for row in cur.fetchall():
            logger.debug("Task row: %s", row)
        cur.close()
        conn.close()
    except Exception as e:
        logger.error("Failed to fetch tasks: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    show_tasks()
