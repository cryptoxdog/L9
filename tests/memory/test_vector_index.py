"""
Vector Index Tests
==================

Tests for vector index configuration and type.
"""


def test_index_type(postgres_cursor):
    """Test that vector index uses IVFFlat (not HNSW)."""
    postgres_cursor.execute(
        "SELECT indexdef FROM pg_indexes WHERE indexname LIKE '%memory_vectors_idx%'"
    )
    idx = postgres_cursor.fetchone()[0]
    assert "ivfflat" in idx.lower()  # no HNSW allowed


def test_index_exists(postgres_cursor):
    """Test that vector index definition is returned."""
    postgres_cursor.execute(
        "SELECT indexdef FROM pg_indexes WHERE indexname LIKE '%memory_vectors_idx%'"
    )
    result = postgres_cursor.fetchone()
    
    assert result is not None
    assert result[0]  # Has content


def test_index_uses_cosine_ops(postgres_cursor):
    """Test that index uses cosine distance operations."""
    postgres_cursor.execute(
        "SELECT indexdef FROM pg_indexes WHERE indexname LIKE '%memory_vectors_idx%'"
    )
    idx = postgres_cursor.fetchone()[0]
    
    assert "cosine" in idx.lower()


def test_cursor_fetchall(postgres_cursor):
    """Test cursor fetchall returns list."""
    postgres_cursor.execute(
        "SELECT indexdef FROM pg_indexes WHERE indexname LIKE '%memory_vectors_idx%'"
    )
    results = postgres_cursor.fetchall()
    
    assert isinstance(results, list)


def test_cursor_empty_query(postgres_cursor):
    """Test cursor handles queries with no results."""
    postgres_cursor.execute("SELECT * FROM nonexistent_table")
    result = postgres_cursor.fetchone()
    
    assert result is None

