from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.repositories.share_repo import ShareRepository
from app.repositories.artifact_repo import ArtifactRepository
from app.repositories.audit_repo import AuditRepository


class ShareService:
    def __init__(self, db: Session):
        self.db = db
        self.share_repo = ShareRepository(db)
        self.artifact_repo = ArtifactRepository(db)
        self.audit = AuditRepository(db)

    def create_share(
        self,
        artifact_id: str,
        actor_id: str,
        expires_in_minutes: int,
    ):
        artifact = self.artifact_repo.get_by_id(artifact_id)
        if not artifact:
            raise ValueError("Artifact not found")

        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

        share = self.share_repo.create(
            artifact_id=artifact_id,
            created_by=actor_id,
            expires_at=expires_at,
        )

        self.audit.log(
            action="artifact_shared",
            actor_id=actor_id,
            org_id=str(artifact.org_id),
            resource_type="share",
            resource_id=str(share.id),
            extra_data={
                "artifact_id": artifact_id,
                "expires_in_minutes": expires_in_minutes,
            },
        )

        return share

    def access_share(self, share_id: str):
        share = self.share_repo.get_valid_share(share_id)
        if not share:
            raise ValueError("Share link expired or invalid")

        artifact = self.artifact_repo.get_by_id(str(share.artifact_id))
        if not artifact:
            raise ValueError("Artifact not found")

        self.audit.log(
            action="share_accessed",
            actor_id=None,
            org_id=str(artifact.org_id),
            resource_type="share",
            resource_id=str(share.id),
        )

        return artifact
