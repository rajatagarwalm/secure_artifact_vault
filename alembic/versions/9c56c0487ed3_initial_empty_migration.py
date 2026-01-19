"""initial empty migration

Revision ID: 9c56c0487ed3
Revises: 72ecff915d9c
Create Date: 2026-01-12 11:55:53.401508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c56c0487ed3'
down_revision: Union[str, Sequence[str], None] = '72ecff915d9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
