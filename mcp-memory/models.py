from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SaveMemoryRequest(BaseModel):
    content: str
    kind: str  # preference, fact, context, error, success
    scope: str = "user"  # user, project, global
    duration: str  # short, medium, long
    userid: str
    tags: Optional[List[str]] = None
    importance: Optional[float] = 1.0
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    id: int
    userid: str
    kind: str
    content: str
    importance: float
    tags: Optional[List[str]] = None
    created_at: datetime
    similarity: Optional[float] = None


class SearchMemoryRequest(BaseModel):
    query: str
    userid: str
    scopes: Optional[List[str]] = ["user", "project", "global"]
    kinds: Optional[List[str]] = None
    topk: Optional[int] = 5
    threshold: Optional[float] = 0.7
    duration: Optional[str] = "all"  # short, medium, long, all


class SearchMemoryResponse(BaseModel):
    results: List[MemoryResponse]
    query_embedding_time_ms: float
    search_time_ms: float
    total_results: int


class MemoryStatsResponse(BaseModel):
    shortterm_count: int
    mediumterm_count: int
    longterm_count: int
    total_count: int
    unique_users: int
    avg_importance: float

