from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import configure_logging

import app.db.models

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.orgs import router as orgs_router
from app.api.v1.artifacts import router as artifacts_router
from app.api.v1.shares import router as shares_router
from app.api.v1.audit import router as audit_router
from app.api.metrics import router as metrics_router
from app.middleware.observability import observability_middleware

configure_logging()

app = FastAPI(title="Secure Artifact Vault")

# Middleware
app.add_middleware(
    BaseHTTPMiddleware,
    dispatch=observability_middleware,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orgs_router)
app.include_router(artifacts_router)
app.include_router(shares_router)
app.include_router(audit_router)
app.include_router(metrics_router)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/readyz")
def readiness_check():
    return {"status": "ready"}
