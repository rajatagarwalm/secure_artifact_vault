from sqlalchemy.orm import Session

from app.db.models.password_history import UserPasswordHistory


class PasswordHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, password_hash: str):
        """Record password change in history."""
        history = UserPasswordHistory(
            user_id=user_id,
            password_hash=password_hash,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_recent_passwords(self, user_id: str, limit: int = 5):
        """Get recent passwords for a user to prevent reuse."""
        return (
            self.db.query(UserPasswordHistory)
            .filter(UserPasswordHistory.user_id == user_id)
            .order_by(UserPasswordHistory.changed_at.desc())
            .limit(limit)
            .all()
        )
