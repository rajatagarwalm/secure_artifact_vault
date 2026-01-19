"""add password_expires_at to users

Revision ID: abc123def456
Revises: 1398671fa5d5
Create Date: 2026-01-19 06:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'abc123def456'
down_revision: Union[str, Sequence[str], None] = '1398671fa5d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('password_expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'password_expires_at')
