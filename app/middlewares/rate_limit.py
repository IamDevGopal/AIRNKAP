from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class _InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = monotonic()
        window_start = now - self.window_seconds
        with self._lock:
            timestamps = self._requests[key]
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            if len(timestamps) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
                return False, retry_after

            timestamps.append(now)
            return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        limit: int,
        window_seconds: int,
        skip_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = _InMemoryRateLimiter(limit=limit, window_seconds=window_seconds)
        self._skip_paths = skip_paths or {"/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path not in self._skip_paths:
            client_ip = request.client.host if request.client else "unknown"
            allowed, retry_after = self._limiter.allow(client_ip)
            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "error": {
                            "code": "rate_limit_exceeded",
                            "message": "Too many requests. Please retry later.",
                        }
                    },
                )

        response: Response = await call_next(request)
        return response
