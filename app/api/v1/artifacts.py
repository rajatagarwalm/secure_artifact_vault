from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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
    response_model=ArtifactResponse,
    dependencies=[Depends(require_permission("artifact:write"))],
)
def upload_artifact(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.get("org_id"):
        raise HTTPException(status_code=400, detail="Organization context missing")

    artifact = ArtifactService(db).upload(
        org_id=user["org_id"],
        owner_id=user["id"],
        file=file,
    )

    return ArtifactResponse(
        id=str(artifact.id),
        filename=artifact.filename,
        content_type=artifact.content_type,
        created_at=artifact.created_at,
    )


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
    "/{artifact_id}",
    dependencies=[Depends(require_permission("artifact:read"))],
)
def download_artifact(
    artifact_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        artifact = ArtifactService(db).get_artifact(
            artifact_id=artifact_id,
            user_org_id=user["org_id"],
            is_superadmin="*" in user["permissions"],
        )

        def file_iterator():
            with open(artifact.file_path, "rb") as f:
                yield from f

        return StreamingResponse(
            file_iterator(),
            media_type=artifact.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{artifact.filename}"'
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
