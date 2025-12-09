# l/memory/shared/concurrency_manager.py

import threading
from contextlib import contextmanager
from typing import Dict

class ConcurrencyManager:
    """Manages locks for concurrent memory operations."""
    
    def __init__(self):
        self._locks: Dict[str, threading.Lock] = {}
        self._lock_registry = threading.Lock()
    
    def _get_lock(self, key: str) -> threading.Lock:
        """Get or create a lock for the given key."""
        with self._lock_registry:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]
    
    @contextmanager
    def lock(self, key: str):
        """
        Context manager for acquiring a lock.
        
        Usage:
            with concurrency.lock("table_name"):
                # critical section
                pass
        """
        lock = self._get_lock(key)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()

concurrency = ConcurrencyManager()
