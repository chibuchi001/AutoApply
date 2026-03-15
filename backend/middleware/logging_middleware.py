"""
Request logging middleware.
Logs every request with timing, status, and masked sensitive fields.
"""

import time
import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("autoapply.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all HTTP requests with:
    - Request ID (for tracing)
    - Method + path
    - Status code
    - Duration in ms
    """

    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Attach request ID so route handlers can reference it
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms:.1f}ms)"
        )

        # Add request ID header to response for client-side tracing
        response.headers["X-Request-ID"] = request_id
        return response
