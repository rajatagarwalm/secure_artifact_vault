import time
import uuid
from fastapi import Request
from prometheus_client import Counter, Histogram

from app.core.request_context import set_request_id

EXCLUDED_PATHS = {"/metrics", "/healthz", "/readyz"}

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["method", "path"],
)

REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total HTTP error responses",
    ["method", "path"],
)


async def observability_middleware(request: Request, call_next):
    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    set_request_id(request_id)

    start = time.time()
    status = 500

    route = request.scope.get("route")
    path = route.path if route else request.url.path

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    except Exception:
        REQUEST_ERRORS.labels(request.method, path).inc()
        raise
    finally:
        duration = time.time() - start

        REQUEST_LATENCY.labels(request.method, path).observe(duration)
        REQUEST_COUNT.labels(request.method, path, status).inc()
