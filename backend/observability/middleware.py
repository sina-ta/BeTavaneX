"""HTTP request observability: correlation ID, timing, operational warnings."""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("betavanx.request")
SLOW_REQUEST_MS = 1_500


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach request_id, log latency, surface slow or failed requests."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed method=%s path=%s duration_ms=%.1f",
                request.method,
                request.url.path,
                duration_ms,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "event": "request_failed",
                },
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id

        log_kwargs = {
            "extra": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "event": "request_complete",
            },
        }

        if response.status_code >= 500:
            logger.error(
                "server_error method=%s path=%s status=%s duration_ms=%.1f",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                **log_kwargs,
            )
        elif duration_ms >= SLOW_REQUEST_MS:
            logger.warning(
                "slow_request method=%s path=%s status=%s duration_ms=%.1f",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                **log_kwargs,
            )
        elif request.url.path not in {"/health", "/health/live"}:
            logger.info(
                "request method=%s path=%s status=%s duration_ms=%.1f",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                **log_kwargs,
            )

        return response
