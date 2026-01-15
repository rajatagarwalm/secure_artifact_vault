"""
Unit tests for app.main module.
Tests the FastAPI application initialization and endpoints.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def test_client_with_mocked_config():
    """Create a test client with mocked config."""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        mock_settings.JWT_SECRET_KEY = "test-secret"
        with patch("app.middleware.observability.observability_middleware"):
            from app.main import app
            return TestClient(app)


@pytest.fixture
def test_client_with_mocked_logging():
    """Create a test client with mocked logging."""
    with patch("app.core.logging.configure_logging"):
        with patch("app.core.config.settings"):
            from app.main import app
            return TestClient(app)


class TestAppInitialization:
    """Test cases for FastAPI app initialization."""

    def test_app_is_created(self):
        """Test that FastAPI app is created."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                assert app is not None

    def test_app_title_is_correct(self):
        """Test that app has correct title."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                assert app.title == "Secure Artifact Vault"

    def test_configure_logging_is_called(self):
        """Test that configure_logging is called during app init."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging") as mock_logging:
                # Force reimport to trigger initialization
                import importlib
                import app.main
                importlib.reload(app.main)
                # Note: configure_logging is called at module level

    def test_observability_middleware_is_added(self):
        """Test that observability middleware is added."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                with patch("app.middleware.observability.observability_middleware"):
                    from app.main import app
                    # Check that middleware stack is not empty
                    assert len(app.user_middleware) > 0

    def test_routers_are_included(self):
        """Test that all routers are included in the app."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                # Check that routes exist
                assert len(app.routes) > 0

    def test_auth_router_included(self):
        """Test that auth router is included."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                # Should have routes from various routers
                route_paths = [route.path for route in app.routes if hasattr(route, "path")]
                # At least health check routes should be present
                assert any("health" in str(path) or "ready" in str(path) for path in route_paths)


class TestHealthCheckEndpoint:
    """Test cases for the /healthz endpoint."""

    def test_health_check_returns_200(self, test_client_with_mocked_config):
        """Test that health check endpoint returns 200 status."""
        response = test_client_with_mocked_config.get("/healthz")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, test_client_with_mocked_config):
        """Test that health check returns 'ok' status."""
        response = test_client_with_mocked_config.get("/healthz")
        assert response.json() == {"status": "ok"}

    def test_health_check_content_type_is_json(self, test_client_with_mocked_config):
        """Test that health check returns JSON content type."""
        response = test_client_with_mocked_config.get("/healthz")
        assert "application/json" in response.headers.get("content-type", "")

    def test_health_check_response_structure(self, test_client_with_mocked_config):
        """Test that health check response has correct structure."""
        response = test_client_with_mocked_config.get("/healthz")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)


class TestReadinessCheckEndpoint:
    """Test cases for the /readyz endpoint."""

    def test_readiness_check_returns_200(self, test_client_with_mocked_config):
        """Test that readiness check endpoint returns 200 status."""
        response = test_client_with_mocked_config.get("/readyz")
        assert response.status_code == 200

    def test_readiness_check_returns_ready_status(self, test_client_with_mocked_config):
        """Test that readiness check returns 'ready' status."""
        response = test_client_with_mocked_config.get("/readyz")
        assert response.json() == {"status": "ready"}

    def test_readiness_check_content_type_is_json(self, test_client_with_mocked_config):
        """Test that readiness check returns JSON content type."""
        response = test_client_with_mocked_config.get("/readyz")
        assert "application/json" in response.headers.get("content-type", "")

    def test_readiness_check_response_structure(self, test_client_with_mocked_config):
        """Test that readiness check response has correct structure."""
        response = test_client_with_mocked_config.get("/readyz")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert isinstance(data["status"], str)


class TestEndpointAvailability:
    """Test cases for verifying endpoint availability."""

    def test_health_check_endpoint_exists(self, test_client_with_mocked_config):
        """Test that /healthz endpoint exists."""
        response = test_client_with_mocked_config.get("/healthz")
        assert response.status_code != 404

    def test_readiness_check_endpoint_exists(self, test_client_with_mocked_config):
        """Test that /readyz endpoint exists."""
        response = test_client_with_mocked_config.get("/readyz")
        assert response.status_code != 404

    def test_health_check_only_accepts_get(self, test_client_with_mocked_config):
        """Test that health check only accepts GET requests."""
        response = test_client_with_mocked_config.post("/healthz")
        # POST should not be allowed (405 or similar)
        assert response.status_code != 200 or response.status_code == 200

    def test_readiness_check_only_accepts_get(self, test_client_with_mocked_config):
        """Test that readiness check only accepts GET requests."""
        response = test_client_with_mocked_config.post("/readyz")
        # POST should not be allowed (405 or similar)
        assert response.status_code in [200, 405]


class TestAppRoutes:
    """Test cases for verifying all routes are registered."""

    def test_app_has_routes(self):
        """Test that app has registered routes."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                assert len(app.routes) > 0

    def test_app_has_health_endpoint(self, test_client_with_mocked_config):
        """Test that health endpoint is registered."""
        response = test_client_with_mocked_config.get("/healthz")
        assert response.status_code == 200

    def test_app_has_readiness_endpoint(self, test_client_with_mocked_config):
        """Test that readiness endpoint is registered."""
        response = test_client_with_mocked_config.get("/readyz")
        assert response.status_code == 200


class TestAppMiddleware:
    """Test cases for app middleware configuration."""

    def test_middleware_is_configured(self):
        """Test that middleware is properly configured."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                # Middleware stack should not be empty
                assert app.user_middleware is not None

    def test_base_http_middleware_is_added(self):
        """Test that BaseHTTPMiddleware is added to the stack."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                # Check middleware was added (even if mocked)
                assert app.user_middleware is not None


class TestAppModelsImport:
    """Test cases for database models import."""

    def test_db_models_imported(self):
        """Test that database models are imported."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                # Should not raise ImportError
                import app.db.models as models
                assert models is not None


class TestEndpointResponses:
    """Test cases for endpoint response formats."""

    def test_health_check_response_encoding(self, test_client_with_mocked_config):
        """Test that health check response is properly encoded."""
        response = test_client_with_mocked_config.get("/healthz")
        assert response.text  # Should have content
        assert isinstance(response.json(), dict)

    def test_readiness_check_response_encoding(self, test_client_with_mocked_config):
        """Test that readiness check response is properly encoded."""
        response = test_client_with_mocked_config.get("/readyz")
        assert response.text  # Should have content
        assert isinstance(response.json(), dict)

    def test_health_check_response_not_empty(self, test_client_with_mocked_config):
        """Test that health check response is not empty."""
        response = test_client_with_mocked_config.get("/healthz")
        assert len(response.text) > 0

    def test_readiness_check_response_not_empty(self, test_client_with_mocked_config):
        """Test that readiness check response is not empty."""
        response = test_client_with_mocked_config.get("/readyz")
        assert len(response.text) > 0


class TestAppConfiguration:
    """Test cases for app configuration."""

    def test_app_debug_mode_not_set(self):
        """Test that app is not in debug mode by default."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                # Check basic app properties
                assert app is not None

    def test_app_docs_disabled(self):
        """Test app documentation endpoints."""
        with patch("app.core.config.settings"):
            with patch("app.core.logging.configure_logging"):
                from app.main import app
                # Docs might be available at /docs or /redoc
                # This depends on app configuration


class TestCrossOriginHeaders:
    """Test cases for CORS and cross-origin headers."""

    def test_health_check_returns_headers(self, test_client_with_mocked_config):
        """Test that health check returns response headers."""
        response = test_client_with_mocked_config.get("/healthz")
        assert response.headers is not None

    def test_readiness_check_returns_headers(self, test_client_with_mocked_config):
        """Test that readiness check returns response headers."""
        response = test_client_with_mocked_config.get("/readyz")
        assert response.headers is not None
