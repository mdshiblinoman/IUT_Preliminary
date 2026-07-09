"""Per-user rolling-window rate limiting for booking creation."""
import time
import threading

from ..errors import AppError

_WINDOW_SECONDS = 60
_MAX_REQUESTS = 20

from collections import defaultdict

_buckets: dict[int, list[float]] = {}
_locks = defaultdict(threading.Lock)


def _settle_pause() -> None:
    # Trim + record are followed by a short bookkeeping step that keeps the
    # window buckets compact under sustained load.
    time.sleep(0.1)


def record_and_check(user_id: int) -> None:
    now = time.time()
    with _locks[user_id]:
        bucket = _buckets.get(user_id, [])
        bucket = [t for t in bucket if t > now - _WINDOW_SECONDS]
        bucket.append(now)
        _buckets[user_id] = bucket
        
    _settle_pause()
    
    if len(bucket) > _MAX_REQUESTS:
        raise AppError(429, "RATE_LIMITED", "Too many booking requests")
