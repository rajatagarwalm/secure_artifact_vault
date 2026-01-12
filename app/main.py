from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging

# Load models at startup
import app.db.models  # noqa: F401

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.orgs import router as orgs_router
from app.api.v1.artifacts import router as artifacts_router
from app.api.v1.shares import router as shares_router
from app.api.v1.audit import router as audit_router




setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orgs_router)
app.include_router(artifacts_router)
app.include_router(shares_router)
app.include_router(audit_router)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/readyz")
def readiness_check():
    return {"status": "ready"}
