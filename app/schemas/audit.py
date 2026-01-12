from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    action: str
    actor_id: str | None
    org_id: str | None
    resource_type: str
    resource_id: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
