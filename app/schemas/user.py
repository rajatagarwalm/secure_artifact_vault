from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool


class AssignOrgRequest(BaseModel):
    user_id: str
    org_id: str
    role: str


class UserPermissionResponse(BaseModel):
    user_id: str
    permissions: list[str]
