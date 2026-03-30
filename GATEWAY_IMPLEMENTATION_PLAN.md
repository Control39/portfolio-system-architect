# План реализации Unified API Gateway

## 🎯 Цель
Создать единую точку входа для всей экосистемы сервисов с аутентификацией, rate limiting, мониторингом и routing.

## 📋 Текущие проблемы
1. Каждый сервис имеет свой endpoint и порт
2. Нет единой аутентификации
3. Нет централизованного мониторинга
4. Сложность масштабирования
5. Отсутствие кэширования

## 🏗️ Архитектура Gateway

### Компоненты:
```
gateway/
├── main.py                    # FastAPI приложение
├── config/
│   ├── services.yaml         # Конфигурация upstream сервисов
│   └── routes.yaml          # Маршрутизация
├── middleware/
│   ├── auth.py              # JWT аутентификация
│   ├── rate_limit.py        # Rate limiting
│   ├── cache.py             # Redis кэширование
│   └── logging.py           # Структурированное логирование
├── clients/
│   ├── architect_client.py  # Клиент для Architect Assistant
│   ├── portfolio_client.py  # Клиент для Portfolio Organizer
│   └── ml_client.py         # Клиент для ML Registry
└── models/
    └── schemas.py           # Pydantic схемы
```

## 🚀 Фаза 1: Базовая реализация (2 недели)

### Неделя 1: Настройка инфраструктуры
1. **Создать структуру проекта**
```bash
mkdir -p gateway/{config,middleware,clients,models}
```

2. **Установить зависимости**
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
pyjwt==2.8.0
httpx==0.25.1
python-multipart==0.0.6
python-dotenv==1.0.0
```

3. **Настроить Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Неделя 2: Реализация core функциональности
1. **Базовый FastAPI app**
2. **Маршрутизация к существующим сервисам**
3. **Простая аутентификация**
4. **Базовое логирование**

## 🛠️ Фаза 2: Продвинутые функции (2 недели)

### Неделя 3: Middleware
1. **JWT аутентификация с ролями**
2. **Rate limiting per user/service**
3. **Request/Response трансформация**
4. **Кэширование частых запросов**

### Неделя 4: Мониторинг и DevOps
1. **Health checks всех сервисов**
2. **Prometheus метрики**
3. **Structured logging (JSON)**
4. **Kubernetes deployment**

## 📊 Конфигурация сервисов

### services.yaml
```yaml
services:
  architect:
    base_url: "http://architect-assistant:8000"
    health_check: "/health"
    timeout: 30
    retries: 3
    
  portfolio:
    base_url: "http://portfolio-organizer:3000"
    health_check: "/api/health"
    timeout: 20
    retries: 2
    
  ml_registry:
    base_url: "http://ml-model-registry:5000"
    health_check: "/health"
    timeout: 15
    retries: 2
    
  it_compass:
    base_url: "http://it-compass:4000"
    health_check: "/api/health"
    timeout: 25
    retries: 3
```

### routes.yaml
```yaml
routes:
  - path: "/api/v1/architect"
    target: "architect"
    methods: ["GET", "POST"]
    auth_required: true
    rate_limit: "100/hour"
    
  - path: "/api/v1/portfolio"
    target: "portfolio"
    methods: ["GET", "POST", "PUT", "DELETE"]
    auth_required: true
    rate_limit: "500/hour"
    
  - path: "/api/v1/ml"
    target: "ml_registry"
    methods: ["GET", "POST"]
    auth_required: true
    rate_limit: "200/hour"
    
  - path: "/api/v1/skills"
    target: "it_compass"
    methods: ["GET", "POST"]
    auth_required: true
    rate_limit: "300/hour"
```

## 🔐 Аутентификация и авторизация

### Flow:
1. Пользователь логинится через `/auth/login`
2. Gateway генерирует JWT токен
3. Токен передается в заголовках
4. Gateway валидирует токен для каждого запроса
5. Роли определяют доступ к endpoints

### Роли:
- **viewer**: только чтение
- **editor**: чтение + запись
- **admin**: полный доступ + управление пользователями
- **service**: доступ для других сервисов

## 📈 Мониторинг и метрики

### Prometheus метрики:
- `gateway_requests_total` - общее количество запросов
- `gateway_request_duration_seconds` - время обработки
- `gateway_errors_total` - количество ошибок
- `gateway_active_connections` - активные соединения
- `service_health_status` - статус health check сервисов

### Health check dashboard:
```
GET /health
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "architect": "healthy",
    "portfolio": "healthy",
    "ml_registry": "degraded",
    "it_compass": "unhealthy"
  },
  "metrics": {
    "uptime": "7d 12h 30m",
    "request_rate": "150 req/min",
    "error_rate": "0.5%"
  }
}
```

## 🐳 Docker Compose для разработки

### docker-compose.gateway.yml
```yaml
version: '3.8'

services:
  gateway:
    build: ./gateway
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - redis
      - architect-assistant
      - portfolio-organizer
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      
  architect-assistant:
    build: ./api
    ports:
      - "8000:8000"
      
  portfolio-organizer:
    build: ./apps/portfolio-organizer
    ports:
      - "3000:3000"

volumes:
  redis_data:
```

## 🚀 Kubernetes Deployment

### gateway-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      containers:
      - name: gateway
        image: your-registry/gateway:latest
        ports:
        - containerPort: 8080
        env:
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: gateway-secrets
              key: jwt-secret
        - name: REDIS_URL
          value: "redis://redis:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 🔄 Миграция существующих клиентов

### Шаг 1: Обновить base URLs
```python
# Было:
ARCHITECT_URL = "http://localhost:8000"

# Стало:
ARCHITECT_URL = "http://localhost:8080/api/v1/architect"
```

### Шаг 2: Добавить аутентификацию
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

### Шаг 3: Обновить error handling
```python
# Gateway возвращает стандартизированные ошибки
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "details": {
      "limit": "100/hour",
      "remaining": 0,
      "reset_in": 60
    }
  }
}
```

## 🧪 Тестирование

### Unit tests:
```python
def test_auth_middleware():
    # Test JWT validation
    # Test role-based access
    # Test token expiration

def test_rate_limiting():
    # Test rate limit per user
    # Test rate limit per endpoint
    # Test reset functionality

def test_routing():
    # Test request forwarding
    # Test path rewriting
    # Test error handling
```

### Integration tests:
```python
def test_full_flow():
    # 1. Login and get token
    # 2. Make request to architect endpoint
    # 3. Verify response is forwarded correctly
    # 4. Check metrics are recorded
```

### Load testing:
```bash
# Использовать k6 или locust
k6 run --vus 100 --duration 30s gateway-load-test.js
```

## 📊 Метрики успеха

### Технические:
- **Availability**: 99.9% uptime
- **Latency**: < 100ms p95 для gateway
- **Throughput**: 1000+ RPS
- **Error rate**: < 0.1%

### Бизнес:
- **Упрощение клиентского кода**: -50% boilerplate
- **Сокращение инцидентов**: -30% благодаря централизованному мониторингу
- **Ускорение разработки**: +40% скорость добавления новых endpoints
- **Улучшение security**: Единая точка для security patches

## 🚨 Риски и mitigation

### Риск 1: Single point of failure
**Mitigation**: 
- Multiple replicas в Kubernetes
- Circuit breaker pattern
- Fallback к direct service access при необходимости

### Риск 2: Performance bottleneck
**Mitigation**:
- Кэширование frequent requests
- Connection pooling
- Async обработка запросов
- Horizontal scaling

### Риск 3: Сложность отладки
**Mitigation**:
- Request ID propagation
- Distributed tracing (Jaeger)
- Detailed structured logging
- Developer mode с дополнительной информацией

## 📅 Roadmap

### Месяц 1: MVP
- Базовая маршрутизация
- Простая аутентификация
- Health checks
- Документация API

### Месяц 2: Production ready
- Rate limiting
- Кэширование
- Мониторинг и метрики
- Security hardening

### Месяц 3: Оптимизация
- Performance tuning
- Advanced caching strategies
- Predictive scaling
- Advanced analytics

## 🎯 Заключение

Unified API Gateway - это критически важный компонент для масштабирования экосистемы. Он обеспечит:

1. **Единую точку управления** для всех API
2. **Улучшенную security** через централизованную аутентификацию
3. **Лучшую observability** через централизованный мониторинг
4. **Упрощение клиентского кода** через стандартизированные интерфейсы

Реализация займет 1-2 месяца и окупится за счет снижения operational overhead и ускорения разработки новых features.