from sqlalchemy.orm import Session
from app.db.models.artifact import Artifact


class ArtifactRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        org_id: str,
        owner_id: str,
        filename: str,
        content_type: str,
        file_path: str,
    ) -> Artifact:
        artifact = Artifact(
            org_id=org_id,
            owner_id=owner_id,
            filename=filename,
            content_type=content_type,
            file_path=file_path,
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        return artifact

    def list_by_org(self, org_id: str):
        return (
            self.db.query(Artifact)
            .filter(
                Artifact.org_id == org_id,
                Artifact.is_deleted.is_(False),
            )
            .all()
        )

    def get_by_id(self, artifact_id: str) -> Artifact | None:
        return (
            self.db.query(Artifact)
            .filter(
                Artifact.id == artifact_id,
                Artifact.is_deleted.is_(False),
            )
            .first()
        )

    def soft_delete(self, artifact: Artifact):
        artifact.is_deleted = True
        self.db.commit()

    def search_by_prefix(
        self,
        *,
        org_id: str,
        prefix: str,
        limit: int = 20,
    ):
        return (
            self.db.query(Artifact)
            .filter(
                Artifact.org_id == org_id,
                Artifact.is_deleted.is_(False),
                Artifact.filename.ilike(f"{prefix}%"),
            )
            .order_by(Artifact.filename)
            .limit(limit)
            .all()
        )

