import hashlib
import os
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status

from app.repositories.artifact_repo import ArtifactRepository
from app.repositories.audit_repo import AuditRepository
from app.db.models.artifact import Artifact
from app.core.config import settings

ARTIFACT_STORAGE_PATH = "./storage/artifacts"
CHUNK_SIZE = 1024 * 1024  # 1 MB

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
    "application/zip",
}

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class ArtifactService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ArtifactRepository(db)
        self.audit = AuditRepository(db)

    async def upload_streaming(
        self,
        file: UploadFile,
        user: dict,
    ):
        """
        Stream upload in fixed-size chunks.
        - Constant memory usage
        - Content-type allowlist
        - File size enforcement
        - SHA-256 checksum
        """

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported content type: {file.content_type}",
            )

        os.makedirs(ARTIFACT_STORAGE_PATH, exist_ok=True)

        artifact_id = str(uuid.uuid4())
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(
            ARTIFACT_STORAGE_PATH, f"{artifact_id}_{safe_filename}"
        )

        sha256 = hashlib.sha256()
        total_bytes = 0

        try:
            with open(file_path, "wb") as out:
                while True:
                    chunk = await file.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    total_bytes += len(chunk)

                    if total_bytes > MAX_UPLOAD_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="File size limit exceeded",
                        )

                    out.write(chunk)
                    sha256.update(chunk)

        except HTTPException:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {str(e)}",
            )

        finally:
            await file.close()

        artifact = Artifact(
            id=artifact_id,
            org_id=user["org_id"],
            owner_id=user["id"],
            filename=safe_filename,
            content_type=file.content_type,
            file_path=file_path,
            checksum=sha256.hexdigest(),
            is_deleted=False,
        )

        self.db.add(artifact)
        self.db.commit()

        # -------------------------
        # Audit log
        # -------------------------
        self.audit.log(
            action="artifact_upload",
            resource_type="artifact",
            actor_id=user["id"],
            org_id=user["org_id"],
            resource_id=artifact.id,
            extra_data={
                "filename": safe_filename,
                "content_type": file.content_type,
                "size_bytes": total_bytes
            },
        )

        return artifact

    def get_download_stream(self, artifact_id: str, user: dict):
        """
        Verify checksum before streaming download.
        Enforces org-level access control.
        """

        artifact = (
            self.db.query(Artifact)
            .filter(
                Artifact.id == artifact_id,
                Artifact.is_deleted.is_(False),
                Artifact.org_id == user["org_id"],
            )
            .first()
        )

        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact not found",
            )

        if not os.path.exists(artifact.file_path):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Artifact file missing from storage",
            )

        sha256 = hashlib.sha256()
        with open(artifact.file_path, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256.update(chunk)

        if sha256.hexdigest() != artifact.checksum:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File integrity check failed",
            )

        def stream():
            with open(artifact.file_path, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    yield chunk

        self.audit.log(
            action="artifact_download",
            resource_type="artifact",
            actor_id=user["id"],
            org_id=user["org_id"],
            resource_id=artifact.id,
            extra_data={
                "filename": artifact.filename,
                "content_type": artifact.content_type,
            },
        )
        return artifact, stream

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
    
    def search_artifacts_by_prefix(
        self,
        *,
        prefix: str,
        user: dict,
        limit: int = 20,
    ):
        if not prefix or len(prefix) < 2:
            raise ValueError("Prefix must be at least 2 characters")

        return self.repo.search_by_prefix(
            org_id=user["org_id"],
            prefix=prefix,
            limit=limit,
        )

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

