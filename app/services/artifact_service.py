import os
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.repositories.artifact_repo import ArtifactRepository
from app.repositories.audit_repo import AuditRepository

ARTIFACT_STORAGE_PATH = "./storage/artifacts"


class ArtifactService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ArtifactRepository(db)
        self.audit = AuditRepository(db)

    def upload(
        self,
        org_id: str,
        owner_id: str,
        file: UploadFile,
    ):
        os.makedirs(ARTIFACT_STORAGE_PATH, exist_ok=True)

        artifact_id = str(uuid.uuid4())
        file_path = f"{ARTIFACT_STORAGE_PATH}/{artifact_id}_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        artifact = self.repo.create(
            org_id=org_id,
            owner_id=owner_id,
            filename=file.filename,
            content_type=file.content_type,
            file_path=file_path,
        )

        self.audit.log(
            action="artifact_uploaded",
            actor_id=owner_id,
            org_id=org_id,
            resource_type="artifact",
            resource_id=str(artifact.id),
        )

        return artifact

    # 🔒 CENTRALIZED ORG CHECK
    def get_artifact(
        self,
        artifact_id: str,
        user_org_id: str,
        is_superadmin: bool,
    ):
        artifact = self.repo.get_by_id(artifact_id)
        if not artifact:
            raise ValueError("Artifact not found")

        if not is_superadmin and str(artifact.org_id) != user_org_id:
            raise ValueError("Cross-org access denied")

        return artifact

    def list_artifacts(self, org_id: str):
        return self.repo.list_by_org(org_id)

    def delete_artifact(
        self,
        artifact_id: str,
        user_org_id: str,
        actor_id: str,
        is_superadmin: bool,
    ):
        artifact = self.get_artifact(
            artifact_id=artifact_id,
            user_org_id=user_org_id,
            is_superadmin=is_superadmin,
        )

        self.repo.soft_delete(artifact)

        self.audit.log(
            action="artifact_deleted",
            actor_id=actor_id,
            org_id=str(artifact.org_id),
            resource_type="artifact",
            resource_id=str(artifact.id),
        )
