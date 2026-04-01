# План внедрения Service Discovery

## Текущее состояние

В проекте используется архитектура микросервисов с API Gateway (Traefik) для маршрутизации запросов. Сервисы общаются через Docker сеть, но отсутствует централизованный механизм Service Discovery.

### Проблемы текущего подхода:
1. **Хардкод адресов**: Сервисы знают адреса друг друга через имена контейнеров Docker
2. **Отсутствие динамического обнаружения**: Новые инстансы сервисов не регистрируются автоматически
3. **Нет health checking на уровне Service Discovery**: Traefik выполняет health checks, но нет централизованного мониторинга состояния сервисов
4. **Сложность масштабирования**: Ручное управление конфигурацией при добавлении реплик

## Цели внедрения

1. **Динамическое обнаружение сервисов**: Автоматическая регистрация и deregistration сервисов
2. **Health checking**: Централизованный мониторинг состояния сервисов
3. **Балансировка нагрузки**: Интеграция с механизмами балансировки
4. **Конфигурация как код**: Управление конфигурацией через декларативные файлы
5. **Безопасность**: Взаимная аутентификация и шифрование трафика

## Варианты реализации

### Вариант 1: Consul (рекомендуется)
**Преимущества:**
- Полнофункциональный Service Discovery и конфигурация
- Встроенный health checking
- Поддержка multi-datacenter
- Интеграция с Traefik через Consul Catalog
- Активное сообщество и документация

**Недостатки:**
- Дополнительная сложность инфраструктуры
- Требует отдельного кластера Consul

### Вариант 2: Kubernetes Service Discovery (для будущего)
**Преимущества:**
- Нативная интеграция при развертывании в Kubernetes
- Встроенные механизмы Service Discovery через DNS
- Интеграция с Ingress контроллерами

**Недостатки:**
- Требует миграции на Kubernetes
- Не решает проблему для Docker Compose окружения

### Вариант 3: Traefik с Docker Provider (текущий)
**Преимущества:**
- Уже работает в проекте
- Простая конфигурация
- Автоматическое обнаружение через Docker labels

**Недостатки:**
- Ограниченная функциональность Service Discovery
- Нет централизованного каталога сервисов
- Зависит от Docker окружения

## План внедрения Consul (Фаза 2)

### Этап 1: Подготовка (1-2 недели)
1. **Добавление Consul в docker-compose**:
   ```yaml
   consul-server:
     image: consul:1.17
     container_name: consul-server
     command: agent -server -bootstrap-expect=1 -ui -client=0.0.0.0
     ports:
       - "8500:8500"  # Web UI
       - "8600:8600/tcp"  # DNS
       - "8600:8600/udp"
     volumes:
       - consul-data:/consul/data
     networks:
       - portfolio-network
   ```

2. **Настройка Consul Client для каждого сервиса**:
   - Sidecar контейнер Consul Agent
   - Health check endpoints
   - Service registration

### Этап 2: Интеграция (2-3 недели)
1. **Обновление docker-compose конфигураций**:
   - Добавление Consul labels
   - Настройка health checks для Consul
   - Конфигурация service registration

2. **Интеграция с Traefik**:
   - Настройка Traefik Consul Catalog provider
   - Динамическая маршрутизация через Consul

3. **Обновление сервисов**:
   - Добавление Consul client библиотек
   - Реализация service discovery через Consul DNS или HTTP API
   - Graceful shutdown с deregistration

### Этап 3: Тестирование и миграция (1-2 недели)
1. **Поэтапная миграция сервисов**:
   - Начать с одного сервиса (например, auth-service)
   - Тестирование в изолированной среде
   - Постепенная миграция остальных сервисов

2. **Сохранение обратной совместимости**:
   - Параллельная работа старого и нового подходов
   - Feature flags для переключения между режимами
   - Fallback на старый подход при сбоях

## Конфигурационные файлы

### docker-compose.consul.yml (дополнительный файл)
```yaml
version: '3.9'

services:
  consul-server:
    image: consul:1.17
    container_name: consul-server
    command: agent -server -bootstrap-expect=1 -ui -client=0.0.0.0
    ports:
      - "8500:8500"
      - "8600:8600/tcp"
      - "8600:8600/udp"
    volumes:
      - consul-data:/consul/data
    networks:
      - portfolio-network
    environment:
      - CONSUL_BIND_INTERFACE=eth0
      - CONSUL_LOCAL_CONFIG={"datacenter": "portfolio-dc", "server": true}

  consul-agent-sidecar:
    image: consul:1.17
    container_name: consul-agent-sidecar
    command: agent -retry-join=consul-server -client=0.0.0.0
    depends_on:
      - consul-server
    networks:
      - portfolio-network
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

volumes:
  consul-data:

networks:
  portfolio-network:
    external: true
    name: portfolio-system-architect_portfolio-network
```

### Обновление сервиса для Consul
```yaml
auth-service:
  # ... существующая конфигурация ...
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.auth.rule=Host(`localhost`) && PathPrefix(`/auth`)"
    - "traefik.http.services.auth-service.loadbalancer.server.port=8100"
    # Consul labels
    - "consul.register=true"
    - "consul.name=auth-service"
    - "consul.port=8100"
    - "consul.tags=traefik,http"
    - "consul.check.http=http://localhost:8100/health"
    - "consul.check.interval=30s"
    - "consul.check.timeout=5s"
```

## Мониторинг и эксплуатация

1. **Consul Web UI**: http://localhost:8500
2. **Метрики Consul**: Интеграция с Prometheus
3. **Алертинг**: Настройка алертов на unhealthy сервисы
4. **Бэкап**: Регулярное резервное копирование Consul данных

## Риски и митигация

### Риск 1: Сложность внедрения
- **Митигация**: Поэтапное внедрение, начиная с dev окружения
- **Fallback**: Сохранение старого подхода как backup

### Риск 2: Производительность
- **Митигация**: Мониторинг нагрузки Consul, горизонтальное масштабирование
- **Оптимизация**: Настройка Consul для оптимальной производительности

### Риск 3: Безопасность
- **Митигация**: Настройка ACL, mTLS, изоляция сети
- **Аудит**: Регулярные security audits

## Следующие шаги

1. **Создать ADR для Service Discovery**
2. **Добавить Consul в dev окружение** (docker-compose.consul.yml)
3. **Протестировать с одним сервисом** (auth-service)
4. **Интегрировать с Traefik**
5. **Постепенно мигрировать остальные сервисы**
6. **Документировать процесс для production**

## Ресурсы

- [Consul Documentation](https://www.consul.io/docs)
- [Traefik Consul Catalog Provider](https://doc.traefik.io/traefik/providers/consul-catalog/)
- [Docker Compose with Consul](https://github.com/hashicorp/consul/tree/main/demo/docker-compose)
