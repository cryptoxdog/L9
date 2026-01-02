# l/memory/shared/locks.py

import asyncio
from contextlib import asynccontextmanager

_locks = {}


def get_lock(name: str):
    if name not in _locks:
        _locks[name] = asyncio.Lock()
    return _locks[name]


@asynccontextmanager
async def memory_lock(table: str):
    lock = get_lock(table)
    await lock.acquire()
    try:
        yield
    finally:
        lock.release()
