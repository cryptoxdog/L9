import os
import psycopg

# Get DSN from environment - NEVER hardcode localhost in Docker!
# Inside containers, use service DNS (l9-postgres:5432)
# Outside containers, use host networking or published ports
MEMORY_DSN = os.getenv(
    "MEMORY_DSN",
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@l9-postgres:5432/l9_memory"),
)


def init_db():
    with psycopg.connect(MEMORY_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS memory;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memory.embeddings (
                    id SERIAL PRIMARY KEY,
                    source TEXT,
                    content TEXT,
                    vector VECTOR(1536)
                );
            """)


def insert_embedding(source, content, vector=None):
    with psycopg.connect(MEMORY_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memory.embeddings (source, content, vector)
                VALUES (%s, %s, %s);
            """,
                (source, content, vector),
            )
