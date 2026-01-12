import os
import logging
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.db.models.artifact import Artifact
from app.db.models.user import User
from app.db.models.user_org_role import UserOrgRole
from app.db.models.refresh_token import RefreshToken
from app.db.models.audit_log import AuditLog
from app.db.models.organization import Organization

ARTIFACT_RETENTION_DAYS = 0
AUDIT_RETENTION_DAYS = 7
SYSTEM_ORG_NAME = "SYSTEM"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] cleanup_job: %(message)s",
)

logger = logging.getLogger(__name__)


def cleanup_artifacts(db):
    logger.info("Cleaning up soft-deleted artifacts")

    artifacts = (
        db.query(Artifact)
        .filter(Artifact.is_deleted.is_(True))
        .all()
    )

    for artifact in artifacts:
        try:
            if artifact.file_path and os.path.exists(artifact.file_path):
                os.remove(artifact.file_path)
                logger.info(
                    "Deleted artifact file %s", artifact.file_path
                )
        except Exception as e:
            logger.error(
                "Failed deleting file for artifact %s: %s",
                artifact.id,
                str(e),
            )
            continue

        db.delete(artifact)

    logger.info("Artifact cleanup completed")


def cleanup_users(db):
    logger.info("Cleaning up inactive users")

    system_org = (
        db.query(Organization)
        .filter(Organization.name == SYSTEM_ORG_NAME)
        .first()
    )

    inactive_users = (
        db.query(User)
        .filter(User.is_active.is_(False))
        .all()
    )

    for user in inactive_users:
        # Protect SYSTEM superadmin
        if system_org:
            roles = (
                db.query(UserOrgRole)
                .filter(
                    UserOrgRole.user_id == user.id,
                    UserOrgRole.org_id == system_org.id,
                    UserOrgRole.role == "superadmin",
                )
                .count()
            )
            if roles > 0:
                logger.info(
                    "Skipping deletion of SYSTEM superadmin %s",
                    user.email,
                )
                continue

        # Delete refresh tokens
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id
        ).delete(synchronize_session=False)

        # Delete role mappings
        db.query(UserOrgRole).filter(
            UserOrgRole.user_id == user.id
        ).delete(synchronize_session=False)

        logger.info("Deleting inactive user %s", user.email)
        db.delete(user)

    logger.info("User cleanup completed")


def cleanup_audit_logs(db):
    logger.info("Cleaning up old audit logs")

    cutoff = datetime.utcnow() - timedelta(days=AUDIT_RETENTION_DAYS)

    deleted = (
        db.query(AuditLog)
        .filter(AuditLog.created_at < cutoff)
        .delete(synchronize_session=False)
    )

    logger.info("Deleted %d audit log records", deleted)


def run_cleanup():
    db = SessionLocal()

    try:
        logger.info("Cleanup job started")

        cleanup_artifacts(db)
        cleanup_users(db)
        cleanup_audit_logs(db)

        db.commit()
        logger.info("Cleanup job completed successfully")

    except Exception as e:
        db.rollback()
        logger.exception("Cleanup job failed: %s", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    run_cleanup()
