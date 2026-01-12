from sqlalchemy.orm import Session
from app.db.models.organization import Organization


class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Organization:
        org = Organization(name=name)
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def get_all(self):
        return self.db.query(Organization).filter(
            Organization.is_deleted.is_(False)
        ).all()

    def get_by_id(self, org_id: str) -> Organization | None:
        return self.db.query(Organization).filter(
            Organization.id == org_id,
            Organization.is_deleted.is_(False),
        ).first()

    def soft_delete(self, org: Organization):
        org.is_deleted = True
        self.db.commit()
