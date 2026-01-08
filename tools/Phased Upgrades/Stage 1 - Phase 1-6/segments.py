"""
Memory Segment Definitions and Models
======================================

Defines the structure of memory packets across all L9 memory tiers.
Segments: governance_meta, project_history, tool_audit, session_context
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, field_validator, Field
import json


class MemorySegment(str, Enum):
    """L's memory organization - 4 segments."""
    
    GOVERNANCE_META = "governance_meta"          # Authority, meta-prompts (immutable)
    PROJECT_HISTORY = "project_history"          # Plans, decisions, outcomes
    TOOL_AUDIT = "tool_audit"                   # Tool invocation audit trail
    SESSION_CONTEXT = "session_context"          # Short-term working memory


class MemoryPacket(BaseModel):
    """
    Unit of memory aligned with L9's PacketEnvelope.
    
    Fields:
        chunk_id: Unique identifier (UUID)
        segment: Memory segment category
        agent_id: Owner agent
        content: Payload data
        metadata: Tags, version info
        timestamp: Creation time
        embedding: Optional vector for semantic search
        version: Conflict resolution
        expires_at: TTL for auto-cleanup
    """
    
    chunk_id: str
    segment: MemorySegment
    agent_id: str
    content: Dict[str, Any]
    metadata: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    embedding: Optional[List[float]] = None
    version: int = 1
    expires_at: Optional[datetime] = None
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v):
        """Embedding must be list of floats, 1536 dims (OpenAI)."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Embedding must be list")
            if len(v) != 1536:
                raise ValueError(f"Embedding must be 1536 dims, got {len(v)}")
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError("Embedding values must be numeric")
        return v
    
    @field_validator('expires_at')
    @classmethod
    def validate_expires_at(cls, v, values):
        """expires_at must be in future."""
        if v and 'timestamp' in values.data:
            if v <= values.data['timestamp']:
                raise ValueError("expires_at must be after timestamp")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "chunk_id": "governance_meta_2025_12_27",
                "segment": "governance_meta",
                "agent_id": "L",
                "content": {
                    "authority_chain": [
                        {"rank": 1, "entity": "Igor", "role": "CEO"},
                        {"rank": 2, "entity": "L", "role": "CTO"}
                    ]
                },
                "timestamp": "2025-12-27T10:30:00Z",
                "version": 1
            }
        }
    }
    
    def as_neo4j_dict(self) -> Dict[str, Any]:
        """Serialize for Neo4j property storage."""
        return {
            "chunk_id": self.chunk_id,
            "segment": self.segment.value,
            "agent_id": self.agent_id,
            "content_hash": hash(json.dumps(self.content, sort_keys=True)),
            "timestamp": int(self.timestamp.timestamp()),
            "version": self.version,
            "embedding_hash": hash(str(self.embedding)) if self.embedding else None,
            "expires_at": int(self.expires_at.timestamp()) if self.expires_at else None
        }
    
    def as_postgres_tuple(self) -> tuple:
        """Serialize for Postgres INSERT."""
        return (
            self.chunk_id,
            self.segment.value,
            self.agent_id,
            json.dumps(self.content),
            json.dumps(self.metadata),
            self.timestamp,
            self.embedding,
            self.version,
            self.expires_at
        )
    
    @classmethod
    def from_postgres_row(cls, row: dict) -> "MemoryPacket":
        """Deserialize from Postgres row."""
        return cls(
            chunk_id=row['chunk_id'],
            segment=MemorySegment(row['segment']),
            agent_id=row['agent_id'],
            content=json.loads(row['content']),
            metadata=json.loads(row['metadata']),
            timestamp=row['timestamp'],
            embedding=row.get('embedding'),
            version=row.get('version', 1),
            expires_at=row.get('expires_at')
        )


class MemoryError(Exception):
    """Base exception for memory operations."""
    pass


class MemoryPacketError(MemoryError):
    """Invalid memory packet."""
    pass


class MemorySegmentError(MemoryError):
    """Segment-related error."""
    pass

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "TOO-OPER-007",
    "component_name": "Segments",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "tools",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides segments components including MemorySegment, MemoryPacket, MemoryError",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
