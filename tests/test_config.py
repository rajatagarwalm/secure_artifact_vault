"""
Unit tests for app.core.config module.
Tests the Settings class and configuration loading.
"""
import pytest
import os
from unittest.mock import patch, MagicMock


class TestSettings:
    """Test cases for the Settings class."""

    def test_settings_initialization_with_env_vars(self, mock_settings):
        """Test that settings can be initialized with environment variables."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "JWT_SECRET_KEY": "secret123",
        }):
            settings = Settings()
            assert settings.DB_USER == "testuser"
            assert settings.DB_PASSWORD == "testpass"
            assert settings.DB_HOST == "localhost"
            assert settings.DB_PORT == 5432
            assert settings.DB_NAME == "testdb"
            assert settings.JWT_SECRET_KEY == "secret123"

    def test_settings_default_values(self):
        """Test that default values are set correctly for optional fields."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
            "DB_HOST": "host",
            "DB_PORT": "5432",
            "DB_NAME": "db",
            "JWT_SECRET_KEY": "secret",
        }):
            settings = Settings()
            assert settings.JWT_ALGORITHM == "HS256"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
            assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
            assert settings.MAX_UPLOAD_SIZE_MB == 1024

    def test_settings_custom_values(self):
        """Test that custom values override defaults."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
            "DB_HOST": "host",
            "DB_PORT": "5432",
            "DB_NAME": "db",
            "JWT_SECRET_KEY": "secret",
            "JWT_ALGORITHM": "HS512",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "14",
            "MAX_UPLOAD_SIZE_MB": "2048",
        }):
            settings = Settings()
            assert settings.JWT_ALGORITHM == "HS512"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 14
            assert settings.MAX_UPLOAD_SIZE_MB == 2048

    def test_database_url_property(self):
        """Test the DATABASE_URL property construction."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
            "DB_HOST": "db.example.com",
            "DB_PORT": "5432",
            "DB_NAME": "mydb",
            "JWT_SECRET_KEY": "secret",
        }):
            settings = Settings()
            expected_url = "postgresql+psycopg2://testuser:testpass@db.example.com:5432/mydb"
            assert settings.DATABASE_URL == expected_url

    def test_database_url_with_special_characters(self):
        """Test DATABASE_URL construction with special characters in password."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "DB_USER": "user@domain",
            "DB_PASSWORD": "p@ss!w0rd",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "JWT_SECRET_KEY": "secret",
        }):
            settings = Settings()
            assert "postgresql+psycopg2://" in settings.DATABASE_URL
            assert "user@domain" in settings.DATABASE_URL
            assert "p@ss!w0rd" in settings.DATABASE_URL

    def test_settings_instance_is_singleton(self):
        """Test that the settings instance is available and consistent."""
        from app.core.config import settings
        assert settings is not None
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "JWT_SECRET_KEY")

    def test_all_required_fields_present(self):
        """Test that all required settings fields are present."""
        from app.core.config import settings
        
        required_fields = [
            "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", 
            "DB_NAME", "JWT_SECRET_KEY"
        ]
        for field in required_fields:
            assert hasattr(settings, field), f"Missing required field: {field}"

    def test_settings_type_conversion(self):
        """Test that string environment variables are converted to proper types."""
        from app.core.config import Settings
        
        with patch.dict(os.environ, {
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
            "DB_HOST": "host",
            "DB_PORT": "12345",  # String that should be converted to int
            "DB_NAME": "db",
            "JWT_SECRET_KEY": "secret",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",  # String to int
        }):
            settings = Settings()
            assert isinstance(settings.DB_PORT, int)
            assert settings.DB_PORT == 12345
            assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
