# Secure Artifact Vault

A production-ready secure file storage and sharing system built with FastAPI, PostgreSQL, and modern security practices.

## Table of Contents

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

## Overview

Secure Artifact Vault is a comprehensive file storage and management system designed for organizations that need secure, auditable artifact storage with fine-grained access control. It provides features for user authentication, organization management, artifact storage, sharing capabilities, and complete audit logging.

**Key Characteristics:**
- REST API-first design
- JWT-based authentication
- Role-based access control (RBAC)
- Complete audit trail
- Prometheus metrics
- Production-ready Docker deployment

## Features

### Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Rate limiting** on login attempts
- **User management** with activation/deactivation
- **Role-based access control** (RBAC) with permissions
- **Organization hierarchy** with user-org-role mapping
- **Password management** with expiration and history tracking
- **Temporary password generation** for admin-created users
- **Password change enforcement** for expired passwords
- **Password history** to prevent reuse

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

## Architecture

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

## Installation

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

## Running the Application

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

## API Documentation

All APIs require JWT authentication unless otherwise noted.

### Authentication Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and invalidate session
- `GET /api/v1/auth/me` - Get current user information
- `GET /api/v1/auth/permissions` - Get current user permissions

### User Management Endpoints

- `GET /api/v1/users` - List all users
- `POST /api/v1/users` - Create new user with default temporary password (superadmin only)
- `POST /api/v1/users/assign-org` - Assign user to organization with role
- `POST /api/v1/users/change-password` - Change own password (user)
- `POST /api/v1/users/reset-password` - Reset user password (superadmin only)
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

## Testing

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

## Database Schema

The application uses PostgreSQL with the following tables:

- **users** - User accounts and authentication
- **organizations** - Organizational units for multi-tenancy
- **user_org_roles** - User-organization role mappings
- **artifacts** - File storage with metadata
- **shares** - Artifact sharing between users
- **audit_logs** - Complete operation audit trail
- **refresh_tokens** - Token management for sessions

## Security

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

## Deployment

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

### Local Kubernetes Deployment (Minikube) - Fresh Setup

Deploy Secure Artifact Vault on a clean local Kubernetes cluster using Minikube.

#### Prerequisites
- Docker installed and running
- Minikube installed (`brew install minikube` on macOS or follow [official guide](https://minikube.sigs.k8s.io/docs/start/))
- kubectl CLI configured
- Git for cloning repository

---

#### **AUTOMATED DEPLOYMENT (Recommended)**

The easiest way to deploy - runs everything automatically in one command!

##### Deployment Script Overview

The `deploy-minikube.sh` script automates the entire deployment process:

**Script Location:** `./deploy-minikube.sh`

**What it does:**
- Validates prerequisites (Docker, Minikube, kubectl)
- Deletes existing Minikube cluster for clean slate
- Starts fresh Minikube instance with Docker driver
- Builds Docker image for the application
- Creates Kubernetes namespace (`artifact-vault`)
- Sets up secrets for database credentials and JWT tokens
- Creates persistent volumes for database and artifacts
- Deploys PostgreSQL database
- Runs database migrations automatically
- Seeds initial data (organizations, users, etc.)
- Deploys FastAPI application (3 replicas)
- Displays access information and URLs

##### One-Command Deployment

```bash
# 1. Clone repository
git clone <YOUR_GITHUB_REPO_URL>
cd secure-artifact-vault

# 2. Make script executable and run
chmod +x deploy-minikube.sh
./deploy-minikube.sh
```

**That's it!** The script will handle everything automatically.

**Expected time:** ~3-5 minutes (first run takes longer due to Docker image build)

**Script output example:**
```
[INFO] Starting Secure Artifact Vault Minikube deployment...
[INFO] Checking prerequisites...
[INFO] All prerequisites met
[INFO] Starting Minikube...
[INFO] Minikube started
[INFO] Building Docker image...
[INFO] Docker image built
[INFO] Creating Kubernetes namespace...
[INFO] Namespace created
[INFO] Deploying PostgreSQL...
[INFO] PostgreSQL deployed and ready
[INFO] Deploying Secure Artifact Vault application...
[INFO] Application deployed and ready

===============================================
Application Access Information
===============================================
Minikube IP:        192.168.58.2
Service Port:       80
NodePort:           31234

Application URL:    http://192.168.58.2:31234
Swagger UI:         http://192.168.58.2:31234/docs
Health Check:       http://192.168.58.2:31234/healthz

Alternative (Port Forwarding):
  kubectl port-forward svc/vault-api-service 8000:80
  Then access: http://localhost:8000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

##### Access the Application

Once deployment completes, access the application:

1. **Swagger UI (Interactive API docs):** `http://<minikube-ip>:<nodeport>/docs`
2. **Health Check:** `http://<minikube-ip>:<nodeport>/healthz`
3. **Metrics:** `http://<minikube-ip>:<nodeport>/metrics` (Prometheus)

##### Port Forwarding (Alternative Access)

```bash
kubectl port-forward svc/vault-api-service 8000:80 -n artifact-vault
# Then access: http://localhost:8000
```

---

#### **For Detailed Reference**

For step-by-step instructions and troubleshooting, see [DEPLOYMENT.md](./DEPLOYMENT.md)

Key sections:
- Manual step-by-step deployment
- Accessing the application
- Useful kubectl commands
- Troubleshooting guide
- Cleanup procedures

---

#### **Quick Start (Complete Fresh Deployment - Manual)**

If you prefer manual control or the script doesn't work, follow these steps:

```bash
# 1. Clone and navigate
git clone <YOUR_GITHUB_REPO_URL>
cd secure-artifact-vault

# 2. Clean previous setup (if exists)
minikube delete
minikube start --driver=docker

# 3. Configure Docker environment
eval $(minikube docker-env)

# 4. Build application image
docker build -t secure-artifact-vault:latest .

# 5. Create namespace
kubectl create namespace artifact-vault

# 6. Set default namespace
kubectl config set-context --current --namespace=artifact-vault

# 7. Create secrets
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: vault-secrets
  namespace: artifact-vault
type: Opaque
stringData:
  database-url: "postgresql://artifact_user:artifact_pass@postgres:5432/artifact_vault"
  jwt-secret-key: "local-development-secret-key-change-in-production"
  postgres-password: "artifact_pass"
EOF

# 8. Create PersistentVolumeClaims
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/artifact-pvc.yaml

# 9. Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# 10. Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# 11. Deploy Application
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/api-service.yaml

# 12. Wait for application to be ready
kubectl wait --for=condition=ready pod -l app=secure-artifact-vault --timeout=300s

# 13. Check all resources
kubectl get all -n artifact-vault

# 14. Get service details
kubectl get service vault-service -n artifact-vault
```

---

#### **Detailed Manual Step-by-Step Instructions**

For comprehensive step-by-step instructions with explanations for each step, see [DEPLOYMENT.md](./DEPLOYMENT.md)

Quick reference of key steps below:

**Step 1: Clean Minikube (Fresh Start)**
```bash
# Stop and delete any existing minikube cluster
minikube delete
```

**Step 2: Start Fresh Minikube Cluster**
```bash
minikube start --driver=docker
# Expected output:
# minikube v1.x.x on Darwin
# Using the docker driver
# Starting control plane node minikube in cluster minikube
# Done! kubectl is now configured to use "minikube" cluster
```

**Step 3: Configure Docker Environment**
```bash
eval $(minikube docker-env)
```

**Step 4: Build Docker Image**
```bash
docker build -t secure-artifact-vault:latest .
# Verify image was built
docker images | grep secure-artifact-vault
```

**Step 5: Create Kubernetes Namespace**
```bash
kubectl create namespace artifact-vault
# Verify namespace created
kubectl get namespaces
```

**Step 6: Set Default Namespace**
```bash
kubectl config set-context --current --namespace=artifact-vault
# Verify context
kubectl config current-context
```

**Step 7: Create Secrets**

Create secrets inline:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: vault-secrets
  namespace: artifact-vault
type: Opaque
stringData:
  database-url: "postgresql://artifact_user:artifact_pass@postgres:5432/artifact_vault"
  jwt-secret-key: "dev-secret-key-12345-change-in-production"
  postgres-password: "artifact_pass"
EOF
```

Or create file `k8s/secret.local.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vault-secrets
  namespace: artifact-vault
type: Opaque
stringData:
  database-url: "postgresql://artifact_user:artifact_pass@postgres:5432/artifact_vault"
  jwt-secret-key: "dev-secret-key-12345-change-in-production"
  postgres-password: "artifact_pass"
```

Then apply:
```bash
kubectl apply -f k8s/secret.local.yaml
```

**Step 8: Apply ConfigMap**
```bash
kubectl apply -f k8s/configmap.yaml
# Verify
kubectl get configmap
```

**Step 9: Create Persistent Volume Claims**
```bash
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/artifact-pvc.yaml

# Verify PVCs created
kubectl get pvc
```

**Step 10: Deploy PostgreSQL Database**
```bash
kubectl apply -f k8s/postgres.yaml

# Watch PostgreSQL startup
kubectl get pods -w
# Wait for postgres pod to be Running and Ready (1/1)
```

**Step 11: Deploy FastAPI Application**
```bash
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/api-service.yaml

# Watch application startup
kubectl get pods -w
# Wait for secure-artifact-vault pods to be Running and Ready (1/1)
```

**Step 12: Verify All Resources**
```bash
# Check all pods
kubectl get pods
# Expected:
# NAME                                     READY   STATUS    RESTARTS   AGE
# postgres-xxxxxxxxx-xxxxx                 1/1     Running   0          2m
# secure-artifact-vault-xxxxxxxxx-xxxxx    1/1     Running   0          1m
# secure-artifact-vault-xxxxxxxxx-xxxxx    1/1     Running   0          1m
# secure-artifact-vault-xxxxxxxxx-xxxxx    1/1     Running   0          1m

# Check services
kubectl get service
# Expected:
# NAME            TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)
# vault-service   NodePort   10.x.x.x         <none>        80:xxxxx/TCP
# postgres        ClusterIP  10.x.x.x         <none>        5432/TCP
```

**Step 13: Access the Application**

Get Minikube IP and NodePort:
```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Get NodePort
NODEPORT=$(kubectl get service vault-service -o jsonpath='{.spec.ports[0].nodePort}')
echo "NodePort: $NODEPORT"

# Full URL
echo "Application URL: http://$MINIKUBE_IP:$NODEPORT"
```

Access via browser or curl:
```bash
# Health check
curl http://$(minikube ip):$(kubectl get service vault-service -o jsonpath='{.spec.ports[0].nodePort}')/healthz

# Swagger UI
# Open: http://<minikube-ip>:<node-port>/docs

# Readiness check
curl http://$(minikube ip):$(kubectl get service vault-service -o jsonpath='{.spec.ports[0].nodePort}')/readyz
```

#### Port Forwarding (Alternative Access Method)

If NodePort doesn't work, use port forwarding:
```bash
# Forward local port 8000 to service
kubectl port-forward svc/vault-service 8000:80

# Access via localhost
curl http://localhost:8000/healthz
# Open browser: http://localhost:8000/docs
```

#### Viewing Logs

```bash
# View specific pod logs
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>

# View logs for all pods in deployment
kubectl logs -f deployment/secure-artifact-vault

# View PostgreSQL logs
kubectl logs -f deployment/postgres
```

#### Useful Minikube Commands

```bash
# View Minikube dashboard (opens browser)
minikube dashboard

# SSH into Minikube node
minikube ssh

# Check Minikube status
minikube status

# View resource usage
kubectl top nodes
kubectl top pods

# Describe resources
kubectl describe pod <pod-name>
kubectl describe service vault-service

# Execute commands in pod
kubectl exec -it <pod-name> -- bash

# Copy files to/from pod
kubectl cp <pod-name>:/path/to/file ./local-path
kubectl cp ./local-path <pod-name>:/path/to/file

# Stop Minikube
minikube stop

# Delete Minikube cluster (fresh start)
minikube delete
```

#### Cleaning Up

To completely remove and start fresh:
```bash
# Delete all resources in namespace
kubectl delete namespace artifact-vault

# Stop Minikube
minikube stop

# Delete entire Minikube cluster
minikube delete

# Then restart from Step 1
```

#### Troubleshooting

**Pods not starting:**
```bash
# Check pod status and events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Check events in namespace
kubectl get events -n artifact-vault
```

**Database connection failed:**
```bash
# Check PostgreSQL pod
kubectl get pod -l app=postgres
kubectl logs -f postgres-xxxxx

# Check if database is accepting connections
kubectl exec -it postgres-xxxxx -- psql -U artifact_user -d artifact_vault
```

**Service not accessible:**
```bash
# Check service
kubectl get service vault-service
kubectl describe service vault-service

# Check if pods are ready
kubectl get pods -l app=secure-artifact-vault
```

**Image pull errors:**
```bash
# Ensure you built the image with minikube docker-env
eval $(minikube docker-env)
docker build -t secure-artifact-vault:latest .

# Verify image exists
docker images
```

**Out of resources:**
```bash
# Check resource allocation
kubectl describe nodes

# Restart with more resources
minikube delete
minikube start --driver=docker --cpus 4 --memory 4096
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

## Project Structure

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
│   │       ├── user_org_role.py
│   │       └── password_history.py
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
│   │   ├── refresh_token_repo.py
│   │   └── password_history_repo.py  
│   ├── middleware/
│   │   └── observability.py    # Request middleware
│   ├── utils/
│   │   ├── pagination.py
│   │   ├── time.py
│   │   ├── uuid.py
│   │   └── __init__.py
│   └── cron/                   # Scheduled tasks
│       └── cleanup.py
├── alembic/                    # Database migrations
│   ├── versions/
│   │   ├── 72ecff915d9c_create_core_tables.py
│   │   ├── 9c56c0487ed3_initial_empty_migration.py
│   │   ├── 9c6d17c204ca_add_checksum_to_artifacts.py
│   │   ├── 1398671fa5d5_add_prefix_search_index_on_artifacts.py
│   │   ├── abc123def456_add_password_expires_at_to_users.py
│   │   └── def456abc789_add_user_password_history_table.py
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── k8s/                        # Kubernetes manifests
│   ├── api.yaml                # API deployment
│   ├── api-service.yaml        # API service
│   ├── postgres.yaml           # PostgreSQL deployment
│   ├── postgres-pvc.yaml       # PostgreSQL persistent volume
│   ├── artifact-pvc.yaml       # Artifact storage persistent volume
│   ├── configmap.yaml          # ConfigMap for environment
│   └── secret.yaml             # Secrets template
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_*.py              # Test files (12+ test modules)
│   ├── test_additional_coverage.py
│   ├── test_api_endpoints.py
│   ├── test_api_endpoints_extended.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_integration.py
│   ├── test_logging.py
│   ├── test_main.py
│   ├── test_observability.py
│   ├── test_repositories.py
│   ├── test_request_context.py
│   ├── test_schemas.py
│   ├── test_security_utils.py
│   ├── test_services.py
│   └── README.md
├── scripts/
│   └── seed_data.py           # Initial data seeding
├── storage/                    # File storage
│   └── artifacts/             # Artifact storage directory
├── alembic.ini                 # Alembic configuration
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── entrypoint.sh               # Docker entrypoint script
├── deploy-minikube.sh          # Automated Minikube deployment script
├── run_tests.sh                # Test execution script
├── .env                        # Environment variables (local)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── DEPLOYMENT.md               # Deployment guide and troubleshooting
├── README.md                   # This file
└── LICENSE                     # License file
```

**secure artifact management**

For the latest updates and more information, visit the [GitHub Repository](https://github.com/rajatagarwalm/secure_artifact_vault)
