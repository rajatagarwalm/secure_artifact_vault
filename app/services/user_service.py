from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.repositories.user_org_role_repo import UserOrgRoleRepository
from app.repositories.audit_repo import AuditRepository
from app.core.permissions import resolve_permissions


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = UserOrgRoleRepository(db)
        self.audit = AuditRepository(db)

    def list_users(self, actor: dict):
        """
        Superadmin -> all users with roles + org
        Admin      -> only own org users
        """
        if "*" in actor["permissions"]:
            return self.user_repo.get_all_with_roles()

        return self.user_repo.get_users_by_org_with_roles(actor["org_id"])

    def assign_user_to_org(
        self,
        user_id: str,
        org_id: str,
        role: str,
        actor: dict,
    ):
        if "*" not in actor["permissions"]:
            if actor["org_id"] != org_id:
                raise ValueError("Admin cannot manage users of another organization")

        mapping = self.role_repo.assign(user_id, org_id, role)

        self.audit.log(
            action="user_role_assigned",
            actor_id=actor["id"],
            org_id=org_id,
            resource_type="user_org_role",
            resource_id=str(mapping.id),
            extra_data={
                "user_id": user_id,
                "role": role,
            },
        )

        return mapping

    def get_user_permissions(self, user_id: str, actor: dict):
        if "*" not in actor["permissions"]:
            roles = self.role_repo.get_roles_for_user(user_id)
            if not roles or str(roles[0].org_id) != actor["org_id"]:
                raise ValueError("Access denied to user permissions")

        roles = self.role_repo.get_roles_for_user(user_id)
        role_names = [r.role for r in roles]
        return resolve_permissions(role_names)
