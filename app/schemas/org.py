from pydantic import BaseModel


class OrganizationCreateRequest(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: str
    name: str
    is_deleted: bool
