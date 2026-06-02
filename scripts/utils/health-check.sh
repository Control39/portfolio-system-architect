#!/bin/bash

# Health check script for portfolio-system-architect services

echo "🏥 Health Check for portfolio-system-architect"
echo "================================================================"
echo "Timestamp: $(date)"
echo ""

# Check Docker services
echo "1. Docker Services Status:"
echo "--------------------------"
docker-compose -f docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "2. Service Health Endpoints:"
echo "---------------------------"

# Define services to check
declare -A services=(
    ["API Gateway"]="http://localhost:8000/health"
    ["PostgreSQL"]="localhost:5432"
    ["Redis"]="localhost:6379"
    ["ChromaDB"]="http://localhost:8001/api/v1/heartbeat"
    ["Prometheus"]="http://localhost:9090/-/healthy"
    ["Grafana"]="http://localhost:3000/api/health"
)

# Check each service
for service in "${!services[@]}"; do
    endpoint=${services[$service]}

    echo -n "   $service: "

    if [[ $endpoint == http* ]]; then
        # HTTP endpoint
        if curl -s --max-time 5 "$endpoint" > /dev/null; then
            echo "✅ Healthy"
        else
            echo "❌ Unreachable"
        fi
    else
        # TCP endpoint (host:port)
        host=$(echo $endpoint | cut -d: -f1)
        port=$(echo $endpoint | cut -d: -f2)

        if nc -z -w5 "$host" "$port" 2>/dev/null; then
            echo "✅ Healthy"
        else
            echo "❌ Unreachable"
        fi
    fi
done

echo ""
echo "3. System Resources:"
echo "-------------------"

# Check memory usage
echo -n "   Memory usage: "
free -h | awk '/^Mem:/ {print $3 "/" $2 " (" $3/$2*100 "%)"}'

# Check disk usage
echo -n "   Disk usage: "
df -h . | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}'

# Check CPU load
echo -n "   CPU load: "
uptime | awk -F'load average:' '{print $2}'

echo ""
echo "4. Python Virtual Environment:"
echo "-----------------------------"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "   ✅ Active: $VIRTUAL_ENV"
    echo "   Python: $(python --version)"
else
    echo "   ⚠️  Not active"
fi

echo ""
echo "5. Recent Errors (last 10 lines):"
echo "--------------------------------"
docker-compose -f docker-compose.yml logs --tail=10 2>/dev/null | grep -i "error\|fail\|exception" || echo "   No recent errors found"

echo ""
echo "================================================================"
echo "📊 Health Summary:"
echo ""
echo "To fix common issues:"
echo "1. If Docker services are down: ./scripts/start-all.sh"
echo "2. If virtual environment not active: source .venv/bin/activate"
echo "3. If ports are busy: ./scripts/stop-all.sh and restart"
echo "4. Check logs: docker-compose logs [service-name]"
echo ""
echo "For more details, check individual service logs."
echo "================================================================"
