import logging
from datetime import datetime

from sqlalchemy.orm import Session
from jose import JWTError

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
)
from app.repositories.user_repo import UserRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_org_role_repo import UserOrgRoleRepository
from app.core.permissions import resolve_permissions

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
        self.audit_repo = AuditRepository(db)
        self.role_repo = UserOrgRoleRepository(db)

    def login(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user or not user.password_hash:
            logger.warning("Invalid login attempt", extra={"email": email})
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            logger.warning("Invalid password", extra={"user_id": str(user.id)})
            raise ValueError("Invalid credentials")

        # CHECK IF PASSWORD HAS EXPIRED
        if user.password_expires_at and datetime.utcnow() > user.password_expires_at:
            logger.warning("Expired password attempt", extra={"user_id": str(user.id)})
            raise ValueError("Password has expired. Please change your password.")

        # FETCH ROLES FROM DB
        roles = self.role_repo.get_roles_for_user(str(user.id))
        role_names = [r.role for r in roles]

        # RESOLVE PERMISSIONS
        permissions = resolve_permissions(role_names)

        # EMBED PERMISSIONS IN TOKEN
        access_token = create_access_token(str(user.id), permissions)
        refresh_token, expires_at = create_refresh_token(str(user.id))

        self.refresh_repo.create(
            user_id=str(user.id),
            token_hash=hash_refresh_token(refresh_token),
            expires_at=expires_at,
        )

        self.audit_repo.log(
            action="login",
            actor_id=str(user.id),
            resource_type="share",
            org_id=None,
            resource_id=str(user.id),
            extra_data={
                
            },
        )

        return access_token, refresh_token

    def refresh(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        token_hash = hash_refresh_token(refresh_token)

        stored_token = self.refresh_repo.get_by_hash(token_hash)

        if not stored_token:
            self.refresh_repo.revoke_all_for_user(user_id)
            self.audit_repo.log(
                action="refresh_token_reuse_detected",
                actor_id=str(user_id),
                resource_type="refresh_token",
                org_id=None,
                resource_id=str(user_id),
                extra_data={}
            )
            raise ValueError("Refresh token reuse detected")

        if stored_token.expires_at < datetime.utcnow():
            raise ValueError("Refresh token expired")

        stored_token.is_revoked = True
        self.db.commit()

        # ✅ RELOAD PERMISSIONS ON REFRESH
        roles = self.role_repo.get_roles_for_user(user_id)
        role_names = [r.role for r in roles]
        permissions = resolve_permissions(role_names)

        new_access_token = create_access_token(user_id, permissions)
        new_refresh_token, expires_at = create_refresh_token(user_id)

        self.refresh_repo.create(
            user_id=user_id,
            token_hash=hash_refresh_token(new_refresh_token),
            expires_at=expires_at,
        )

        self.audit_repo.log(
            action="refresh_token_rotated",
            actor_id=str(user_id),
            resource_type="refresh_token",
            org_id=None,
            resource_id=str(user_id),
            extra_data={}
        )

        return new_access_token, new_refresh_token

    def logout(self, user_id: str):
        self.refresh_repo.revoke_all_for_user(user_id)
        self.audit_repo.log(
            action="logout",
            actor_id=str(user_id),
            resource_type="logout",
            org_id=None,
            resource_id=str(user_id),
            extra_data={}
        )
