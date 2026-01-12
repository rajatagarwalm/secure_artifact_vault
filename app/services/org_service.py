from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.org_repo import OrganizationRepository
from app.repositories.audit_repo import AuditRepository
from db.models.artifact import Artifact
from db.models.organization import Organization
from app.db.models.user import User
from db.models.share import Share
from db.models.user_org_role import UserOrgRole


class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrganizationRepository(db)
        self.audit = AuditRepository(db)

    def create_org(self, name: str, actor_id: str):
        org = self.repo.create(name)
        self.audit.log(
            action="org_created",
            actor_id=actor_id,
            resource_type="organization",
            resource_id=str(org.id),
        )
        return org

    def delete_org(self, org_id: str, actor: dict):
        """
        SUPERADMIN ONLY

        Cascade:
        - Soft delete organization
        - Deactivate users
        - Soft delete artifacts
        - Invalidate shares
        - Audit everything
        """

        now = datetime.utcnow()

        org = (
            self.db.query(Organization)
            .filter(
                Organization.id == org_id,
                Organization.is_deleted.is_(False),
            )
            .first()
        )

        if not org:
            raise ValueError("Organization not found or already deleted")

        # 1️⃣ Soft delete organization
        org.is_deleted = True
        org.deleted_at = now

        self.audit.log(
            action="org_soft_deleted",
            actor_id=actor["id"],
            org_id=org.id,
            resource_type="organization",
            resource_id=str(org.id),
        )

        # 2️⃣ Deactivate users of org
        users = (
            self.db.query(User)
            .join(UserOrgRole, User.id == UserOrgRole.user_id)
            .filter(UserOrgRole.org_id == org.id)
            .all()
        )

        for user in users:
            user.is_active = False

            self.audit.log(
                action="user_deactivated",
                actor_id=actor["id"],
                org_id=org.id,
                resource_type="user",
                resource_id=str(user.id),
                extra_data={"email": user.email},
            )

        # 3️⃣ Soft delete artifacts
        artifacts = (
            self.db.query(Artifact)
            .filter(
                Artifact.org_id == org.id,
                Artifact.is_deleted.is_(False),
            )
            .all()
        )

        for artifact in artifacts:
            artifact.is_deleted = True
            artifact.deleted_at = now

            self.audit.log(
                action="artifact_soft_deleted",
                actor_id=actor["id"],
                org_id=org.id,
                resource_type="artifact",
                resource_id=str(artifact.id),
                extra_data={"filename": artifact.filename},
            )

        # 4️⃣ Invalidate share links
        shares = (
            self.db.query(Share)
            .filter(
                Share.org_id == org.id,
                Share.is_active.is_(True),
            )
            .all()
        )

        for share in shares:
            share.is_active = False

            self.audit.log(
                action="share_revoked",
                actor_id=actor["id"],
                org_id=org.id,
                resource_type="share",
                resource_id=str(share.id),
            )

        self.db.commit()