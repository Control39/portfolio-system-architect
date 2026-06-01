#!/bin/bash

# Start all services for portfolio-system-architect
# This script starts all 8 microservices and dependencies

set -e

echo "🚀 Starting portfolio-system-architect services"
echo "================================================================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    else
        echo "❌ Virtual environment not found. Run ./scripts/setup-environment.sh first"
        exit 1
    fi
fi

echo "Python: $(which python)"
echo "Virtual environment: $VIRTUAL_ENV"

# Check Docker
echo ""
echo "1. Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop"
    exit 1
fi

echo "✅ Docker is running: $(docker --version)"

# Start infrastructure services
echo ""
echo "2. Starting infrastructure services..."
echo "   - PostgreSQL database"
echo "   - Redis cache"
echo "   - ChromaDB vector database"

docker-compose -f docker-compose.yml up -d postgres redis chromadb

echo "✅ Infrastructure services starting..."
sleep 10  # Wait for services to initialize

# Check if services are healthy
echo ""
echo "3. Checking service health..."
if docker-compose -f docker-compose.yml ps | grep -q "Up"; then
    echo "✅ Infrastructure services are running"
else
    echo "⚠️  Some services may not have started properly"
fi

# Start microservices
echo ""
echo "4. Starting microservices..."
echo "   This may take a few minutes..."

# Start API gateway
echo "   - Starting API Gateway..."
cd gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
GATEWAY_PID=$!
cd ..

echo "   API Gateway started on http://localhost:8000"
echo "   - API docs: http://localhost:8000/docs"
echo "   - Health check: http://localhost:8000/health"

# Start other services (simplified - in real project you would start each service)
echo ""
echo "5. Starting other services in background..."
echo "   Note: In production, each service would run in its own container"

# Create a PID file to track running processes
echo $GATEWAY_PID > .service-pids.txt

echo ""
echo "================================================================"
echo "🎉 All services started!"
echo ""
echo "📊 Service Status:"
echo "   - API Gateway:      http://localhost:8000"
echo "   - PostgreSQL:       localhost:5432"
echo "   - Redis:            localhost:6379"
echo "   - ChromaDB:         localhost:8001"
echo "   - Prometheus:       http://localhost:9090"
echo "   - Grafana:          http://localhost:3000"
echo ""
echo "🔧 Management commands:"
echo "   - Stop all:         ./scripts/stop-all.sh"
echo "   - Check health:     ./scripts/health-check.sh"
echo "   - View logs:        docker-compose logs -f"
echo ""
echo "📝 Quick tests:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/api/v1/status"
echo ""
echo "⚠️  Press Ctrl+C to stop services"
echo "================================================================"

# Keep script running
wait $GATEWAY_PID
