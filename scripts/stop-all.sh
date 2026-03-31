#!/bin/bash

# Stop all services for portfolio-system-architect

echo "🛑 Stopping portfolio-system-architect services"
echo "================================================================"

# Stop Docker containers
echo "1. Stopping Docker containers..."
docker-compose -f docker-compose.yml down

# Stop any background Python processes
echo "2. Stopping Python processes..."
if [ -f ".service-pids.txt" ]; then
    while read pid; do
        if kill -0 $pid 2>/dev/null; then
            echo "   Stopping process $pid"
            kill $pid
        fi
    done < .service-pids.txt
    rm -f .service-pids.txt
fi

# Additional cleanup for Python processes
echo "3. Cleaning up remaining processes..."
pkill -f "uvicorn" || true
pkill -f "python.*main" || true

echo ""
echo "✅ All services stopped"
echo ""
echo "To start services again:"
echo "   ./scripts/start-all.sh"
echo ""
echo "To completely reset:"
echo "   docker system prune -a"
echo "================================================================"