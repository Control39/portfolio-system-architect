#!/bin/bash

# Setup monitoring and alerting for portfolio-system-architect

set -e

echo "📊 Setting up Monitoring and Alerting"
echo "================================================================"

# Default values
SETUP_TYPE="all"  # all, prometheus, grafana, alertmanager, loki
NOTIFICATION_CHANNEL="slack"  # slack, email, telegram, webhook

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            SETUP_TYPE="$2"
            shift 2
            ;;
        -n|--notification)
            NOTIFICATION_CHANNEL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -t, --type TYPE          Setup type: all, prometheus, grafana, alertmanager, loki"
            echo "  -n, --notification CHAN  Notification channel: slack, email, telegram, webhook"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --type all --notification slack"
            echo "  $0 --type grafana"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Setup type: $SETUP_TYPE"
echo "Notification channel: $NOTIFICATION_CHANNEL"
echo ""

# Function to check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker."
        exit 1
    fi
    
    if ! docker ps &> /dev/null; then
        echo "❌ Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    echo "✅ Docker is running"
}

# Function to setup Prometheus
setup_prometheus() {
    echo "📈 Setting up Prometheus..."
    
    # Create Prometheus configuration directory
    mkdir -p monitoring/prometheus
    
    # Create prometheus.yml if it doesn't exist
    if [ ! -f "monitoring/prometheus/prometheus.yml" ]; then
        cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert-rules.yaml"

scrape_configs:
  - job_name: 'portfolio-system'
    static_configs:
      - targets: ['gateway:8000', 'api:8000']
        labels:
          environment: 'development'
          component: 'api'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
        echo "✅ Created Prometheus configuration"
    fi
    
    # Copy alert rules
    if [ -f "monitoring/alert-rules.yaml" ]; then
        cp monitoring/alert-rules.yaml monitoring/prometheus/
        echo "✅ Copied alert rules"
    fi
    
    echo "✅ Prometheus setup completed"
}

# Function to setup Grafana
setup_grafana() {
    echo "📊 Setting up Grafana..."
    
    # Create Grafana configuration directories
    mkdir -p monitoring/grafana/provisioning/datasources
    mkdir -p monitoring/grafana/provisioning/dashboards
    
    # Create datasource configuration
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF
    
    # Create dashboard configuration
    cat > monitoring/grafana/provisioning/dashboards/portfolio.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'Portfolio System'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/dashboards
EOF
    
    # Create sample dashboard
    mkdir -p monitoring/grafana/dashboards
    cat > monitoring/grafana/dashboards/portfolio-overview.json << 'EOF'
{
  "dashboard": {
    "title": "Portfolio System Overview",
    "panels": [
      {
        "title": "HTTP Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      }
    ]
  }
}
EOF
    
    echo "✅ Grafana setup completed"
}

# Function to setup Alertmanager
setup_alertmanager() {
    echo "🚨 Setting up Alertmanager..."
    
    mkdir -p monitoring/alertmanager
    
    # Create Alertmanager configuration based on notification channel
    case $NOTIFICATION_CHANNEL in
        slack)
            cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:
  slack_api_url: '${SLACK_WEBHOOK_URL}'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'slack-notifications'

receivers:
- name: 'slack-notifications'
  slack_configs:
  - channel: '#alerts'
    title: '{{ .GroupLabels.alertname }}'
    text: '{{ .CommonAnnotations.summary }}\n{{ .CommonAnnotations.description }}'
    send_resolved: true
EOF
            echo "⚠️  Please set SLACK_WEBHOOK_URL environment variable"
            ;;
        email)
            cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@portfolio-system.com'
  smtp_auth_username: '${EMAIL_USERNAME}'
  smtp_auth_password: '${EMAIL_PASSWORD}'

route:
  receiver: 'email-notifications'

receivers:
- name: 'email-notifications'
  email_configs:
  - to: 'admin@portfolio-system.com'
    send_resolved: true
EOF
            echo "⚠️  Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables"
            ;;
        telegram)
            cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:

route:
  receiver: 'telegram-notifications'

receivers:
- name: 'telegram-notifications'
  telegram_configs:
  - bot_token: '${TELEGRAM_BOT_TOKEN}'
    chat_id: '${TELEGRAM_CHAT_ID}'
    send_resolved: true
EOF
            echo "⚠️  Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables"
            ;;
        webhook)
            cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:

route:
  receiver: 'webhook-notifications'

receivers:
- name: 'webhook-notifications'
  webhook_configs:
  - url: '${WEBHOOK_URL}'
    send_resolved: true
EOF
            echo "⚠️  Please set WEBHOOK_URL environment variable"
            ;;
        *)
            echo "⚠️  Unknown notification channel: $NOTIFICATION_CHANNEL"
            echo "    Using default configuration"
            cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:

route:
  receiver: 'null'

receivers:
- name: 'null'
EOF
            ;;
    esac
    
    echo "✅ Alertmanager setup completed"
}

# Function to setup Loki (logs)
setup_loki() {
    echo "📝 Setting up Loki for logs..."
    
    mkdir -p monitoring/loki
    
    # Create Loki configuration
    cat > monitoring/loki/loki-config.yaml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: false
  retention_period: 0s
EOF
    
    echo "✅ Loki setup completed"
}

# Function to start monitoring stack
start_monitoring() {
    echo "🚀 Starting monitoring stack..."
    
    # Check if docker-compose.monitoring.yml exists
    if [ -f "docker-compose.monitoring.yml" ]; then
        echo "Starting monitoring services..."
        docker-compose -f docker-compose.monitoring.yml up -d
    else
        echo "⚠️  docker-compose.monitoring.yml not found"
        echo "Creating basic monitoring stack..."
        
        cat > docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/etc/grafana/dashboards
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
EOF
        
        docker-compose -f docker-compose.monitoring.yml up -d
    fi
    
    echo "✅ Monitoring stack started"
    echo ""
    echo "📊 Monitoring URLs:"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Alertmanager: http://localhost:9093"
    echo "  - Node Exporter: http://localhost:9100"
    echo "  - cAdvisor: http://localhost:8080"
}

# Function to verify monitoring setup
verify_monitoring() {
    echo "🔍 Verifying monitoring setup..."
    
    # Wait for services to start
    sleep 10
    
    # Check Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        echo "✅ Prometheus is healthy"
    else
        echo "❌ Prometheus is not responding"
    fi
    
    # Check Grafana
    if curl -s http://localhost:3000/api/health > /dev/null; then
        echo "✅ Grafana is healthy"
    else
        echo "❌ Grafana is not responding"
    fi
    
    # Check Alertmanager
    if curl -s http://localhost:9093/-/healthy > /dev/null; then
        echo "✅ Alertmanager is healthy"
    else
        echo "❌ Alertmanager is not responding"
    fi
    
    echo "✅ Monitoring verification completed"
}

# Main setup function
main() {
    echo "Starting monitoring setup..."
    echo ""
    
    # Check Docker
    check_docker
    echo ""
    
    # Setup based on type
    case $SETUP_TYPE in
        all)
            setup_prometheus
            echo ""
            setup_grafana
            echo ""
            setup_alertmanager
            echo ""
            setup_loki
            echo ""
            start_monitoring
            ;;
        prometheus)
            setup_prometheus
            ;;
        grafana)
            setup_grafana
            ;;
        alertmanager)
            setup_alertmanager
            ;;
        loki)
            setup_loki
            ;;
        *)
            echo "❌ Unknown setup type: $SETUP_TYPE"
            exit 1
            ;;
    esac
    
    # Verify setup
    if [[ "$SETUP_TYPE" == "all" ]]; then
        echo ""
        verify_monitoring
    fi
    
    echo ""
    echo "================================================================"
    echo "🎉 Monitoring setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Configure notification channels in Alertmanager"
    echo "  2. Import dashboards in Grafana"
    echo "  3. Set up additional metrics in your applications"
    echo "  4. Test alerts by triggering conditions"
    echo ""
    echo "📚 Documentation:"
    echo "  - Monitoring guide: docs/monitoring/README.md"
    echo "  - Alert runbook: docs/monitoring/RUNBOOK.md"
    echo "================================================================"
}

# Run main function
main