import os
import uuid
import hashlib
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.organization import Organization
from app.db.models.user_org_role import UserOrgRole
from app.db.models.artifact import Artifact
from app.core.security import hash_password

ARTIFACT_DIR = "/app/storage/artifacts"
PASSWORD = "password123"
SYSTEM_ORG_NAME = "SYSTEM"


def get_or_create_user(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    user = User(
        email=email,
        password_hash=hash_password(PASSWORD),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_org(db: Session, name: str) -> Organization:
    org = db.query(Organization).filter(Organization.name == name).first()
    if org:
        return org

    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def assign_role_if_not_exists(
    db: Session,
    user_id,
    org_id,
    role: str,
):
    exists = (
        db.query(UserOrgRole)
        .filter(
            UserOrgRole.user_id == user_id,
            UserOrgRole.org_id == org_id,
            UserOrgRole.role == role,
        )
        .first()
    )

    if exists:
        return

    db.add(
        UserOrgRole(
            user_id=user_id,
            org_id=org_id,
            role=role,
        )
    )
    db.commit()


def create_artifact_if_not_exists(
    db: Session,
    org_id,
    owner_id,
    filename: str,
):
    existing = (
        db.query(Artifact)
        .filter(
            Artifact.org_id == org_id,
            Artifact.filename == filename,
            Artifact.is_deleted.is_(False),
        )
        .first()
    )

    if existing:
        return

    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    artifact_id = str(uuid.uuid4())
    path = f"{ARTIFACT_DIR}/{artifact_id}_{filename}"

    content = f"Seeded artifact for org {org_id}"
    with open(path, "w") as f:
        f.write(content)

    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()

    artifact = Artifact(
        id=artifact_id,
        org_id=org_id,
        owner_id=owner_id,
        filename=filename,
        content_type="text/plain",
        file_path=path,
        checksum=checksum,
    )

    db.add(artifact)
    db.commit()

def main():
    db = SessionLocal()

    try:
        print("🚀 Initializing database with seed data...")

        # SYSTEM ORG
        system_org = get_or_create_org(db, SYSTEM_ORG_NAME)

        # SUPERADMIN
        superadmin = get_or_create_user(db, "superadmin@vault.com")
        assign_role_if_not_exists(
            db=db,
            user_id=superadmin.id,
            org_id=system_org.id,
            role="superadmin",
        )

        # ORGANIZATIONS
        for i in range(1, 4):
            org = get_or_create_org(db, f"Organization-{i}")

            admin = get_or_create_user(db, f"admin{i}@org{i}.com")
            assign_role_if_not_exists(db, admin.id, org.id, "admin")

            editor = get_or_create_user(db, f"editor{i}@org{i}.com")
            assign_role_if_not_exists(db, editor.id, org.id, "editor")

            viewer = get_or_create_user(db, f"viewer{i}@org{i}.com")
            assign_role_if_not_exists(db, viewer.id, org.id, "viewer")

            create_artifact_if_not_exists(
                db=db,
                org_id=org.id,
                owner_id=admin.id,
                filename=f"org{i}_artifact.txt",
            )

        print("✅ Database seed completed successfully")

    finally:
        db.close()


if __name__ == "__main__":
    main()
