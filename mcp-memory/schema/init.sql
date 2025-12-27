-- L9 MCP Memory Server Schema
-- Version: 1.0.0
-- Requires: PostgreSQL 15+ with pgvector extension

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the memory schema
CREATE SCHEMA IF NOT EXISTS memory;

-- Short-term memory (ephemeral, auto-expire)
CREATE TABLE IF NOT EXISTS memory.shortterm (
    id SERIAL PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    kind VARCHAR(50) NOT NULL CHECK (kind IN ('preference', 'fact', 'context', 'error', 'success')),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    importance FLOAT DEFAULT 1.0 CHECK (importance >= 0 AND importance <= 1),
    metadata JSONB DEFAULT '{}',
    createdat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expiresat TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Medium-term memory (hours to days)
CREATE TABLE IF NOT EXISTS memory.mediumterm (
    id SERIAL PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    kind VARCHAR(50) NOT NULL CHECK (kind IN ('preference', 'fact', 'context', 'error', 'success')),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    importance FLOAT DEFAULT 1.0 CHECK (importance >= 0 AND importance <= 1),
    metadata JSONB DEFAULT '{}',
    createdat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expiresat TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Long-term memory (persistent)
CREATE TABLE IF NOT EXISTS memory.longterm (
    id SERIAL PRIMARY KEY,
    userid VARCHAR(255) NOT NULL,
    scope VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (scope IN ('user', 'project', 'global')),
    kind VARCHAR(50) NOT NULL CHECK (kind IN ('preference', 'fact', 'context', 'error', 'success')),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    importance FLOAT DEFAULT 1.0 CHECK (importance >= 0 AND importance <= 1),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    createdat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (userid, scope, content)
);

-- Audit log for all operations
CREATE TABLE IF NOT EXISTS memory.auditlog (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL,
    tablename VARCHAR(100),
    memoryid INTEGER,
    userid VARCHAR(255),
    status VARCHAR(50) DEFAULT 'success',
    details JSONB DEFAULT '{}',
    createdat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for short-term
CREATE INDEX IF NOT EXISTS idx_shortterm_userid ON memory.shortterm(userid);
CREATE INDEX IF NOT EXISTS idx_shortterm_kind ON memory.shortterm(kind);
CREATE INDEX IF NOT EXISTS idx_shortterm_expiresat ON memory.shortterm(expiresat);
CREATE INDEX IF NOT EXISTS idx_shortterm_embedding ON memory.shortterm USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Indexes for medium-term
CREATE INDEX IF NOT EXISTS idx_mediumterm_userid ON memory.mediumterm(userid);
CREATE INDEX IF NOT EXISTS idx_mediumterm_kind ON memory.mediumterm(kind);
CREATE INDEX IF NOT EXISTS idx_mediumterm_expiresat ON memory.mediumterm(expiresat);
CREATE INDEX IF NOT EXISTS idx_mediumterm_embedding ON memory.mediumterm USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Indexes for long-term
CREATE INDEX IF NOT EXISTS idx_longterm_userid ON memory.longterm(userid);
CREATE INDEX IF NOT EXISTS idx_longterm_scope ON memory.longterm(scope);
CREATE INDEX IF NOT EXISTS idx_longterm_kind ON memory.longterm(kind);
CREATE INDEX IF NOT EXISTS idx_longterm_tags ON memory.longterm USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_longterm_embedding ON memory.longterm USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Indexes for audit log
CREATE INDEX IF NOT EXISTS idx_auditlog_operation ON memory.auditlog(operation);
CREATE INDEX IF NOT EXISTS idx_auditlog_userid ON memory.auditlog(userid);
CREATE INDEX IF NOT EXISTS idx_auditlog_createdat ON memory.auditlog(createdat);

-- Function to auto-update 'updatedat'
CREATE OR REPLACE FUNCTION memory.update_updatedat()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updatedat = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for long-term updatedat
DROP TRIGGER IF EXISTS trigger_longterm_updatedat ON memory.longterm;
CREATE TRIGGER trigger_longterm_updatedat
    BEFORE UPDATE ON memory.longterm
    FOR EACH ROW
    EXECUTE FUNCTION memory.update_updatedat();

-- Cleanup function for expired memories (callable by cron or app)
CREATE OR REPLACE FUNCTION memory.cleanup_expired()
RETURNS TABLE(shortterm_deleted INT, mediumterm_deleted INT) AS $$
DECLARE
    short_count INT;
    medium_count INT;
BEGIN
    WITH deleted_short AS (
        DELETE FROM memory.shortterm WHERE expiresat <= CURRENT_TIMESTAMP RETURNING 1
    )
    SELECT COUNT(*) INTO short_count FROM deleted_short;

    WITH deleted_medium AS (
        DELETE FROM memory.mediumterm WHERE expiresat <= CURRENT_TIMESTAMP RETURNING 1
    )
    SELECT COUNT(*) INTO medium_count FROM deleted_medium;

    shortterm_deleted := short_count;
    mediumterm_deleted := medium_count;
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

