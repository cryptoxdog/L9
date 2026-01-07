"""
Request/response models.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class SaveMemoryRequest(BaseModel):
    content: str
    kind: str
    scope: str = "user"
    duration: str
    user_id: str
    tags: Optional[List[str]] = None
    importance: Optional[float] = 1.0
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    id: int
    user_id: str
    kind: str
    content: str
    importance: float
    tags: Optional[List[str]] = None
    created_at: datetime
    similarity: Optional[float] = None


class SearchMemoryRequest(BaseModel):
    query: str
    user_id: str
    scopes: Optional[List[str]] = ["user", "project", "global"]
    kinds: Optional[List[str]] = None
    top_k: Optional[int] = 5
    threshold: Optional[float] = 0.7
    duration: Optional[str] = "all"


class SearchMemoryResponse(BaseModel):
    results: List[MemoryResponse]
    query_embedding_time_ms: float
    search_time_ms: float
    total_results: int


class MemoryStatsResponse(BaseModel):
    short_term_count: int
    medium_term_count: int
    long_term_count: int
    total_count: int
    unique_users: int
    avg_importance: float


class CompoundResult(BaseModel):
    memories_analyzed: int
    clusters_found: int
    memories_merged: int
    importance_boosted: int


# =============================================================================
# Enhanced Memory Models (10x Upgrade)
# =============================================================================


class ContextInjectionRequest(BaseModel):
    """Request for auto context injection before a task."""
    task_description: str
    user_id: str
    top_k: Optional[int] = 5
    include_recent: Optional[bool] = True  # Include last 24h context
    kinds: Optional[List[str]] = None  # Filter by memory kinds


class ContextInjectionResponse(BaseModel):
    """Context memories to inject into system prompt."""
    memories: List[MemoryResponse]
    recent_context: List[MemoryResponse]
    total_injected: int
    retrieval_time_ms: float


class SessionLearningRequest(BaseModel):
    """Request to extract learnings from a session."""
    user_id: str
    session_id: str
    session_summary: str  # What happened this session
    key_decisions: Optional[List[str]] = None
    errors_encountered: Optional[List[str]] = None
    successes: Optional[List[str]] = None


class SessionLearningResponse(BaseModel):
    """Learnings extracted and stored from session."""
    learnings_stored: int
    memory_ids: List[int]
    kinds_created: List[str]


class ProactiveRecallRequest(BaseModel):
    """Request for proactive memory suggestions based on patterns."""
    current_context: str  # What user is currently working on
    user_id: str
    include_error_fixes: Optional[bool] = True
    include_preferences: Optional[bool] = True
    top_k: Optional[int] = 3


class ProactiveRecallResponse(BaseModel):
    """Proactive suggestions surfaced from memory."""
    suggestions: List[MemoryResponse]
    error_fix_pairs: List[Dict[str, Any]]  # {error: str, fix: str, confidence: float}
    relevant_preferences: List[MemoryResponse]
    recall_time_ms: float


class TemporalQueryRequest(BaseModel):
    """Request for temporal memory queries."""
    user_id: str
    since: Optional[datetime] = None  # What changed since this time
    until: Optional[datetime] = None
    kinds: Optional[List[str]] = None
    operation: Optional[str] = "changes"  # "changes", "timeline", "diff"


class TemporalQueryResponse(BaseModel):
    """Temporal query results showing memory evolution."""
    memories: List[MemoryResponse]
    created_count: int
    updated_count: int
    deleted_count: int
    period_start: datetime
    period_end: datetime


class SaveMemoryWithConfidenceRequest(BaseModel):
    """Save memory with explicit confidence scoring."""
    content: str
    kind: str
    scope: str = "user"
    duration: str
    user_id: str
    tags: Optional[List[str]] = None
    importance: Optional[float] = 1.0
    confidence: Optional[float] = 1.0  # How confident are we in this memory
    source: Optional[str] = "cursor"  # Where did this memory come from
    related_memory_ids: Optional[List[int]] = None  # Link to related memories
    metadata: Optional[Dict[str, Any]] = None
