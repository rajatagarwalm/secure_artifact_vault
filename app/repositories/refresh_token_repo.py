from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
            .first()
        )

    def revoke_all_for_user(self, user_id: str):
        (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .update({"is_revoked": True})
        )
        self.db.commit()
