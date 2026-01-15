# Unit Tests for Secure Artifact Vault

This directory contains comprehensive unit tests for the Secure Artifact Vault application.

## Quick Start

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_config.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_config.py::TestSettings -v
```

### Run Specific Test
```bash
pytest tests/test_config.py::TestSettings::test_settings_initialization_with_env_vars -v
```

## Test Organization

### Core Module Tests
- `test_config.py` - Configuration and settings management
- `test_logging.py` - Logging configuration
- `test_request_context.py` - Request ID context management
- `test_observability.py` - Observability middleware and metrics

### Application Tests
- `test_main.py` - FastAPI app initialization and endpoints
- `test_api_endpoints.py` - API router registration

### Database Tests
- `test_database.py` - Database configuration and models

### Feature Tests
- `test_schemas.py` - Pydantic schema validation
- `test_repositories.py` - Data access layer
- `test_services.py` - Business logic services
- `test_security_utils.py` - Security functions and utilities

### Integration Tests
- `test_integration.py` - Cross-module integration
- `test_additional_coverage.py` - Additional coverage tests

## Coverage Report

Current coverage: **62%** (238 tests passed)

Modules with 100% coverage:
- app/main.py
- app/core/config.py
- app/core/logging.py
- app/core/request_context.py
- app/middleware/observability.py
- All database models (app/db/models/*)
- All schemas (app/schemas/*)

## Test Fixtures

Common fixtures defined in `conftest.py`:

- `test_db` - In-memory SQLite database
- `db_session` - Fresh database session per test
- `mock_settings` - Mocked configuration
- `test_client` - FastAPI test client
- `mock_request_context` - Request context mock
- `mock_logger` - Logger mock

## Requirements

Test dependencies are listed in `requirements.txt`:
- pytest==7.4.3
- pytest-asyncio==0.21.1
- pytest-cov==4.1.0
- httpx==0.24.1

## Running Tests with Python

If you prefer not to use bash:

```bash
# Basic test run
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Specific test
python -m pytest tests/test_config.py::TestSettings::test_settings_initialization_with_env_vars -v
```

## Environment Setup

The tests use environment variables defined in `conftest.py`:

```python
DB_USER = "test"
DB_PASSWORD = "test"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "test_db"
JWT_SECRET_KEY = "test_secret_key_for_testing_only"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = "15"
REFRESH_TOKEN_EXPIRE_DAYS = "7"
MAX_UPLOAD_SIZE_MB = "1024"
```

## Continuous Integration

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=app --cov-report=xml
```

## HTML Coverage Report

After running tests with coverage, open `htmlcov/index.html` in a browser to view detailed coverage information by file and line.

## Tips for Writing New Tests

1. **Follow the naming convention**: `test_<module>.py` with `Test<Name>` classes
2. **Use descriptive names**: `test_<what_is_being_tested>`
3. **Keep tests focused**: One test should test one thing
4. **Use fixtures**: Leverage conftest.py fixtures to avoid duplication
5. **Mock external dependencies**: Use unittest.mock for database, external services, etc.
6. **Add docstrings**: Explain what each test verifies

## Common Issues

### Import errors
- Ensure you've activated the virtual environment
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Database errors
- Tests use in-memory SQLite, no external database needed
- If you see connection errors, check conftest.py environment variables

### Async test errors
- Use `@pytest.mark.asyncio` decorator for async tests
- Ensure pytest-asyncio is installed

## Performance

- Full test suite runs in ~4 seconds
- Individual test modules run in <1 second each

## Troubleshooting

```bash
# Show verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Show slowest tests
pytest tests/ --durations=10

# Run only failed tests
pytest tests/ --lf

# Run only last passed tests
pytest tests/ --ff
```

## Contributing

When adding new features:
1. Write unit tests first (TDD)
2. Ensure tests pass: `pytest tests/`
3. Check coverage doesn't decrease: `pytest tests/ --cov=app`
4. Update TEST_SUMMARY.md if adding new test files

## Support

For issues or questions about the test suite, refer to:
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- TEST_SUMMARY.md for detailed coverage information
