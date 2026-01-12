from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.schemas.audit import AuditLogListResponse, AuditLogResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_permission("*"))],  # superadmin only
)
def get_audit_logs(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    logs = AuditService(db).list_audit_logs(limit, offset)

    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=str(log.id),
                action=log.action,
                actor_id=str(log.actor_id) if log.actor_id else None,
                org_id=str(log.org_id) if log.org_id else None,
                resource_type=log.resource_type,
                resource_id=str(log.resource_id) if log.resource_id else None,
                created_at=log.created_at,
            )
            for log in logs
        ]
    )
