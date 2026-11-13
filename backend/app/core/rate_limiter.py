from collections import deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, status


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()

        with self._lock:
            expired_keys = []

            for stored_key, attempts in self._attempts.items():
                while attempts and now - attempts[0] >= self.window_seconds:
                    attempts.popleft()
                if not attempts:
                    expired_keys.append(stored_key)

            for expired_key in expired_keys:
                del self._attempts[expired_key]

            attempts = self._attempts.setdefault(key, deque())

            if len(attempts) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - attempts[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiados intentos. Intenta nuevamente más tarde.",
                    headers={"Retry-After": str(retry_after)},
                )

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._attempts.setdefault(key, deque()).append(monotonic())

    def reset_key(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._attempts.clear()
