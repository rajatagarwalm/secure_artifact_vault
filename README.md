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
  - [Docker Deployment](#docker-deployment)
  - [Local Kubernetes Deployment (Minikube)](#local-kubernetes-deployment-minikube)
  - [Kubernetes Deployment](#kubernetes-deployment)
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
git clone https://github.com/rajatagarwalm/secure_artifact_vault
cd secure_artifact_vault
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

All APIs require JWT authentication unless otherwise noted.

### Authentication Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and invalidate session
- `GET /api/v1/auth/me` - Get current user information
- `GET /api/v1/auth/permissions` - Get current user permissions

### User Management Endpoints

- `GET /api/v1/users` - List all users
- `POST /api/v1/users/assign-org` - Assign user to organization with role
- `GET /api/v1/users/{user_id}/permissions` - Get user permissions

### Artifact Management Endpoints

- `POST /api/v1/artifacts/upload` - Upload artifact
- `GET /api/v1/artifacts` - List artifacts in organization
- `GET /api/v1/artifacts/search` - Search artifacts by prefix
- `GET /api/v1/artifacts/{artifact_id}` - Download artifact
- `DELETE /api/v1/artifacts/{artifact_id}` - Delete artifact

### Organization Endpoints

- `GET /api/v1/orgs` - List all organizations
- `POST /api/v1/orgs` - Create new organization
- `DELETE /api/v1/orgs/{org_id}` - Delete organization

### Share Endpoints

- `POST /api/v1/shares` - Create artifact share link
- `GET /api/v1/shares/{share_id}/download` - Download shared artifact

### Audit Log Endpoints

- `GET /api/v1/audit/logs` - Retrieve audit logs with pagination

### Health & Monitoring Endpoints

- `GET /healthz` - Liveness probe (application health)
- `GET /readyz` - Readiness probe (ready to serve traffic)
- `GET /metrics` - Prometheus metrics

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

The application uses PostgreSQL with the following tables:

- **users** - User accounts and authentication
- **organizations** - Organizational units for multi-tenancy
- **user_org_roles** - User-organization role mappings
- **artifacts** - File storage with metadata
- **shares** - Artifact sharing between users
- **audit_logs** - Complete operation audit trail
- **refresh_tokens** - Token management for sessions

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

### Local Kubernetes Deployment (Minikube)

Deploy Secure Artifact Vault on a local Kubernetes cluster using Minikube.

#### Prerequisites
- Docker installed and running
- Minikube installed (`brew install minikube` on macOS or follow [official guide](https://minikube.sigs.k8s.io/docs/start/))
- kubectl CLI configured
- Git for cloning repository

#### Step-by-Step Instructions

**1. Clone Repository**
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd secure-artifact-vault
```

**2. Start Minikube**
```bash
minikube start --driver=docker
```

**3. Configure Docker Daemon**
```bash
eval $(minikube docker-env)
```

**4. Build Application Image**
```bash
docker build -t secure-artifact-vault:latest .
```

**5. Create Kubernetes Namespace**
```bash
kubectl create namespace artifact-vault
kubectl config set-context --current --namespace=artifact-vault
```

**6. Create Local Secrets**
```bash
kubectl apply -f k8s/secret.local.yaml
```

**Note:** Create `k8s/secret.local.yaml` with local development values:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vault-secrets
  namespace: artifact-vault
type: Opaque
stringData:
  database-url: "postgresql://artifact_user:artifact_pass@postgres:5432/artifact_vault"
  jwt-secret-key: "local-development-secret-key-not-for-production"
  postgres-password: "artifact_pass"
```

**7. Apply ConfigMap**
```bash
kubectl apply -f k8s/configmap.yaml
```

**8. Create Persistent Volume Claims**
```bash
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/artifact-pvc.yaml
```

**9. Deploy PostgreSQL**
```bash
kubectl apply -f k8s/postgres.yaml
```

**10. Deploy FastAPI Application**
```bash
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/api-service.yaml
```

**11. Verify Pods Are Running**
```bash
kubectl get pods
```

Expected output:
```
NAME                                       READY   STATUS    RESTARTS   AGE
postgres-0                                 1/1     Running   0          2m
secure-artifact-vault-xxxxxxxxxx-xxxxx     1/1     Running   0          1m
secure-artifact-vault-xxxxxxxxxx-xxxxx     1/1     Running   0          1m
```

**12. Access Application**

Get Minikube IP:
```bash
minikube ip
```

Access via NodePort:
```bash
# Get the NodePort assigned
kubectl get service vault-service -n artifact-vault

# Access application
# Open browser: http://<minikube-ip>:<node-port>
# Or use curl:
curl http://$(minikube ip):<node-port>/healthz
```

#### Useful Minikube Commands

```bash
# View Minikube dashboard
minikube dashboard

# SSH into Minikube
minikube ssh

# View logs
kubectl logs -f deployment/secure-artifact-vault -n artifact-vault

# Port forward for local access
kubectl port-forward svc/vault-service 8000:80 -n artifact-vault

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

#### Troubleshooting

**Pods not starting:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n artifact-vault

# Check logs
kubectl logs <pod-name> -n artifact-vault
```

**Database connection issues:**
```bash
# Verify PostgreSQL pod
kubectl get pods -l app=postgres -n artifact-vault

# Check PostgreSQL logs
kubectl logs postgres-0 -n artifact-vault
```

**Port access issues:**
```bash
# Check if service is running
kubectl get service vault-service -n artifact-vault

# Port forward as alternative
kubectl port-forward svc/vault-service 8000:80 -n artifact-vault

# Then access http://localhost:8000
```

### AWS ECS Deployment

Push to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag secure-artifact-vault:latest <account>.dkr.ecr.us-east-1.amazonaws.com/secure-artifact-vault:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/secure-artifact-vault:latest
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

**secure artifact management**

For the latest updates and more information, visit the [GitHub Repository](https://github.com/rajatagarwalm/secure_artifact_vault)
