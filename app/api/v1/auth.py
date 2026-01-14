import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserMeResponse,
)
from app.services.auth_service import AuthService
from app.core.rate_limiter import check_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        rate_key = f"{request.client.host}:{payload.email}"

        if not check_rate_limit(rate_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Try again later.",
            )
        access, refresh = AuthService(db).login(
            payload.email,
            payload.password,
        )
        return TokenResponse(access_token=access, refresh_token=refresh)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        access, refresh = AuthService(db).refresh(payload.refresh_token)
        return TokenResponse(access_token=access, refresh_token=refresh)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
def logout(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).logout(user["id"])
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserMeResponse)
def me(user=Depends(get_current_user)):
    return UserMeResponse(
        id=user["id"],
        email=user["email"],
        permissions=user["permissions"],
    )


@router.get("/permissions")
def permissions(user=Depends(get_current_user)):
    return {"permissions": user["permissions"]}
