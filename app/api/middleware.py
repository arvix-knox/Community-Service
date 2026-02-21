"""Middleware — JWT, логирование запросов."""
from __future__ import annotations
import time
import uuid as uuid_mod

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.core.security import extract_user_from_token

logger = get_logger(__name__)

PUBLIC_PATHS = {"/health", "/api/docs", "/api/redoc", "/api/openapi.json"}


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                user = extract_user_from_token(token)
                request.state.user = user
            except Exception:
                request.state.user = None
        else:
            request.state.user = None

        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid_mod.uuid4()))
        request.state.request_id = request_id

        start_time = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code}",
            extra={
                "request_id": request_id, "method": request.method, "path": request.url.path,
                "status_code": response.status_code, "duration_ms": duration_ms,
                "user_id": str(getattr(getattr(request.state, "user", None), "user_id", "anonymous")),
            },
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response
