import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class UserPasswordHistory(Base):
    __tablename__ = "user_password_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    password_hash = Column(String, nullable=False)
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
