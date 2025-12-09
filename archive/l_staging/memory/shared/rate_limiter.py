# l/memory/shared/rate_limiter.py

import time

class MemoryRateLimiter:
    """Simple per-process rate limiter to avoid Supabase overload."""
    MIN_INTERVAL = 0.05  # 20 writes/sec max

    def __init__(self):
        self.last_write = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_write
        if elapsed < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - elapsed)
        self.last_write = time.time()

rate_limiter = MemoryRateLimiter()

