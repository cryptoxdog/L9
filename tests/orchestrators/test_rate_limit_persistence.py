"""
Rate Limit Persistence Tests
============================

Tests for rate limit tracking in Redis.
"""

import pytest


@pytest.mark.asyncio
async def test_rate_limits(redis, tool_registry):
    """Test rate limits are tracked in Redis."""
    await redis.set("rate_limit:google:now", 5)
    count = await tool_registry.get_usage("google")
    assert count == 5


@pytest.mark.asyncio
async def test_rate_limit_increment(redis, tool_registry):
    """Test rate limit counter increments."""
    await redis.set("rate_limit:google:now", 0)

    await tool_registry.increment_usage("google")
    count = await tool_registry.get_usage("google")

    assert count == 1


@pytest.mark.asyncio
async def test_rate_limit_check_within(tool_registry):
    """Test rate limit check when within limits."""
    # google has limit of 100
    within_limit = await tool_registry.check_rate_limit("google")
    assert within_limit is True


@pytest.mark.asyncio
async def test_rate_limit_check_exceeded(redis, tool_registry):
    """Test rate limit check when exceeded."""
    # Set usage to exceed limit (100)
    await redis.set("rate_limit:google:now", 150)

    within_limit = await tool_registry.check_rate_limit("google")
    assert within_limit is False


@pytest.mark.asyncio
async def test_redis_key_persistence(redis):
    """Test Redis keys persist across operations."""
    await redis.set("test_key", "test_value")

    # Should still be there
    value = await redis.get("test_key")
    assert value == "test_value"


@pytest.mark.asyncio
async def test_redis_incr(redis):
    """Test Redis increment operation."""
    await redis.set("counter", 10)
    new_value = await redis.incr("counter")

    assert new_value == 11


@pytest.mark.asyncio
async def test_redis_decr(redis):
    """Test Redis decrement operation."""
    await redis.set("counter", 10)
    new_value = await redis.decr("counter")

    assert new_value == 9


@pytest.mark.asyncio
async def test_redis_keys_pattern(redis):
    """Test Redis keys pattern matching."""
    await redis.set("rate_limit:google:now", 5)
    await redis.set("rate_limit:openai:now", 10)
    await redis.set("other_key", 1)

    keys = await redis.keys("rate_limit:*")

    assert len(keys) == 2
    assert "rate_limit:google:now" in keys
    assert "rate_limit:openai:now" in keys
