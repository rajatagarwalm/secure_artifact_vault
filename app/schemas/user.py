from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool


class AssignOrgRequest(BaseModel):
    user_id: str
    org_id: str
    role: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    org_id: str
    role: str  # editor, viewer, admin


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    user_id: str
    new_password: str


class UserPermissionResponse(BaseModel):
    user_id: str
    permissions: list[str]
