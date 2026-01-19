from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.user_org_role import UserOrgRole
from app.db.models.organization import Organization


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_all_with_roles(self):
        """
        Used by superadmin
        """
        return (
            self.db.query(
                User,
                UserOrgRole.role,
                Organization.id.label("org_id"),
                Organization.name.label("org_name"),
            )
            .join(UserOrgRole, User.id == UserOrgRole.user_id)
            .join(Organization, Organization.id == UserOrgRole.org_id)
            .all()
        )

    def get_users_by_org_with_roles(self, org_id: str):
        """
        Used by org admin
        """
        return (
            self.db.query(
                User,
                UserOrgRole.role,
                Organization.id.label("org_id"),
                Organization.name.label("org_name"),
            )
            .join(UserOrgRole, User.id == UserOrgRole.user_id)
            .join(Organization, Organization.id == UserOrgRole.org_id)
            .filter(UserOrgRole.org_id == org_id)
            .all()
        )

def create(self, email: str, password_hash: str, password_expires_at=None):
        user = User(
            email=email,
            password_hash=password_hash,
            password_expires_at=password_expires_at,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
