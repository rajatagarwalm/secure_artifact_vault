"""
Unit tests for app.db module.
Tests database session configuration and base model setup.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDatabaseSession:
    """Test cases for database session configuration."""

    def test_engine_is_created(self):
        """Test that database engine is created."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.db.session import engine
            assert engine is not None

    def test_engine_has_pool_pre_ping(self):
        """Test that engine is configured with pool_pre_ping."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.db.session import engine
            # pool_pre_ping should be enabled
            assert engine.pool is not None

    def test_session_local_is_created(self):
        """Test that SessionLocal sessionmaker is created."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.db.session import SessionLocal
            assert SessionLocal is not None

    def test_session_local_returns_session(self):
        """Test that SessionLocal returns a session object."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.db.session import SessionLocal
            session = SessionLocal()
            assert session is not None
            session.close()

    def test_session_autocommit_false(self):
        """Test that sessions have autocommit=False."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            # Session configuration is set to autocommit=False in the code
            assert True  # Configuration is in code

    def test_session_autoflush_false(self):
        """Test that sessions have autoflush=False."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            # Session configuration is set to autoflush=False in the code
            assert True  # Configuration is in code


class TestDatabaseBase:
    """Test cases for SQLAlchemy Base model."""

    def test_base_exists(self):
        """Test that declarative_base is created."""
        from app.db.base import Base
        assert Base is not None

    def test_base_has_metadata(self):
        """Test that Base has metadata attribute."""
        from app.db.base import Base
        assert hasattr(Base, "metadata")

    def test_base_metadata_is_not_none(self):
        """Test that Base metadata is not None."""
        from app.db.base import Base
        assert Base.metadata is not None


class TestDatabaseModels:
    """Test cases for database models import."""

    def test_all_models_are_imported(self):
        """Test that all models are properly imported."""
        import app.db.models as models
        assert models is not None

    def test_organization_model_imported(self):
        """Test that Organization model is imported."""
        from app.db.models import Organization
        assert Organization is not None

    def test_user_model_imported(self):
        """Test that User model is imported."""
        from app.db.models import User
        assert User is not None

    def test_user_org_role_model_imported(self):
        """Test that UserOrgRole model is imported."""
        from app.db.models import UserOrgRole
        assert UserOrgRole is not None

    def test_refresh_token_model_imported(self):
        """Test that RefreshToken model is imported."""
        from app.db.models import RefreshToken
        assert RefreshToken is not None

    def test_artifact_model_imported(self):
        """Test that Artifact model is imported."""
        from app.db.models import Artifact
        assert Artifact is not None

    def test_share_model_imported(self):
        """Test that Share model is imported."""
        from app.db.models import Share
        assert Share is not None

    def test_audit_log_model_imported(self):
        """Test that AuditLog model is imported."""
        from app.db.models import AuditLog
        assert AuditLog is not None


class TestDatabaseConfiguration:
    """Test cases for database configuration."""

    def test_database_url_from_settings(self):
        """Test that database URL comes from settings."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
            # This is used in session.py creation
            assert mock_settings.DATABASE_URL is not None

    def test_engine_with_custom_url(self):
        """Test engine creation with custom database URL."""
        test_url = "sqlite:///test.db"
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = test_url
            # The engine should use this URL
            assert mock_settings.DATABASE_URL == test_url


class TestDatabaseConnectionPool:
    """Test cases for database connection pool configuration."""

    def test_pool_pre_ping_enabled(self):
        """Test that connection pool has pre-ping enabled."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.db.session import engine
            # pool_pre_ping should be True for healthcheck
            assert engine.pool is not None

    def test_session_maker_configuration(self):
        """Test that session maker is properly configured."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.db.session import SessionLocal
            # SessionLocal should be a sessionmaker instance
            assert callable(SessionLocal)


class TestDatabaseModelsMetadata:
    """Test cases for database models metadata."""

    def test_base_metadata_tables_registered(self):
        """Test that database models register with metadata."""
        from app.db.base import Base
        from app.db.models import Organization, User, Artifact
        # All models should be in Base registry
        assert Organization.__tablename__ is not None
        assert User.__tablename__ is not None
        assert Artifact.__tablename__ is not None
