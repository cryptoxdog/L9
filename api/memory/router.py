from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from api.auth import verify_api_key
import psycopg
import os
from typing import Optional, List

router = APIRouter()

MEMORY_DSN = os.environ.get("MEMORY_DSN", "postgresql://postgres:8e4fXWM6Q3M87*b3@127.0.0.1:5432/l9_memory")

class EmbeddingRequest(BaseModel):
    source: str
    content: str
    embedding: Optional[List[float]] = None

class EmbeddingResponse(BaseModel):
    id: int
    source: str
    content: str
    created_at: str

@router.post("/test")
async def memory_test(
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    return {"ok": True, "msg": "memory endpoint reachable"}

@router.post("/embeddings", response_model=dict)
async def create_embedding(
    request: EmbeddingRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """Create and store an embedding"""
    try:
        with psycopg.connect(MEMORY_DSN) as conn:
            with conn.cursor() as cur:
                # Convert embedding list to pgvector format if provided
                embedding_str = None
                if request.embedding:
                    embedding_str = f"[{','.join(map(str, request.embedding))}]"
                
                cur.execute(
                    """
                    INSERT INTO memory.embeddings (source, content, embedding)
                    VALUES (%s, %s, %s)
                    RETURNING id, source, content, created_at;
                    """,
                    (request.source, request.content, embedding_str)
                )
                result = cur.fetchone()
                conn.commit()
                
                return {
                    "success": True,
                    "id": result[0],
                    "source": result[1],
                    "content": result[2],
                    "created_at": str(result[3])
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create embedding: {str(e)}")

@router.get("/embeddings", response_model=dict)
async def list_embeddings(
    limit: int = 10,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """List stored embeddings"""
    try:
        with psycopg.connect(MEMORY_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, source, content, created_at
                    FROM memory.embeddings
                    ORDER BY created_at DESC
                    LIMIT %s;
                    """,
                    (limit,)
                )
                results = cur.fetchall()
                
                return {
                    "count": len(results),
                    "embeddings": [
                        {
                            "id": r[0],
                            "source": r[1],
                            "content": r[2][:100] + "..." if len(r[2]) > 100 else r[2],
                            "created_at": str(r[3])
                        }
                        for r in results
                    ]
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list embeddings: {str(e)}")

@router.get("/stats")
async def get_stats(
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """Get memory system statistics"""
    try:
        with psycopg.connect(MEMORY_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM memory.embeddings;")
                embedding_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM memory.raw_text;")
                raw_text_count = cur.fetchone()[0]
                
                return {
                    "embeddings": embedding_count,
                    "raw_text": raw_text_count,
                    "status": "operational"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
