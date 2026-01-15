# Secure Artifact Vault

A production-ready secure file storage and sharing system built with FastAPI, PostgreSQL, and modern security practices.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Database Schema](#database-schema)
- [Security](#security)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Secure Artifact Vault is a comprehensive file storage and management system designed for organizations that need secure, auditable artifact storage with fine-grained access control. It provides features for user authentication, organization management, artifact storage, sharing capabilities, and complete audit logging.

**Key Characteristics:**
- REST API-first design
- JWT-based authentication
- Role-based access control (RBAC)
- Complete audit trail
- Prometheus metrics
- Production-ready Docker deployment

## ✨ Features

### Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Rate limiting** on login attempts
- **User management** with activation/deactivation
- **Role-based access control** (RBAC) with permissions
- **Organization hierarchy** with user-org-role mapping

### Artifact Management
- **Secure file storage** with size validation
- **Artifact versioning** support
- **Metadata tracking** (owner, timestamps, etc.)
- **File download with streaming**
- **Batch operations** support

### Sharing & Collaboration
- **Share artifacts** with other users
- **Share expiration** support
- **Permission-based sharing** with read/write access levels
- **Audit trail** for all share events

### Organization Features
- **Multi-organization support**
- **Organization hierarchy**
- **User role assignments** per organization
- **Team management**

### Audit & Monitoring
- **Complete audit logging** of all operations
- **Prometheus metrics** for monitoring
- **Request tracing** with unique request IDs
- **Structured logging** with request context

### Security
- **Password hashing** with bcrypt
- **Rate limiting** on sensitive operations
- **CORS support** with configurable origins
- **Database encryption** support
- **Secure token handling**

## 🏗️ Architecture

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Web Framework** | FastAPI 0.115.6 |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0.36 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | Bcrypt (passlib) |
| **Data Validation** | Pydantic 2.9.2 |
| **Monitoring** | Prometheus Client 0.21.0 |
| **API Server** | Uvicorn 0.30.6 |
| **Testing** | Pytest 7.4.3 |

### Architectural Layers

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - Auth, Users, Artifacts, etc.     │
├─────────────────────────────────────┤
│       Service Layer (Business Logic)│
│  - AuthService, UserService, etc.   │
├─────────────────────────────────────┤
│    Repository Layer (Data Access)   │
│  - UserRepo, ArtifactRepo, etc.     │
├─────────────────────────────────────┤
│      Database Layer (SQLAlchemy)    │
│  - Models, Migrations, Sessions     │
├─────────────────────────────────────┤
│         PostgreSQL Database         │
└─────────────────────────────────────┘
```

### Database Schema

**Core Models:**
- **User** - User accounts and authentication
- **Organization** - Organizational units
- **UserOrgRole** - User roles within organizations
- **Artifact** - File storage with metadata
- **Share** - Artifact sharing between users
- **AuditLog** - Complete operation audit trail
- **RefreshToken** - Token management for sessions

## 📦 Prerequisites

- **Python 3.12+**
- **PostgreSQL 15+**
- **Docker & Docker Compose** (for containerized deployment)
- **Git** (for version control)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/secure-artifact-vault.git
cd secure-artifact-vault
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the project root:

```bash
# Application Settings
PROJECT_NAME=Secure Artifact Vault
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://artifact_user:artifact_pass@localhost:5432/artifact_vault
ENVIRONMENT=production

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Logging
LOG_LEVEL=INFO

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Security
BCRYPT_ROUNDS=12
MAX_UPLOAD_SIZE_MB=1024

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### 5. Setup PostgreSQL Database

#### Option A: Using Docker Compose

```bash
docker-compose up -d db
```

#### Option B: Local PostgreSQL Installation

```bash
createdb artifact_vault
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. (Optional) Seed Initial Data

```bash
python scripts/seed_data.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | Secure Artifact Vault | Application name |
| `DEBUG` | False | Debug mode (never True in production) |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | *required* | Secret key for JWT signing |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token TTL |
| `LOG_LEVEL` | INFO | Logging level |
| `ALLOWED_ORIGINS` | localhost | CORS allowed origins |
| `BCRYPT_ROUNDS` | 12 | Password hashing rounds |
| `MAX_UPLOAD_SIZE_MB` | 1024 | Maximum file size |

### Configuration File

The application uses `app/core/config.py` for centralized configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Secure Artifact Vault"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    # ... more settings
    
    class Config:
        env_file = ".env"
```

## 🏃 Running the Application

### Development Server

```bash
# Start with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the provided script
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📚 API Documentation

### Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer <access_token>
```

### User Endpoints

#### List Users
```http
GET /users?skip=0&limit=10
Authorization: Bearer <access_token>
```

#### Get User by ID
```http
GET /users/{user_id}
Authorization: Bearer <access_token>
```

#### Create User
```http
POST /users
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User"
}
```

#### Update User
```http
PUT /users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Updated Name",
  "is_active": true
}
```

#### Delete User
```http
DELETE /users/{user_id}
Authorization: Bearer <access_token>
```

### Artifact Endpoints

#### List Artifacts
```http
GET /artifacts?org_id=org123&skip=0&limit=10
Authorization: Bearer <access_token>
```

#### Get Artifact
```http
GET /artifacts/{artifact_id}
Authorization: Bearer <access_token>
```

#### Create Artifact
```http
POST /artifacts
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary_file>
name: "document.pdf"
org_id: "org123"
```

#### Update Artifact
```http
PUT /artifacts/{artifact_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "updated_name.pdf"
}
```

#### Delete Artifact
```http
DELETE /artifacts/{artifact_id}
Authorization: Bearer <access_token>
```

#### Download Artifact
```http
GET /artifacts/{artifact_id}/download
Authorization: Bearer <access_token>
```

### Organization Endpoints

#### List Organizations
```http
GET /orgs
Authorization: Bearer <access_token>
```

#### Get Organization
```http
GET /orgs/{org_id}
Authorization: Bearer <access_token>
```

#### Create Organization
```http
POST /orgs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Organization Name"
}
```

#### Update Organization
```http
PUT /orgs/{org_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Organization Name"
}
```

### Share Endpoints

#### List Shares
```http
GET /shares?artifact_id=art123
Authorization: Bearer <access_token>
```

#### Create Share
```http
POST /shares
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "artifact_id": "art123",
  "target_user_id": "user456"
}
```

#### Delete Share
```http
DELETE /shares/{share_id}
Authorization: Bearer <access_token>
```

### Audit Log Endpoints

#### List Audit Logs
```http
GET /audit?skip=0&limit=50
Authorization: Bearer <access_token>
```

#### Get Audit Log Details
```http
GET /audit/{log_id}
Authorization: Bearer <access_token>
```

### Health & Monitoring

#### Health Check
```http
GET /healthz
```

#### Readiness Check
```http
GET /readyz
```

#### Prometheus Metrics
```http
GET /metrics
```

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/test_main.py -v
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration
```

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Structure

- **test_config.py** - Configuration and settings tests
- **test_logging.py** - Logging system tests
- **test_request_context.py** - Request context tests
- **test_observability.py** - Middleware and metrics tests
- **test_main.py** - FastAPI app initialization tests
- **test_database.py** - Database models and session tests
- **test_schemas.py** - Pydantic schema validation tests
- **test_repositories.py** - Data repository tests
- **test_services.py** - Service layer tests
- **test_security_utils.py** - Security function tests
- **test_api_endpoints.py** - API endpoint tests
- **test_integration.py** - Cross-module integration tests

**Current Coverage:** 62% with 286 passing tests

## 🗄️ Database Schema

### User Table
```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Organization Table
```sql
CREATE TABLE organization (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  owner_id UUID NOT NULL REFERENCES "user"(id),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Artifact Table
```sql
CREATE TABLE artifact (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  owner_id UUID NOT NULL REFERENCES "user"(id),
  org_id UUID NOT NULL REFERENCES organization(id),
  size_bytes BIGINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Share Table
```sql
CREATE TABLE share (
  id UUID PRIMARY KEY,
  artifact_id UUID NOT NULL REFERENCES artifact(id),
  target_user_id UUID NOT NULL REFERENCES "user"(id),
  created_by UUID NOT NULL REFERENCES "user"(id),
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### AuditLog Table
```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  action VARCHAR(50) NOT NULL,
  user_id UUID NOT NULL REFERENCES "user"(id),
  artifact_id UUID REFERENCES artifact(id),
  resource_type VARCHAR(100),
  resource_id VARCHAR(255),
  details JSONB,
  ip_address VARCHAR(45),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### RefreshToken Table
```sql
CREATE TABLE refresh_token (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES "user"(id),
  token_hash VARCHAR(255) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 Security

### Best Practices Implemented

1. **Password Security**
   - Bcrypt hashing with configurable rounds (default: 12)
   - Salt generation automatic with each hash
   - Password never stored in plain text

2. **Authentication**
   - JWT tokens with expiration (access: 30 min, refresh: 7 days)
   - Refresh token rotation on use
   - Token revocation support

3. **Authorization**
   - Role-based access control (RBAC)
   - Permission validation on all endpoints
   - Organization isolation

4. **Rate Limiting**
   - Login attempt rate limiting
   - Configurable rate limits per operation
   - IP-based tracking

5. **API Security**
   - CORS configuration
   - HTTPS/TLS enforcement in production
   - Secure headers configuration

6. **Data Protection**
   - Request/response logging (sensitive data masked)
   - Audit trail for all operations
   - Secure file storage

7. **Infrastructure Security**
   - Non-root user in Docker
   - Environment variable isolation
   - Database user with minimal permissions

### Security Headers

The application should be deployed behind a reverse proxy (nginx, AWS ALB, etc.) that adds:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Environment Security

Never commit sensitive information:
- `.env` file (add to `.gitignore`)
- Private keys
- Database passwords
- API tokens

## 📦 Deployment

### Docker Deployment

#### Build Image
```bash
docker build -t secure-artifact-vault:latest .
```

#### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/vault \
  -e JWT_SECRET_KEY=your-secret-key \
  secure-artifact-vault:latest
```

#### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-artifact-vault
spec:
  replicas: 3
  selector:
    matchLabels:
      app: secure-artifact-vault
  template:
    metadata:
      labels:
        app: secure-artifact-vault
    spec:
      containers:
      - name: api
        image: secure-artifact-vault:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: vault-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: vault-secrets
              key: jwt-secret
```

### AWS ECS Deployment

Push to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag secure-artifact-vault:latest <account>.dkr.ecr.us-east-1.amazonaws.com/secure-artifact-vault:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/secure-artifact-vault:latest
```

### Reverse Proxy Configuration (Nginx)

```nginx
upstream api {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    
    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring in Production

1. **Prometheus Metrics**
   - Metrics endpoint: `/metrics`
   - Integration with Prometheus scraper

2. **Application Logging**
   - Structured JSON logging
   - Centralized log aggregation (ELK, Splunk, etc.)

3. **Health Checks**
   - `/healthz` - Application health
   - `/readyz` - Readiness probe
   - Configure Kubernetes probes

4. **Distributed Tracing** (Optional)
   - Request ID tracking
   - OpenTelemetry integration

## 📁 Project Structure

```
secure-artifact-vault/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management endpoints
│   │   │   ├── artifacts.py    # Artifact endpoints
│   │   │   ├── orgs.py         # Organization endpoints
│   │   │   ├── shares.py       # Sharing endpoints
│   │   │   ├── audit.py        # Audit log endpoints
│   │   │   └── health.py       # Health check endpoints
│   │   ├── deps.py             # Dependency injection
│   │   └── metrics.py          # Prometheus metrics
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   ├── security.py         # Security utilities (JWT, hashing)
│   │   ├── logging.py          # Logging configuration
│   │   ├── permissions.py      # RBAC definitions
│   │   ├── rate_limiter.py     # Rate limiting logic
│   │   ├── request_context.py  # Request context variables
│   │   └── observability.py    # Metrics collection
│   ├── db/
│   │   ├── base.py             # SQLAlchemy base
│   │   ├── session.py          # Database session management
│   │   └── models/
│   │       ├── user.py
│   │       ├── organization.py
│   │       ├── artifact.py
│   │       ├── share.py
│   │       ├── audit_log.py
│   │       ├── refresh_token.py
│   │       └── user_org_role.py
│   ├── schemas/                # Pydantic models
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── artifact.py
│   │   ├── share.py
│   │   ├── org.py
│   │   └── audit.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── artifact_service.py
│   │   ├── share_service.py
│   │   ├── org_service.py
│   │   └── audit_service.py
│   ├── repositories/           # Data access layer
│   │   ├── user_repo.py
│   │   ├── artifact_repo.py
│   │   ├── share_repo.py
│   │   ├── audit_repo.py
│   │   ├── org_repo.py
│   │   ├── user_org_role_repo.py
│   │   └── refresh_token_repo.py
│   ├── middleware/
│   │   └── observability.py    # Request middleware
│   ├── utils/
│   │   └── __init__.py
│   └── cron/                   # Scheduled tasks
├── alembic/                    # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_*.py              # Test files
│   └── htmlcov/               # Coverage reports
├── scripts/
│   └── seed_data.py           # Initial data seeding
├── storage/                    # File storage
├── htmlcov/                    # Coverage reports
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── LICENSE                     # License file
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dependencies: `pip install -r requirements.txt`
4. Create tests for new features
5. Run tests: `pytest tests/ --cov=app`
6. Commit with descriptive messages: `git commit -am 'Add new feature'`
7. Push to branch: `git push origin feature/my-feature`
8. Create Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Document public functions with docstrings
- Keep functions focused and small

### Testing Requirements

- All new features must have tests
- Maintain or improve code coverage
- All tests must pass before PR merge
- Use fixtures from `conftest.py` for common setup

### Commit Message Format

```
type(scope): subject

body

footer
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(auth): add two-factor authentication

Implement TOTP-based 2FA for user accounts.

Closes #123
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: See API docs at `/docs`
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@example.com

### Common Issues

#### Database Connection Error
```
Error: could not translate host name "db" to address
```
Solution: Ensure PostgreSQL is running and DATABASE_URL is correct.

#### JWT Token Expired
```
Error: Invalid or expired token
```
Solution: Use the refresh endpoint to get a new access token.

#### File Upload Size Exceeded
```
Error: File too large
```
Solution: Check `MAX_UPLOAD_SIZE_MB` configuration.

## 🗺️ Roadmap

- [ ] Two-factor authentication (2FA)
- [ ] OAuth2/OIDC integration
- [ ] WebSocket support for real-time updates
- [ ] S3 backend support
- [ ] Mobile app
- [ ] Advanced search and filtering
- [ ] API key authentication
- [ ] Webhook support
- [ ] Batch export/import
- [ ] Full-text search

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial release
- User authentication and management
- Artifact storage and sharing
- Organization management
- Complete audit logging
- Prometheus metrics
- Comprehensive test suite (286 tests, 62% coverage)

---

**secure artifact management**

For the latest updates and more information, visit the [GitHub Repository](https://github.com/rajatagarwalm/secure_artifact_vault)
