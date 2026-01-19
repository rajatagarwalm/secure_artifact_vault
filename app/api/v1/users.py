from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.schemas.user import AssignOrgRequest, CreateUserRequest, ChangePasswordRequest, ResetPasswordRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    dependencies=[Depends(require_permission("user:manage"))],
)
def list_users(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = UserService(db).list_users(actor=user)

    response = []
    for u, role, org_id, org_name in rows:
        response.append(
            {
                "id": str(u.id),
                "email": u.email,
                "is_active": u.is_active,
                "role": role,
                "organization": {
                    "org_id": str(org_id),
                    "name": org_name,
                },
            }
        )

    return response


@router.post(
    "",
    dependencies=[Depends(require_permission("user:manage"))],
)
def create_user(
    payload: CreateUserRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = UserService(db).create_user(
            email=payload.email,
            password=payload.password,
            org_id=payload.org_id,
            role=payload.role,
            actor=user,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/assign-org",
    dependencies=[Depends(require_permission("user:manage"))],
)
def assign_user_to_org(
    payload: AssignOrgRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        UserService(db).assign_user_to_org(
            user_id=payload.user_id,
            org_id=payload.org_id,
            role=payload.role,
            actor=user,
        )
        return {"message": "User assigned to organization successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/{user_id}/permissions",
    dependencies=[Depends(require_permission("user:manage"))],
)
def get_user_permissions(
    user_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        permissions = UserService(db).get_user_permissions(
            user_id=user_id,
            actor=user,
        )
        return {"permissions": permissions}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

@router.post(
    "/change-password",
)
def change_password(
    payload: ChangePasswordRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Allow user to change their own password.
    User must provide current password and new password.
    """
    try:
        result = UserService(db).change_password(
            user_id=user["id"],
            old_password=payload.old_password,
            new_password=payload.new_password,
            actor=user,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/reset-password",
    dependencies=[Depends(require_permission("user:manage"))],
)
def reset_password(
    payload: ResetPasswordRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to reset a user's password.
    Only superadmin can reset passwords.
    Generates a new temporary password that expires after configured hours.
    """
    try:
        result = UserService(db).reset_password(
            user_id=payload.user_id,
            new_password=payload.new_password,
            actor=user,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )