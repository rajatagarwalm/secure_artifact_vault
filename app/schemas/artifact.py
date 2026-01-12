from pydantic import BaseModel
from datetime import datetime


class ArtifactResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    created_at: datetime


class ArtifactListResponse(BaseModel):
    artifacts: list[ArtifactResponse]
