# rate_limit_mw.py
import os, time, asyncio
from collections import defaultdict, deque
from typing import Iterable, Optional, Set

class IPRateLimitMiddleware:
    def __init__(self, app,
                 limit: int = 5,
                 window_sec: int = 60,
                 block_sec: int = 600,
                 paths: Optional[Iterable[str]] = None):
        self.app = app
        self.limit = limit
        self.window = window_sec
        self.block = block_sec
        self.paths: Set[str] = set(paths or [])
        self._hits = defaultdict(deque)          # ip -> deque[timestamps]
        self._blocked_until: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path") or ""
        if self.paths and path not in self.paths:
            return await self.app(scope, receive, send)

        # get client IP (Heroku: use X-Forwarded-For)
        xff = None
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                xff = value.decode()
                break
        ip = (xff.split(",")[0].strip() if xff else (scope.get("client")[0] if scope.get("client") else "unknown"))

        now = time.time()
        async with self._lock:
            # still blocked?
            until = self._blocked_until.get(ip)
            if until and now < until:
                return await self._send_429(send, max(1, int(until - now)))

            # sliding window
            q = self._hits[ip]
            cutoff = now - self.window
            while q and q[0] <= cutoff:
                q.popleft()

            if len(q) >= self.limit:
                self._blocked_until[ip] = now + self.block
                return await self._send_429(send, self.block)

            q.append(now)

        # pass through to route (OpenAI code won’t run if we returned above)
        return await self.app(scope, receive, send)

    async def _send_429(self, send, retry_after: int):
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", str(retry_after).encode()),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"detail":"Too many requests. You are temporarily blocked."}',
        })
