import psycopg
import os

DB_DSN = os.environ.get("L9_PG_DSN")

def save_embedding(source, content, embedding):
    with psycopg.connect(DB_DSN) as conn:
        conn.execute(
            "INSERT INTO memory.embeddings (source, content, embedding) VALUES (%s, %s, %s)",
            (source, content, embedding)
        )
