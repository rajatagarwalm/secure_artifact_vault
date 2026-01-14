from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ArtifactResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    checksum: str
    created_at: datetime

    class Config:
        from_attributes = True 


class ArtifactListResponse(BaseModel):
    artifacts: list[ArtifactResponse]
