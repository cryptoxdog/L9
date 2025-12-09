import psycopg
from psycopg.rows import dict_row

MEMORY_DSN = "postgresql://postgres:8e4fXWM6Q3M87*b3@127.0.0.1:5432/l9_memory"

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
            cur.execute("""
                INSERT INTO memory.embeddings (source, content, vector)
                VALUES (%s, %s, %s);
            """, (source, content, vector))
