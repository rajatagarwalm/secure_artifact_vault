from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.schemas.share import ShareCreateRequest, ShareResponse
from app.services.share_service import ShareService

router = APIRouter(prefix="/shares", tags=["Shares"])


@router.post(
    "",
    response_model=ShareResponse,
    dependencies=[Depends(require_permission("artifact:read"))],
)
def create_share(
    payload: ShareCreateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        share = ShareService(db).create_share(
            artifact_id=payload.artifact_id,
            actor_id=user["id"],
            expires_in_minutes=payload.expires_in_minutes,
        )
        return ShareResponse(
            share_id=str(share.id),
            artifact_id=str(share.artifact_id),
            expires_at=share.expires_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{share_id}/download")
def download_shared_artifact(
    share_id: str,
    db: Session = Depends(get_db),
):
    try:
        artifact = ShareService(db).access_share(share_id)

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
