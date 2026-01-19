"""add prefix search index on artifacts

Revision ID: 1398671fa5d5
Revises: 9c6d17c204ca
Create Date: 2026-01-13 10:40:33.720010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1398671fa5d5'
down_revision: Union[str, Sequence[str], None] = '9c6d17c204ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index(
        "ix_artifacts_org_filename_prefix",
        "artifacts",
        ["org_id", sa.text("filename varchar_pattern_ops")],
        postgresql_using="btree",
    )


def downgrade():
    op.drop_index(
        "ix_artifacts_org_filename_prefix",
        table_name="artifacts",
    )
