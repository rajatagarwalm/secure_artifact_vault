from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        actor_id: str | None = None,
        org_id: str | None = None,
        resource_type: str = "system",
        resource_id: str | None = None,
        extra_data: dict | None = None,
    ):
        entry = AuditLog(
            action=action,
            actor_id=actor_id,
            org_id=org_id,
            resource_type=resource_type,
            resource_id=resource_id,
            extra_data=extra_data,
        )
        self.db.add(entry)
        self.db.commit()

    def list_logs(self, limit: int = 50, offset: int = 0):
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
