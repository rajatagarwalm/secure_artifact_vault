from sqlalchemy.orm import Session
from app.repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditRepository(db)

    def list_audit_logs(self, limit: int, offset: int):
        return self.repo.list_logs(limit=limit, offset=offset)
