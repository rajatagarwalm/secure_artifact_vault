from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.schemas.artifact import ArtifactResponse, ArtifactListResponse
from app.services.artifact_service import ArtifactService

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])

@router.post(
    "/upload",
    dependencies=[Depends(require_permission("artifact:write"))],
)
async def upload_artifact(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    artifact = await ArtifactService(db).upload_streaming(
        file=file,
        user=user,
    )

    return {
        "id": str(artifact.id),
        "filename": artifact.filename,
        "checksum": artifact.checksum,
    }

@router.get(
    "",
    response_model=ArtifactListResponse,
    dependencies=[Depends(require_permission("artifact:read"))],
)
def list_artifacts(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.get("org_id"):
        raise HTTPException(status_code=400, detail="Organization context missing")

    artifacts = ArtifactService(db).list_artifacts(user["org_id"])

    return ArtifactListResponse(
        artifacts=[
            ArtifactResponse(
                id=str(a.id),
                filename=a.filename,
                content_type=a.content_type,
                created_at=a.created_at,
            )
            for a in artifacts
        ]
    )

@router.get(
    "/search",
    response_model=ArtifactListResponse,
    dependencies=[Depends(require_permission("artifact:read"))],
)
def search_artifacts(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    artifacts = ArtifactService(db).search_artifacts_by_prefix(
        prefix=q,
        user=user,
        limit=limit,
    )

    return ArtifactListResponse(
        artifacts=[
            ArtifactResponse(
                id=str(a.id),
                filename=a.filename,
                content_type=a.content_type,
                checksum=a.checksum,
                created_at=a.created_at,
            )
            for a in artifacts
        ]
    )

@router.get("/{artifact_id}")
def download_artifact(
    artifact_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    artifact, stream = ArtifactService(db).get_download_stream(
        artifact_id=artifact_id,
        user=user,
    )

    return StreamingResponse(
        stream(),
        media_type=artifact.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{artifact.filename}"'
        },
    )

@router.delete(
    "/{artifact_id}",
    dependencies=[Depends(require_permission("artifact:write"))],
)
def delete_artifact(
    artifact_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        ArtifactService(db).delete_artifact(
            artifact_id=artifact_id,
            user_org_id=user["org_id"],
            actor_id=user["id"],
            is_superadmin="*" in user["permissions"],
        )
        return {"message": "Artifact deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))