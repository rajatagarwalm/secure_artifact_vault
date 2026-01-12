from sqlalchemy.orm import Session
from app.db.models.user_org_role import UserOrgRole


class UserOrgRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign(self, user_id: str, org_id: str, role: str):
        existing = (
            self.db.query(UserOrgRole)
            .filter(
                UserOrgRole.user_id == user_id,
                UserOrgRole.org_id == org_id,
            )
            .first()
        )

        if existing:
            # Update role
            existing.role = role
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new mapping
        record = UserOrgRole(
            user_id=user_id,
            org_id=org_id,
            role=role,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_roles_for_user(self, user_id: str):
        return (
            self.db.query(UserOrgRole)
            .filter(UserOrgRole.user_id == user_id)
            .all()
        )
