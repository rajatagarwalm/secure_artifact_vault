"""
Unit tests for app.core.logging module.
Tests the logging configuration and RequestIdFilter.
"""
import pytest
import logging
from unittest.mock import patch, Mock, MagicMock
from app.core.logging import configure_logging, RequestIdFilter


class TestRequestIdFilter:
    """Test cases for the RequestIdFilter class."""

    def test_filter_adds_request_id_to_record(self):
        """Test that filter adds request_id to log record."""
        filter_obj = RequestIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        with patch("app.core.logging.get_request_id", return_value="test-123"):
            result = filter_obj.filter(record)
            assert result is True
            assert record.request_id == "test-123"

    def test_filter_returns_true(self):
        """Test that filter always returns True."""
        filter_obj = RequestIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        with patch("app.core.logging.get_request_id", return_value=None):
            result = filter_obj.filter(record)
            assert result is True

    def test_filter_with_none_request_id(self):
        """Test filter when request_id is None."""
        filter_obj = RequestIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        with patch("app.core.logging.get_request_id", return_value=None):
            filter_obj.filter(record)
            assert record.request_id is None

    def test_filter_with_different_request_ids(self):
        """Test filter with different request IDs."""
        filter_obj = RequestIdFilter()
        
        test_ids = ["req-001", "req-002", "12345", "uuid-style-id-here"]
        
        for test_id in test_ids:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg="Test message",
                args=(),
                exc_info=None,
            )
            
            with patch("app.core.logging.get_request_id", return_value=test_id):
                filter_obj.filter(record)
                assert record.request_id == test_id


class TestConfigureLogging:
    """Test cases for the configure_logging function."""

    def test_configure_logging_sets_up_logging(self):
        """Test that configure_logging sets up the logging system."""
        # Get root logger
        root_logger = logging.getLogger()
        initial_handlers = len(root_logger.handlers)
        
        with patch("logging.basicConfig") as mock_basic_config:
            with patch.object(root_logger, "addFilter"):
                configure_logging()
                mock_basic_config.assert_called_once()

    def test_configure_logging_sets_correct_level(self):
        """Test that configure_logging sets INFO level."""
        root_logger = logging.getLogger()
        
        with patch("logging.basicConfig") as mock_basic_config:
            with patch.object(root_logger, "addFilter"):
                configure_logging()
                call_kwargs = mock_basic_config.call_args[1]
                assert call_kwargs["level"] == logging.INFO

    def test_configure_logging_sets_format(self):
        """Test that configure_logging sets the correct format."""
        root_logger = logging.getLogger()
        expected_format = "%(asctime)s %(levelname)s [request_id=%(request_id)s] %(message)s"
        
        with patch("logging.basicConfig") as mock_basic_config:
            with patch.object(root_logger, "addFilter"):
                configure_logging()
                call_kwargs = mock_basic_config.call_args[1]
                assert call_kwargs["format"] == expected_format

    def test_configure_logging_adds_filter(self):
        """Test that configure_logging adds RequestIdFilter to root logger."""
        root_logger = logging.getLogger()
        
        with patch("logging.basicConfig"):
            with patch.object(root_logger, "addFilter") as mock_add_filter:
                configure_logging()
                mock_add_filter.assert_called_once()
                # Verify that it's a RequestIdFilter instance
                filter_arg = mock_add_filter.call_args[0][0]
                assert isinstance(filter_arg, RequestIdFilter)

    def test_configure_logging_idempotent(self):
        """Test that configure_logging can be called multiple times."""
        root_logger = logging.getLogger()
        
        with patch("logging.basicConfig") as mock_basic_config:
            with patch.object(root_logger, "addFilter"):
                # Call multiple times
                configure_logging()
                configure_logging()
                configure_logging()
                # basicConfig should be called three times
                assert mock_basic_config.call_count == 3

    def test_filter_integration_with_logging(self):
        """Test that the filter actually affects log records."""
        filter_obj = RequestIdFilter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Integration test message",
            args=(),
            exc_info=None,
        )
        
        with patch("app.core.logging.get_request_id", return_value="integration-test-id"):
            filter_obj.filter(record)
            assert hasattr(record, "request_id")
            assert record.request_id == "integration-test-id"
