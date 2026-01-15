"""
Unit tests for app.middleware.observability module.
Tests the observability middleware for request tracking and metrics.
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import Request
from app.middleware.observability import (
    observability_middleware,
    EXCLUDED_PATHS,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    REQUEST_ERRORS,
)


class TestExcludedPaths:
    """Test cases for excluded paths constant."""

    def test_excluded_paths_contains_metrics(self):
        """Test that /metrics is in excluded paths."""
        assert "/metrics" in EXCLUDED_PATHS

    def test_excluded_paths_contains_healthz(self):
        """Test that /healthz is in excluded paths."""
        assert "/healthz" in EXCLUDED_PATHS

    def test_excluded_paths_contains_readyz(self):
        """Test that /readyz is in excluded paths."""
        assert "/readyz" in EXCLUDED_PATHS

    def test_excluded_paths_is_set(self):
        """Test that EXCLUDED_PATHS is a set."""
        assert isinstance(EXCLUDED_PATHS, set)

    def test_excluded_paths_count(self):
        """Test that there are exactly 3 excluded paths."""
        assert len(EXCLUDED_PATHS) == 3


class TestMetricsInitialization:
    """Test cases for metrics initialization."""

    def test_request_count_counter_exists(self):
        """Test that REQUEST_COUNT counter is defined."""
        assert REQUEST_COUNT is not None

    def test_request_latency_histogram_exists(self):
        """Test that REQUEST_LATENCY histogram is defined."""
        assert REQUEST_LATENCY is not None

    def test_request_errors_counter_exists(self):
        """Test that REQUEST_ERRORS counter is defined."""
        assert REQUEST_ERRORS is not None


@pytest.mark.asyncio
class TestObservabilityMiddleware:
    """Test cases for the observability middleware."""

    async def test_middleware_skips_excluded_paths(self):
        """Test that middleware skips processing for excluded paths."""
        request = Mock(spec=Request)
        request.url.path = "/healthz"
        request.headers.get.return_value = None
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 200
        call_next.return_value = response
        
        result = await observability_middleware(request, call_next)
        
        assert result == response
        # Should call next without incrementing metrics
        call_next.assert_called_once()

    async def test_middleware_processes_normal_paths(self):
        """Test that middleware processes normal paths."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 200
        call_next.return_value = response
        
        result = await observability_middleware(request, call_next)
        
        assert result == response
        call_next.assert_called_once()

    async def test_middleware_uses_provided_request_id(self):
        """Test that middleware uses X-Request-ID header if provided."""
        request_id = "provided-request-id-123"
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = request_id
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 200
        call_next.return_value = response
        
        with patch("app.middleware.observability.set_request_id") as mock_set_id:
            result = await observability_middleware(request, call_next)
            mock_set_id.assert_called_once_with(request_id)

    async def test_middleware_generates_request_id_if_not_provided(self):
        """Test that middleware generates a request ID if not provided."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 200
        call_next.return_value = response
        
        with patch("app.middleware.observability.str") as mock_str:
            with patch("app.middleware.observability.uuid") as mock_uuid:
                with patch("app.middleware.observability.set_request_id") as mock_set_id:
                    mock_uuid.uuid4.return_value = "generated-uuid"
                    mock_str.return_value = "generated-uuid"
                    
                    await observability_middleware(request, call_next)

    async def test_middleware_measures_request_latency(self):
        """Test that middleware measures request latency."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        async def slow_call_next(req):
            await asyncio.sleep(0.01)  # 10ms delay
            response = Mock()
            response.status_code = 200
            return response
        
        with patch("app.middleware.observability.set_request_id"):
            with patch("app.middleware.observability.REQUEST_LATENCY") as mock_latency:
                await observability_middleware(request, slow_call_next)
                # Verify that latency was recorded
                mock_latency.labels.assert_called()

    async def test_middleware_increments_request_count(self):
        """Test that middleware increments request count."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 200
        call_next.return_value = response
        
        with patch("app.middleware.observability.set_request_id"):
            with patch("app.middleware.observability.REQUEST_COUNT") as mock_count:
                await observability_middleware(request, call_next)
                # Verify that count was incremented
                mock_count.labels.assert_called()

    async def test_middleware_handles_exception(self):
        """Test that middleware handles exceptions properly."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        call_next.side_effect = Exception("Test exception")
        
        with patch("app.middleware.observability.set_request_id"):
            with patch("app.middleware.observability.REQUEST_ERRORS") as mock_errors:
                with pytest.raises(Exception):
                    await observability_middleware(request, call_next)
                # Verify that error counter was incremented
                mock_errors.labels.assert_called()

    async def test_middleware_records_status_code(self):
        """Test that middleware records the response status code."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "POST"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 201
        call_next.return_value = response
        
        with patch("app.middleware.observability.set_request_id"):
            with patch("app.middleware.observability.REQUEST_COUNT") as mock_count:
                await observability_middleware(request, call_next)
                # Verify that status code is included in labels
                call_args = mock_count.labels.call_args
                assert call_args[0][2] == 201  # Third argument should be status code

    async def test_middleware_handles_no_route_in_scope(self):
        """Test that middleware handles requests with no route in scope."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        request.headers.get.return_value = None
        request.scope = {}  # No route
        
        call_next = AsyncMock()
        response = Mock()
        response.status_code = 200
        call_next.return_value = response
        
        with patch("app.middleware.observability.set_request_id"):
            result = await observability_middleware(request, call_next)
            assert result == response

    async def test_middleware_exception_still_records_metrics(self):
        """Test that exception cases still record metrics."""
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "DELETE"
        request.headers.get.return_value = None
        request.scope = {"route": Mock(path="/api/users")}
        
        call_next = AsyncMock()
        call_next.side_effect = ValueError("Test value error")
        
        with patch("app.middleware.observability.set_request_id"):
            with patch("app.middleware.observability.REQUEST_LATENCY") as mock_latency:
                with pytest.raises(ValueError):
                    await observability_middleware(request, call_next)
                # Latency should still be recorded even on exception
                mock_latency.labels.assert_called()

    async def test_middleware_with_different_http_methods(self):
        """Test middleware with different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            request = Mock(spec=Request)
            request.url.path = "/api/resource"
            request.method = method
            request.headers.get.return_value = None
            request.scope = {"route": Mock(path="/api/resource")}
            
            call_next = AsyncMock()
            response = Mock()
            response.status_code = 200
            call_next.return_value = response
            
            with patch("app.middleware.observability.set_request_id"):
                result = await observability_middleware(request, call_next)
                assert result == response

    async def test_middleware_with_different_status_codes(self):
        """Test middleware with different HTTP status codes."""
        status_codes = [200, 201, 204, 400, 401, 403, 404, 500, 502]
        
        for status_code in status_codes:
            request = Mock(spec=Request)
            request.url.path = "/api/resource"
            request.method = "GET"
            request.headers.get.return_value = None
            request.scope = {"route": Mock(path="/api/resource")}
            
            call_next = AsyncMock()
            response = Mock()
            response.status_code = status_code
            call_next.return_value = response
            
            with patch("app.middleware.observability.set_request_id"):
                with patch("app.middleware.observability.REQUEST_COUNT") as mock_count:
                    result = await observability_middleware(request, call_next)
                    assert result.status_code == status_code
