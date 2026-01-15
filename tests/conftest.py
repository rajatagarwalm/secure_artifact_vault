"""
Pytest configuration and fixtures for the Secure Artifact Vault application.
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set up test environment variables
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["MAX_UPLOAD_SIZE_MB"] = "1024"


@pytest.fixture(scope="session")
def test_db():
    """Create a test database engine with in-memory SQLite for testing."""
    # Using SQLite in-memory database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    return engine


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a new database session for a test."""
    from app.db.base import Base
    
    # Create tables
    Base.metadata.create_all(bind=test_db)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = SessionLocal()
    
    yield session
    
    session.close()
    # Clean up tables after test
    Base.metadata.drop_all(bind=test_db)


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings_mock = Mock()
    settings_mock.DB_USER = "test"
    settings_mock.DB_PASSWORD = "test"
    settings_mock.DB_HOST = "localhost"
    settings_mock.DB_PORT = 5432
    settings_mock.DB_NAME = "test_db"
    settings_mock.JWT_SECRET_KEY = "test_secret_key"
    settings_mock.JWT_ALGORITHM = "HS256"
    settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 15
    settings_mock.REFRESH_TOKEN_EXPIRE_DAYS = 7
    settings_mock.MAX_UPLOAD_SIZE_MB = 1024
    settings_mock.DATABASE_URL = "sqlite:///:memory:"
    return settings_mock


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    # Import here to avoid circular imports
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        from app.main import app
        return TestClient(app)


@pytest.fixture
def mock_request_context():
    """Mock request context for testing."""
    with patch("app.core.request_context.request_id_ctx_var") as mock_ctx:
        mock_ctx.get.return_value = "test-request-id-12345"
        mock_ctx.set = Mock()
        yield mock_ctx


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger
