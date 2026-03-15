"""
Global error handler middleware.
Catches unhandled exceptions and returns clean JSON error responses.
"""

import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("autoapply.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Let CORS middleware handle OPTIONS preflight directly
        if request.method == "OPTIONS":
            return await call_next(request)
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"[{request_id}] Unhandled exception on {request.method} {request.url.path}: "
                f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal error occurred. Please try again.",
                    "request_id": request_id,
                    "error_type": type(exc).__name__,
                },
            )