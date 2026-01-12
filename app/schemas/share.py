from pydantic import BaseModel, Field


class ShareCreateRequest(BaseModel):
    artifact_id: str
    expires_in_minutes: int = Field(
        gt=0,
        le=1440,  # max 24 hours
        description="Expiry time in minutes",
    )


class ShareResponse(BaseModel):
    share_id: str
    artifact_id: str
    expires_at: str
