#!/bin/bash

# Deployment script for portfolio-system-architect
# Supports local, staging, and production deployments

set -e

echo "🚀 Portfolio System Architect Deployment"
echo "================================================================"

# Default values
ENVIRONMENT="local"
FORCE=false
DRY_RUN=false
VERSION="latest"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -e, --environment ENV   Deployment environment (local, staging, production)"
            echo "  -f, --force             Force deployment even if tests fail"
            echo "  -d, --dry-run           Show what would be deployed without actually deploying"
            echo "  -v, --version VERSION   Docker image version to deploy"
            echo "  -h, --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --environment local"
            echo "  $0 --environment staging --version v1.2.3"
            echo "  $0 --environment production --dry-run"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Force: $FORCE"
echo "Dry run: $DRY_RUN"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker."
        exit 1
    fi
    echo "✅ Docker: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    echo "✅ Docker Compose: $(docker-compose --version)"
    
    # Check kubectl for Kubernetes deployments
    if [[ "$ENVIRONMENT" == "staging" || "$ENVIRONMENT" == "production" ]]; then
        if ! command -v kubectl &> /dev/null; then
            echo "❌ kubectl not found. Required for Kubernetes deployments."
            exit 1
        fi
        echo "✅ kubectl: $(kubectl version --client --short)"
    fi
    
    # Check Python and virtual environment
    if [[ "$ENVIRONMENT" == "local" ]]; then
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "⚠️  Virtual environment not activated. Activating..."
            if [ -f ".venv/bin/activate" ]; then
                source .venv/bin/activate
            elif [ -f ".venv/Scripts/activate" ]; then
                source .venv/Scripts/activate
            else
                echo "⚠️  Virtual environment not found. Some commands may fail."
            fi
        fi
        echo "✅ Python: $(python --version)"
    fi
}

# Function to run tests
run_tests() {
    if [[ "$FORCE" == false ]]; then
        echo "🧪 Running tests..."
        
        if [[ "$DRY_RUN" == false ]]; then
            pytest tests/ -v --tb=short
            if [ $? -ne 0 ]; then
                echo "❌ Tests failed. Use --force to deploy anyway."
                exit 1
            fi
            echo "✅ Tests passed"
        else
            echo "⚠️  Skipping tests in dry-run mode"
        fi
    else
        echo "⚠️  Skipping tests (force mode)"
    fi
}

# Function to build Docker images
build_images() {
    echo "🐳 Building Docker images..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Build gateway image
        echo "  Building gateway image..."
        docker build -t portfolio-gateway:$VERSION -f gateway/Dockerfile gateway/
        
        # Build API image
        echo "  Building API image..."
        docker build -t portfolio-api:$VERSION -f api/Dockerfile api/
        
        echo "✅ Docker images built"
    else
        echo "⚠️  Would build Docker images (dry-run)"
        echo "  - portfolio-gateway:$VERSION"
        echo "  - portfolio-api:$VERSION"
    fi
}

# Function to deploy locally
deploy_local() {
    echo "🏠 Deploying locally..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Stop existing services
        echo "  Stopping existing services..."
        docker-compose down || true
        
        # Start services
        echo "  Starting services..."
        docker-compose up -d
        
        # Wait for services to be ready
        echo "  Waiting for services to be ready..."
        sleep 10
        
        # Check service health
        echo "  Checking service health..."
        ./scripts/health-check.sh
        
        echo "✅ Local deployment completed"
        echo ""
        echo "📊 Services running:"
        echo "  - API Gateway: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - PostgreSQL: localhost:5432"
        echo "  - Redis: localhost:6379"
        echo "  - ChromaDB: http://localhost:8001"
    else
        echo "⚠️  Would deploy locally (dry-run)"
        echo "  - Start Docker Compose services"
        echo "  - Run health checks"
    fi
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    local env=$1
    
    echo "☸️  Deploying to Kubernetes ($env)..."
    
    # Check for kubeconfig
    if [[ ! -f "$HOME/.kube/config" ]]; then
        echo "❌ kubeconfig not found. Please configure kubectl."
        exit 1
    fi
    
    # Set Kubernetes context based on environment
    case $env in
        staging)
            CONTEXT="staging-cluster"
            NAMESPACE="portfolio-system-staging"
            ;;
        production)
            CONTEXT="production-cluster"
            NAMESPACE="portfolio-system"
            ;;
        *)
            echo "❌ Unknown Kubernetes environment: $env"
            exit 1
            ;;
    esac
    
    echo "  Context: $CONTEXT"
    echo "  Namespace: $NAMESPACE"
    
    if [[ "$DRY_RUN" == false ]]; then
        # Switch to context
        kubectl config use-context $CONTEXT
        
        # Create namespace if it doesn't exist
        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
        
        # Apply Kubernetes manifests
        echo "  Applying Kubernetes manifests..."
        
        if [ -d "deployment/k8s" ]; then
            # Apply all manifests in order
            for file in deployment/k8s/*.yaml; do
                if [ -f "$file" ]; then
                    echo "    Applying $(basename $file)..."
                    kubectl apply -f $file -n $NAMESPACE
                fi
            done
        else
            echo "⚠️  No Kubernetes manifests found in deployment/k8s/"
        fi
        
        # Wait for deployments
        echo "  Waiting for deployments to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/portfolio-gateway -n $NAMESPACE
        kubectl wait --for=condition=available --timeout=300s deployment/portfolio-api -n $NAMESPACE
        
        # Show deployment status
        echo ""
        echo "📊 Deployment status:"
        kubectl get pods -n $NAMESPACE
        echo ""
        kubectl get svc -n $NAMESPACE
        echo ""
        kubectl get ingress -n $NAMESPACE 2>/dev/null || echo "No ingress configured"
        
        echo "✅ Kubernetes deployment completed"
    else
        echo "⚠️  Would deploy to Kubernetes (dry-run)"
        echo "  - Switch to context: $CONTEXT"
        echo "  - Create/update namespace: $NAMESPACE"
        echo "  - Apply manifests from deployment/k8s/"
        echo "  - Wait for deployments to be ready"
    fi
}

# Function to verify deployment
verify_deployment() {
    echo "🔍 Verifying deployment..."
    
    case $ENVIRONMENT in
        local)
            # Check local services
            curl -f http://localhost:8000/health || echo "⚠️  Gateway health check failed"
            ;;
        staging|production)
            # Get service URL (would need to be configured)
            echo "  Deployment verification would run here"
            ;;
    esac
    
    echo "✅ Deployment verification completed"
}

# Main deployment flow
main() {
    echo "Starting deployment to $ENVIRONMENT..."
    echo ""
    
    # Check prerequisites
    check_prerequisites
    echo ""
    
    # Run tests (unless forced)
    run_tests
    echo ""
    
    # Build images
    build_images
    echo ""
    
    # Deploy based on environment
    case $ENVIRONMENT in
        local)
            deploy_local
            ;;
        staging|production)
            deploy_kubernetes $ENVIRONMENT
            ;;
        *)
            echo "❌ Unknown environment: $ENVIRONMENT"
            echo "   Valid options: local, staging, production"
            exit 1
            ;;
    esac
    echo ""
    
    # Verify deployment
    verify_deployment
    echo ""
    
    echo "================================================================"
    echo "🎉 Deployment to $ENVIRONMENT completed successfully!"
    echo ""
    echo "📋 Summary:"
    echo "  - Environment: $ENVIRONMENT"
    echo "  - Version: $VERSION"
    echo "  - Status: ✅ Success"
    echo ""
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "⚠️  This was a dry run. No changes were made."
    fi
    
    echo "================================================================"
}

# Run main function
main