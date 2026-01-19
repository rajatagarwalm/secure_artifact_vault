import sys
import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# -------------------------------------------------------
# Add project root to PYTHONPATH
# -------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app.core.config import settings
from app.db.base import Base

from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.models.user_org_role import UserOrgRole
from app.db.models.refresh_token import RefreshToken
from app.db.models.artifact import Artifact
from app.db.models.share import Share
from app.db.models.audit_log import AuditLog

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
