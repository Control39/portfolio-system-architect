# Monitoring Stack for Portfolio System Architect

This directory contains the complete monitoring stack for the portfolio system, demonstrating production-grade observability practices.

## 🎯 Purpose

The monitoring stack is included to demonstrate:

1. **Production readiness** – real systems need monitoring, not just code
2. **Observability expertise** – understanding of metrics, logging, tracing
3. **SRE principles** – SLIs, SLOs, alerting, incident response
4. **Enterprise relevance** – financial sector and large companies require comprehensive monitoring

## 🏗️ Architecture

```
Portfolio Services (8 deployable microservices)
        ↓
    Prometheus (metrics collection)
        ↓
    Grafana (visualization & dashboards)
        ↓
  Alertmanager (alert routing)
        ↓
   Notifications (Telegram, Email, etc.)
```

## 📊 Components

### 1. Prometheus
- **Configuration**: `prometheus/prometheus.yml` (main), `prometheus/prometheus-full.yml` (extended)
- **What it collects**:
  - Application metrics (HTTP requests, latency, errors)
  - System metrics (CPU, memory, disk)
  - Business metrics (user activity, feature usage)
  - Custom metrics from portfolio services
- **Scrape intervals**: 15s default
- **Retention**: 15 days

### 2. Grafana
- **Dashboards**: `grafana/dashboards/portfolio.json`
- **Data sources**: Prometheus (auto-configured)
- **Provisioning**: Automatic via `grafana/provisioning/`
- **Features**:
  - Real-time monitoring
  - Historical analysis
  - Alert visualization
  - Team collaboration

### 3. Alertmanager
- **Configuration**: `alertmanager/alertmanager.yml`
- **Alert routing**:
  - Critical alerts → Telegram immediate notification
  - Warning alerts → Telegram delayed notification
  - Info alerts → Log only
- **Features**:
  - Grouping and deduplication
  - Silence management
  - Template-based notifications

## 🚀 Getting Started

### Local Development
```bash
# Start monitoring stack
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d prometheus grafana alertmanager

# Access services
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# Alertmanager: http://localhost:9093
```

### Production Deployment
- Use `prometheus/prometheus-full.yml` for production
- Configure persistent volumes for data
- Set up TLS and authentication
- Configure external alert receivers (Telegram bot token, email, etc.)

## 📈 Key Metrics & Dashboards

### Portfolio Dashboard (`portfolio.json`)
- **CPU Usage** – per service, with trends
- **HTTP Latency** – p95, p99 percentiles
- **Request Rate** – requests per second
- **Error Rate** – 4xx/5xx errors
- **Business Metrics** – user activity, feature usage

### SLO/SLI Examples
While formal SLOs aren't defined (this is a portfolio), the monitoring supports:
- **Availability**: HTTP success rate > 99.9%
- **Latency**: p95 < 200ms
- **Throughput**: RPS capacity planning
- **Errors**: Error budget tracking

## 🔔 Alerting Rules

### Critical Alerts (immediate response)
- Service down for > 5 minutes
- Error rate > 5% for 10 minutes
- Latency p95 > 1s for 15 minutes
- CPU > 90% for 10 minutes

### Warning Alerts (investigate)
- Error rate > 2% for 30 minutes
- Latency p95 > 500ms for 30 minutes
- Memory > 80% for 1 hour
- Disk > 85% utilization

### Info Alerts (monitoring)
- Deployment events
- Configuration changes
- Certificate expirations (30-day warning)

## 🛠️ Configuration Details

### Prometheus Configuration
- **Target discovery**: Static configuration (can be extended with service discovery)
- **Relabeling**: Adds environment and service labels
- **Recording rules**: Pre-computed metrics for efficiency
- **Alerting rules**: Defined in `prometheus/rules.yml`

### Grafana Provisioning
- **Automatic dashboard loading**: `grafana/provisioning/dashboards/`
- **Data source configuration**: `grafana/provisioning/datasources/`
- **No manual setup required**

### Alertmanager Configuration
- **Receivers**: Telegram (critical/warning), Email (optional)
- **Routes**: Based on severity labels
- **Templates**: Custom message formatting
- **Inhibitions**: Prevent alert storms

## 🤔 Why Include Monitoring in a Portfolio?

### Demonstrates:
1. **Production mindset** – thinking beyond development to operations
2. **Observability skills** – metrics, logging, tracing understanding
3. **SRE competency** – error budgets, SLIs, alerting strategies
4. **Enterprise thinking** – large companies require robust monitoring

### Addresses "overengineering" criticism:
- **Not "dead weight"** – fully functional monitoring stack
- **Not "complexity for complexity"** – each component has purpose
- **Documented and justified** – see ADR-007 and README architectural justification

## 📸 Screenshots & Visual Evidence

To demonstrate the monitoring stack in action, here are example screenshots of Grafana dashboards and alert notifications:

### Grafana Dashboard - AI Service Monitoring
![Grafana Dashboard - AI Service](./docs/screenshots/monitoring/grafana-ai-service.png)

*This dashboard shows real-time metrics for the AI service:*
- **CPU/Memory usage** across replicas
- **HTTP request rate** and latency percentiles
- **Error rate** with 5-minute rolling average
- **Custom business metrics** (RAG processing time, vector search latency)

### Grafana Dashboard - Portfolio Overview
![Grafana Dashboard - Portfolio Overview](./docs/screenshots/monitoring/grafana-portfolio-overview.png)

*High-level overview of the entire portfolio system:*
- **Service health** (8 deployable microservices)
- **Infrastructure metrics** (Kubernetes cluster resources)
- **Business KPIs** (user activity, feature adoption)
- **SLO compliance** (availability, latency, error budget)

### Alert Notification Example
![Telegram Alert Notification](./docs/screenshots/monitoring/telegram-alert-example.png)

*Example of an alert delivered via Telegram:*
- **Clear severity indication** (WARNING/CRITICAL)
- **Actionable information** (which service, metric, threshold)
- **Direct links** to Grafana dashboard for investigation
- **Runbook references** for standard operating procedures

> **Note**: These are placeholder screenshots. To capture actual screenshots:
> 1. Start the monitoring stack: `docker compose -f docker-compose.monitoring.yml up -d`
> 2. Access Grafana at http://localhost:3000 (admin/admin)
> 3. Navigate to the "Portfolio" dashboard
> 4. Take screenshots and save them to `docs/screenshots/monitoring/`
> 5. Update the image references above with actual filenames

## 🚨 Пример алерта

### Как работает алертинг в продакшн-системе

Алертинг настроен через Prometheus Alertmanager с маршрутизацией в Telegram. Вот конкретный пример:

#### Сценарий: Высокое использование памяти в поде AI-сервиса

**Правило алерта (Prometheus rules.yml):**
```yaml
- alert: HighMemoryUsage
  expr: container_memory_usage_bytes{container="ai-service"} / container_spec_memory_limit_bytes{container="ai-service"} > 0.95
  for: 5m
  labels:
    severity: warning
    service: ai-service
  annotations:
    summary: "Memory usage >95% for pod {{ $labels.pod }}"
    description: "AI service pod {{ $labels.pod }} is using {{ $value | humanizePercentage }} of its memory limit for more than 5 minutes."
    runbook_url: "https://github.com/leadarchitect-ai/portfolio-system-architect/blob/main/docs/runbooks/high-memory.md"
```

#### Что происходит при срабатывании:

1. **Prometheus** обнаруживает, что использование памяти превышает 95% в течение 5 минут
2. **Alertmanager** получает алерт, группирует его с другими алертами AI-сервиса
3. **Уведомление отправляется в Telegram**:

```
[WARNING] Memory usage >95% for pod ai-service-7d8f9b

📊 **Метрика**: container_memory_usage_bytes
📈 **Текущее значение**: 97.3%
⏰ **Длительность**: 5m 12s
🏷️ **Лейблы**: service=ai-service, pod=ai-service-7d8f9b, namespace=portfolio
🔗 **Дашборд**: http://grafana.local/d/portfolio/ai-service
📚 **Runbook**: https://github.com/.../high-memory.md

Рекомендуемые действия:
1. Проверить логи пода на утечки памяти
2. Увеличить memory limit в манифесте развертывания
3. Масштабировать replicas до 3 для распределения нагрузки
```

#### Автоматическое действие:

В конфигурации Kubernetes настроен Horizontal Pod Autoscaler (HPA), который автоматически увеличивает количество реплик при высокой нагрузке:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-service
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Результат**: При получении алерта система автоматически:
1. Увеличивает количество реплик AI-сервиса с 1 до 3
2. Распределяет нагрузку между новыми подами
3. Снижает использование памяти на каждом поде ниже 80%
4. Через 10 минут алерт автоматически разрешается

#### Почему это важно для портфолио:

1. **Демонстрация production-мышления** – не просто мониторинг, а автоматическое реагирование
2. **Показ SRE-практик** – error budget, автоматическое масштабирование
3. **Реальная ценность** – система сама решает проблемы, уменьшая нагрузку на инженеров
4. **Enterprise-уровень** – полный цикл: обнаружение → алерт → действие → разрешение

## 📚 Related Documentation
- [ADR-007: Technology Stack Justification](../docs/docs/adr/ADR-007-technology-stack-justification.md)
- README.md: Architectural Justification section
- [Docker Compose Configuration](../docker-compose.monitoring.yml)
- [Grafana Dashboard Screenshots](../docs/screenshots/monitoring/)

## 🔮 Future Enhancements
1. **Distributed tracing** – Jaeger or Zipkin integration
2. **Log aggregation** – Loki or ELK stack
3. **Synthetic monitoring** – blackbox exporter for external checks
4. **Business metrics** – more portfolio-specific KPIs
5. **Anomaly detection** – machine learning on metrics
