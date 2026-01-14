from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.permissions import has_permission
from app.db.session import SessionLocal
from app.core.security import decode_token
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_repo import UserRepository
from app.db.models.user_org_role import UserOrgRole

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    permissions = payload.get("permissions", [])

    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    roles = (
        db.query(UserOrgRole)
        .filter(UserOrgRole.user_id == user_id)
        .all()
    )

    org_id = str(roles[0].org_id) if roles else None

    return {
        "id": str(user.id),
        "email": user.email,
        "permissions": permissions,
        "org_id": org_id,
    }


def require_permission(permission: str):
    def checker(
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not has_permission(user["permissions"], permission):
            AuditRepository(db).log(
                action="share_accessed",
                resource_type="share",
                actor_id=user["id"],
                org_id=user["org_id"],
                resource_id=str(user["id"]),
                extra_data={"required": permission},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return checker
