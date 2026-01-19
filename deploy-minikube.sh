#!/bin/bash
##############################################################################
# Secure Artifact Vault - Minikube Deployment Script
# This script automates the entire deployment process on Minikube
##############################################################################

set -e

# Functions
log_info() {
    echo "[INFO] $1"
}

log_warn() {
    echo "[WARN] $1"
}

log_error() {
    echo "[ERROR] $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v minikube &> /dev/null; then
        log_error "Minikube is not installed"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    log_info "All prerequisites met"
}

# Clean up
cleanup() {
    log_info "Cleaning up previous deployment..."
    minikube delete || true
}

# Start minikube
start_minikube() {
    log_info "Starting Minikube..."
    minikube start --driver=docker
    log_info "Minikube started"
}

# Configure docker
configure_docker() {
    log_info "Configuring Docker environment..."
    eval $(minikube docker-env)
    log_info "Docker environment configured"
}

# Build image
build_image() {
    log_info "Building Docker image..."
    docker build -t secure-artifact-vault:latest .
    log_info "Docker image built"
}

# Create namespace
create_namespace() {
    log_info "Creating Kubernetes namespace..."
    kubectl create namespace artifact-vault
    kubectl config set-context --current --namespace=artifact-vault
    log_info "Namespace created"
}

# Create secrets
create_secrets() {
    log_info "Creating secrets..."
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: vault-secrets
  namespace: artifact-vault
type: Opaque
stringData:
  DATABASE_URL: "postgresql://artifact_user:artifact_pass@postgres:5432/artifact_vault"
  JWT_SECRET_KEY: "dev-secret-key-minikube-change-in-production"
  DB_USER: "artifact_user"
  DB_PASSWORD: "artifact_pass"
EOF
    log_info "Secrets created"
}

# Create PVCs
create_pvcs() {
    log_info "Creating Persistent Volume Claims..."
    kubectl apply -f k8s/postgres-pvc.yaml
    kubectl apply -f k8s/artifact-pvc.yaml
    log_info "PVCs created"
}

# Deploy PostgreSQL
deploy_postgres() {
    log_info "Deploying PostgreSQL..."
    kubectl apply -f k8s/postgres.yaml
    
    log_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
    log_info "PostgreSQL deployed and ready"
}

# Deploy application
deploy_application() {
    log_info "Deploying Secure Artifact Vault application..."
    kubectl apply -f k8s/api.yaml
    kubectl apply -f k8s/api-service.yaml
    
    log_info "Waiting for application to be ready..."
    kubectl wait --for=condition=ready pod -l app=vault-api --timeout=300s
    log_info "Application deployed and ready"
}

# Print access info
print_access_info() {
    log_info "Deployment complete!"
    
    MINIKUBE_IP=$(minikube ip)
    NODEPORT=$(kubectl get service vault-api-service -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "N/A")
    
    echo ""
    echo "==============================================="
    echo "Application Access Information"
    echo "==============================================="
    echo "Minikube IP:        $MINIKUBE_IP"
    echo "Service Port:       80"
    echo "NodePort:           $NODEPORT"
    echo ""
    echo "Application URL:    http://$MINIKUBE_IP:$NODEPORT"
    echo "Swagger UI:         http://$MINIKUBE_IP:$NODEPORT/docs"
    echo "Health Check:       http://$MINIKUBE_IP:$NODEPORT/healthz"
    echo ""
    echo "Alternative (Port Forwarding):"
    echo "  kubectl port-forward svc/vault-api-service 8000:80"
    echo "  Then access: http://localhost:8000"
    echo "==============================================="
    echo ""
}

# Main execution
main() {
    log_info "Starting Secure Artifact Vault Minikube deployment..."
    echo ""
    
    check_prerequisites
    cleanup
    start_minikube
    configure_docker
    build_image
    create_namespace
    create_secrets
    kubectl apply -f k8s/configmap.yaml || true
    create_pvcs
    deploy_postgres
    deploy_application
    print_access_info
    
    log_info "Deployment successful!"
}

# Run main
main
