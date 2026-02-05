"""
Distributed Locking Mechanism

Uses Redis to implement distributed locks, preventing race conditions
when multiple workers try to process the same job update simultaneously.
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import LockError, ConnectionError, TimeoutError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("locking")

_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get or create singleton Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
    return _redis_client


async def close_redis():
    """Close Redis connection. Call on app shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


@asynccontextmanager
async def distributed_lock(
    key: str,
    timeout: int = 300,  # 5 minutes max lock duration (safety valve)
    blocking_timeout: int = 5,  # Wait up to 5s for lock
):
    """
    Acquire a distributed lock for the given key.

    Usage:
        async with distributed_lock(f"job:{job_id}"):
            await process_job(job_id)

    Args:
        key: Unique lock identifier
        timeout: Auto-expiry in seconds (prevents deadlocks if worker crashes)
        blocking_timeout: How long to wait to acquire lock

    Raises:
        LockError: If lock cannot be acquired
    """
    try:
        redis = await get_redis()
    except (ConnectionError, OSError) as e:
        logger.warning(f"Redis unavailable, skipping lock for {key}: {e}")
        # If Redis is down, we can either fail or proceed without locking.
        # For a critical safety system, we might fail.
        # For this MVP, we'll log and proceed (risking race conditions but keeping availability).
        yield
        return

    lock_id = str(uuid.uuid4())
    lock_key = f"lock:{key}"
    acquired = False

    try:
        try:
            # 1. Try to acquire
            logger.debug(f"Acquiring lock {lock_key}...")

            # Fast path: try once
            acquired = await redis.set(lock_key, lock_id, nx=True, ex=timeout)

            # Slow path: poll if allowed
            if not acquired and blocking_timeout > 0:
                start_time = asyncio.get_event_loop().time()
                while not acquired:
                    if asyncio.get_event_loop().time() - start_time > blocking_timeout:
                        break
                    await asyncio.sleep(0.1)
                    acquired = await redis.set(lock_key, lock_id, nx=True, ex=timeout)
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(
                f"Redis unavailable during lock acquisition, skipping lock for {key}: {e}"
            )
            yield
            return

        if not acquired:
            raise LockError(
                f"Could not acquire lock {lock_key} after {blocking_timeout}s"
            )

        logger.debug(f"Lock acquired: {lock_key}")
        yield

    finally:
        # 2. Key release (Lua script for atomicity)
        if acquired:
            try:
                # Only delete if WE hold the lock (value matches lock_id)
                script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                await redis.eval(script, 1, lock_key, lock_id)
                logger.debug(f"Lock released: {lock_key}")
            except Exception as e:
                logger.error(f"Error releasing lock {lock_key}: {e}")
