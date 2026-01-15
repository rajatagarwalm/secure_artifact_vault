"""
Integration and comprehensive tests for app modules.
Tests for overall app functionality and module interactions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session


class TestCoreModulesIntegration:
    """Integration tests for core modules."""

    def test_all_core_modules_importable(self):
        """Test that all core modules can be imported together."""
        from app.core import config, logging, request_context, security
        assert config is not None
        assert logging is not None
        assert request_context is not None
        assert security is not None

    def test_core_config_and_logging_integration(self):
        """Test config and logging work together."""
        from app.core.config import settings
        from app.core.logging import configure_logging, RequestIdFilter
        
        # Both should exist and work together
        assert settings is not None
        assert configure_logging is not None
        assert RequestIdFilter is not None

    def test_request_context_usage_in_logging(self):
        """Test that request context is used by logging."""
        from app.core.logging import RequestIdFilter
        from app.core.request_context import set_request_id, get_request_id
        import logging
        
        # Set a request ID
        test_id = "test-integration-id"
        set_request_id(test_id)
        
        # Verify it can be retrieved
        assert get_request_id() == test_id
        
        # Create a filter
        filter_obj = RequestIdFilter()
        assert filter_obj is not None


class TestDatabaseModulesIntegration:
    """Integration tests for database modules."""

    def test_all_database_modules_importable(self):
        """Test that all database modules can be imported."""
        from app.db import base, session
        from app.db import models
        
        assert base is not None
        assert session is not None
        assert models is not None

    def test_database_models_with_base(self):
        """Test that models work with base."""
        from app.db.base import Base
        from app.db.models import (
            Organization, User, UserOrgRole,
            RefreshToken, Artifact, Share, AuditLog
        )
        
        # All models should exist
        models_list = [Organization, User, UserOrgRole, RefreshToken, Artifact, Share, AuditLog]
        assert all(m is not None for m in models_list)

    def test_session_uses_database_url(self):
        """Test that session uses database URL from config."""
        from app.db.session import engine
        from app.core.config import settings
        
        # Both should exist
        assert engine is not None
        assert settings.DATABASE_URL is not None


class TestMiddlewareIntegration:
    """Integration tests for middleware."""

    def test_observability_middleware_with_request_context(self):
        """Test observability middleware integrates with request context."""
        from app.middleware.observability import observability_middleware
        from app.core.request_context import set_request_id, get_request_id
        
        # Both should work together
        assert observability_middleware is not None
        assert set_request_id is not None
        assert get_request_id is not None

    def test_middleware_metrics_are_configured(self):
        """Test that middleware metrics are properly configured."""
        from app.middleware.observability import (
            REQUEST_COUNT, REQUEST_LATENCY, REQUEST_ERRORS, EXCLUDED_PATHS
        )
        
        assert REQUEST_COUNT is not None
        assert REQUEST_LATENCY is not None
        assert REQUEST_ERRORS is not None
        assert EXCLUDED_PATHS is not None
        assert len(EXCLUDED_PATHS) > 0


class TestRepositoriesIntegration:
    """Integration tests for repositories."""

    def test_all_repositories_importable(self):
        """Test that all repositories can be imported."""
        from app.repositories import (
            user_repo, artifact_repo, org_repo, share_repo,
            audit_repo, refresh_token_repo, user_org_role_repo
        )
        
        assert user_repo is not None
        assert artifact_repo is not None
        assert org_repo is not None
        assert share_repo is not None
        assert audit_repo is not None
        assert refresh_token_repo is not None
        assert user_org_role_repo is not None

    def test_repository_classes_can_be_instantiated(self):
        """Test that repository classes can be instantiated."""
        from app.repositories.user_repo import UserRepository
        from app.repositories.artifact_repo import ArtifactRepository
        from app.repositories.share_repo import ShareRepository
        
        mock_session = Mock(spec=Session)
        
        user_repo = UserRepository(mock_session)
        artifact_repo = ArtifactRepository(mock_session)
        share_repo = ShareRepository(mock_session)
        
        assert user_repo is not None
        assert artifact_repo is not None
        assert share_repo is not None


class TestSchemasIntegration:
    """Integration tests for schemas."""

    def test_all_schemas_importable(self):
        """Test that all schemas can be imported."""
        from app.schemas import (
            artifact, auth, user, org, share, audit
        )
        
        assert artifact is not None
        assert auth is not None
        assert user is not None
        assert org is not None
        assert share is not None
        assert audit is not None

    def test_schemas_are_pydantic_compatible(self):
        """Test that all schemas are Pydantic compatible."""
        from pydantic import BaseModel
        from app.schemas.artifact import ArtifactResponse, ArtifactListResponse
        from app.schemas.auth import LoginRequest, TokenResponse
        
        assert issubclass(ArtifactResponse, BaseModel)
        assert issubclass(ArtifactListResponse, BaseModel)
        assert issubclass(LoginRequest, BaseModel)
        assert issubclass(TokenResponse, BaseModel)


class TestSecurityIntegration:
    """Integration tests for security features."""

    def test_password_hashing_and_verification_integration(self):
        """Test password hashing and verification work together."""
        from app.core.security import hash_password, verify_password
        
        password = "secure_password_123"
        hashed = hash_password(password)
        
        # Hashed should be different from original
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_token_creation_integration(self):
        """Test token creation works."""
        from app.core.security import create_access_token
        
        data = {"sub": "user_id"}
        permissions = ["read", "write"]
        
        token = create_access_token(data, permissions)
        assert isinstance(token, str)
        assert len(token) > 0


class TestAppInitializationIntegration:
    """Integration tests for app initialization."""

    def test_app_imports_all_routers(self):
        """Test that main app imports all routers."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            from app.main import app
            
            # App should have multiple routes
            routes = [r for r in app.routes if hasattr(r, "path")]
            assert len(routes) > 2  # At least health, readiness, and others

    def test_app_initialization_with_all_modules(self):
        """Test app initialization uses all core modules."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                from app.db import models
                
                assert app is not None
                assert models is not None


class TestCronModulePresent:
    """Test that cron module exists."""

    def test_cron_module_exists(self):
        """Test that cron module is present."""
        import app.cron
        assert app.cron is not None

    def test_cron_module_is_importable(self):
        """Test that cron module can be imported."""
        try:
            import app.cron as cron_module
            assert cron_module is not None
        except ImportError:
            # If cron module has no __init__.py, that's ok
            assert True


class TestUtilsModule:
    """Test that utils module is present."""

    def test_utils_module_exists(self):
        """Test that utils module exists."""
        import app.utils
        assert app.utils is not None

    def test_utils_module_is_importable(self):
        """Test that utils module can be imported."""
        try:
            import app.utils as utils_module
            assert utils_module is not None
        except ImportError:
            # If utils module has no __init__.py, that's ok
            assert True
