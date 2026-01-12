from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models.share import Share


class ShareRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        artifact_id: str,
        created_by: str,
        expires_at: datetime,
    ) -> Share:
        share = Share(
            artifact_id=artifact_id,
            created_by=created_by,
            expires_at=expires_at,
        )
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    def get_valid_share(self, share_id: str) -> Share | None:
        return (
            self.db.query(Share)
            .filter(
                Share.id == share_id,
                Share.expires_at > datetime.utcnow(),
            )
            .first()
        )
