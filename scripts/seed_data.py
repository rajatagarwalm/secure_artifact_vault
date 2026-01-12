import os
import uuid
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.organization import Organization
from app.db.models.user_org_role import UserOrgRole
from app.db.models.artifact import Artifact
from app.core.security import hash_password

ARTIFACT_DIR = "storage/artifacts"
PASSWORD = "password123"
SYSTEM_ORG_NAME = "SYSTEM"


def create_user(db: Session, email: str):
    user = User(
        email=email,
        password_hash=hash_password(PASSWORD),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_org(db: Session, name: str):
    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def assign_role(db: Session, user_id, org_id, role):
    db.add(
        UserOrgRole(
            user_id=user_id,
            org_id=org_id,
            role=role,
        )
    )
    db.commit()


def create_artifact(db: Session, org_id, owner_id, filename):
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    artifact_id = str(uuid.uuid4())
    path = f"{ARTIFACT_DIR}/{artifact_id}_{filename}"

    with open(path, "w") as f:
        f.write(f"Seeded artifact for org {org_id}")

    artifact = Artifact(
        org_id=org_id,
        owner_id=owner_id,
        filename=filename,
        content_type="text/plain",
        file_path=path,
    )
    db.add(artifact)
    db.commit()


def main():
    db = SessionLocal()

    try:
        print("🚀 Initializing database with seed data...")

        # 1️⃣ SYSTEM ORG (for superadmin)
        system_org = create_org(db, SYSTEM_ORG_NAME)

        # 2️⃣ SUPERADMIN (ROLE-BASED, ATTACHED TO SYSTEM ORG)
        superadmin = create_user(db, "superadmin@vault.com")
        assign_role(
            db=db,
            user_id=superadmin.id,
            org_id=system_org.id,   # ✅ NOT NULL
            role="superadmin",
        )

        # 3️⃣ NORMAL ORGANIZATIONS + USERS
        for i in range(1, 4):
            org = create_org(db, f"Organization-{i}")

            # Admin
            admin = create_user(db, f"admin{i}@org{i}.com")
            assign_role(db, admin.id, org.id, "admin")

            # Editor
            editor = create_user(db, f"editor{i}@org{i}.com")
            assign_role(db, editor.id, org.id, "editor")

            # Viewer
            viewer = create_user(db, f"viewer{i}@org{i}.com")
            assign_role(db, viewer.id, org.id, "viewer")

            # One artifact per org
            create_artifact(
                db=db,
                org_id=org.id,
                owner_id=admin.id,
                filename=f"org{i}_artifact.txt",
            )

        print("✅ Database initialized successfully")

    finally:
        db.close()


if __name__ == "__main__":
    main()
