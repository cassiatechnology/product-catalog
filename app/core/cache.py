from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import time
import asyncio

@dataclass
class _Entry:
    value: Any
    expires_at: float

class AsyncTTLCache:
    """Simple in-memory async TTL cache with namespace-based invalidation."""
    def __init__(self) -> None:
        self._store: dict[str, _Entry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        now = time.time()
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry.expires_at < now:
                # Expired; remove lazily
                self._store.pop(key, None)
                return None
            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires_at = time.time() + ttl_seconds
        async with self._lock:
            self._store[key] = _Entry(value=value, expires_at=expires_at)

    async def invalidate(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all keys starting with prefix. Returns number of removed keys."""
        async with self._lock:
            to_delete = [k for k in self._store.keys() if k.startswith(prefix)]
            for k in to_delete:
                self._store.pop(k, None)
            return len(to_delete)

# Singleton cache instance
cache = AsyncTTLCache()

def make_key(namespace: str, **params: Any) -> str:
    """
    Build a stable cache key: <namespace>|k1=v1|k2=v2...
    Ensures order by sorting keys.
    """
    parts = [namespace]
    for k in sorted(params.keys()):
        parts.append(f"{k}={params[k]}")
    return "|".join(parts)
