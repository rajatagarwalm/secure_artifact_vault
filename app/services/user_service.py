from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.repositories.user_org_role_repo import UserOrgRoleRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.password_history_repo import PasswordHistoryRepository
from app.core.permissions import resolve_permissions
from app.core.security import hash_password, verify_password
from app.core.config import settings


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = UserOrgRoleRepository(db)
        self.audit = AuditRepository(db)
        self.password_history = PasswordHistoryRepository(db)

    def list_users(self, actor: dict):
        """
        Superadmin -> all users with roles + org
        Admin      -> only own org users
        """
        if "*" in actor["permissions"]:
            return self.user_repo.get_all_with_roles()

        return self.user_repo.get_users_by_org_with_roles(actor["org_id"])

    def create_user(
        self,
        email: str,
        password: str,
        org_id: str,
        role: str,
        actor: dict,
    ):
        """
        Create a new user and assign to organization with specified role.
        Only superadmin can create users.
        Password expires after TEMP_PASSWORD_VALIDITY_HOURS.
        """
        if "*" not in actor["permissions"]:
            raise ValueError("Only superadmin can create users")

        # Check if user already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Create user with hashed password
        password_hash = hash_password(password)
        password_expires_at = datetime.utcnow() + timedelta(
            hours=settings.TEMP_PASSWORD_VALIDITY_HOURS
        )
        
        user = self.user_repo.create(
            email=email, 
            password_hash=password_hash,
            password_expires_at=password_expires_at
        )

        # Record in password history
        self.password_history.create(str(user.id), password_hash)

        # Assign user to organization with role
        mapping = self.role_repo.assign(str(user.id), org_id, role)

        # Log the action
        self.audit.log(
            action="user_created",
            actor_id=actor["id"],
            org_id=org_id,
            resource_type="user",
            resource_id=str(user.id),
            extra_data={
                "email": email,
                "role": role,
                "password_expires_at": password_expires_at.isoformat(),
            },
        )

        return {
            "id": str(user.id),
            "email": user.email,
            "message": "User created successfully",
            "password_expires_at": password_expires_at.isoformat(),
        }

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
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
        actor: dict,
    ):
        """
        Allow user to change their own password.
        Validates old password before allowing change.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Only user can change their own password
        if str(user.id) != actor["id"]:
            raise ValueError("You can only change your own password")

        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Incorrect current password")

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update user password and clear expiration (password is now permanent)
        user.password_hash = new_password_hash
        user.password_expires_at = None
        self.db.commit()

        # Record in password history
        self.password_history.create(user_id, new_password_hash)

        # Log the action
        self.audit.log(
            action="password_changed",
            actor_id=actor["id"],
            org_id=actor.get("org_id"),
            resource_type="user",
            resource_id=user_id,
            extra_data={"email": user.email},
        )

        return {"message": "Password changed successfully"}

    def reset_password(
        self,
        user_id: str,
        new_password: str,
        actor: dict,
    ):
        """
        Admin or superadmin can reset user's password.
        New temporary password expires after configured hours.
        """
        # Only superadmin can reset passwords
        if "*" not in actor["permissions"]:
            raise ValueError("Only superadmin can reset user passwords")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Hash new password
        new_password_hash = hash_password(new_password)
        password_expires_at = datetime.utcnow() + timedelta(
            hours=settings.TEMP_PASSWORD_VALIDITY_HOURS
        )

        # Update user password with expiration
        user.password_hash = new_password_hash
        user.password_expires_at = password_expires_at
        self.db.commit()

        # Record in password history
        self.password_history.create(user_id, new_password_hash)

        # Log the action
        self.audit.log(
            action="password_reset",
            actor_id=actor["id"],
            org_id=actor.get("org_id"),
            resource_type="user",
            resource_id=user_id,
            extra_data={
                "email": user.email,
                "password_expires_at": password_expires_at.isoformat(),
            },
        )

        return {
            "id": str(user.id),
            "email": user.email,
            "message": "Password reset successfully",
            "password_expires_at": password_expires_at.isoformat(),
        }

    def is_password_expired(self, user_id: str) -> bool:
        """Check if user's password has expired."""
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.password_expires_at:
            return False

        return datetime.utcnow() > user.password_expires_at