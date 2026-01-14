from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        action: str,
        resource_type: str,
        actor_id: Optional[str] = None,
        org_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        extra_data: Optional[Dict] = None,
    ) -> None:
        audit = AuditLog(
            action=action,
            resource_type=resource_type,
            actor_id=actor_id,
            org_id=org_id,
            resource_id=resource_id,
            extra_data=extra_data,
        )

        self.db.add(audit)
        self.db.commit()

    def list_logs(self, limit: int = 50, offset: int = 0):
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
