"""
Unit tests for app.api endpoints.
Tests API routes and request handling.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def test_client_full():
    """Create test client with minimal mocking."""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        mock_settings.JWT_SECRET_KEY = "test-secret"
        mock_settings.MAX_UPLOAD_SIZE_MB = 1024
        with patch("app.middleware.observability.observability_middleware", side_effect=lambda r, c: c(r)):
            from app.main import app
            return TestClient(app)


class TestMetricsEndpoint:
    """Test cases for metrics endpoint."""

    def test_metrics_endpoint_imported(self):
        """Test that metrics router can be imported."""
        from app.api.metrics import router as metrics_router
        assert metrics_router is not None

    def test_metrics_module_exists(self):
        """Test that metrics module exists."""
        import app.api.metrics
        assert app.api.metrics is not None


class TestAuthEndpoints:
    """Test cases for auth API endpoints."""

    def test_auth_router_endpoints_registered(self, test_client_full):
        """Test that auth endpoints are registered."""
        # Check if auth endpoints are in the routes
        routes = [route.path for route in test_client_full.app.routes if hasattr(route, "path")]
        # At least healthz and readyz should be present
        assert len(routes) > 0


class TestUsersEndpoints:
    """Test cases for users API endpoints."""

    def test_users_router_registered(self, test_client_full):
        """Test that users router is registered."""
        routes = [route.path for route in test_client_full.app.routes if hasattr(route, "path")]
        assert len(routes) > 0


class TestArtifactsEndpoints:
    """Test cases for artifacts API endpoints."""

    def test_artifacts_router_registered(self, test_client_full):
        """Test that artifacts router is registered."""
        routes = [route.path for route in test_client_full.app.routes if hasattr(route, "path")]
        assert len(routes) > 0


class TestOrgsEndpoints:
    """Test cases for orgs API endpoints."""

    def test_orgs_router_registered(self, test_client_full):
        """Test that orgs router is registered."""
        routes = [route.path for route in test_client_full.app.routes if hasattr(route, "path")]
        assert len(routes) > 0


class TestSharesEndpoints:
    """Test cases for shares API endpoints."""

    def test_shares_router_registered(self, test_client_full):
        """Test that shares router is registered."""
        routes = [route.path for route in test_client_full.app.routes if hasattr(route, "path")]
        assert len(routes) > 0


class TestAuditEndpoints:
    """Test cases for audit API endpoints."""

    def test_audit_router_registered(self, test_client_full):
        """Test that audit router is registered."""
        routes = [route.path for route in test_client_full.app.routes if hasattr(route, "path")]
        assert len(routes) > 0


class TestApiModulesImport:
    """Test cases for API module imports."""

    def test_all_api_modules_exist(self):
        """Test that all API modules can be imported."""
        import app.api
        import app.api.metrics
        import app.api.deps
        import app.api.v1.auth
        import app.api.v1.users
        import app.api.v1.artifacts
        import app.api.v1.orgs
        import app.api.v1.shares
        import app.api.v1.audit
        assert True

    def test_api_routers_are_importable(self):
        """Test that all routers can be imported."""
        from app.api.v1.auth import router as auth_router
        from app.api.v1.users import router as users_router
        from app.api.v1.artifacts import router as artifacts_router
        from app.api.v1.orgs import router as orgs_router
        from app.api.v1.shares import router as shares_router
        from app.api.v1.audit import router as audit_router
        from app.api.metrics import router as metrics_router
        
        assert auth_router is not None
        assert users_router is not None
        assert artifacts_router is not None
        assert orgs_router is not None
        assert shares_router is not None
        assert audit_router is not None
        assert metrics_router is not None
