# Анализ маршрутизации через Traefik

**Дата:** 15 мая 2026 г.
**Статус:** Временное решение (прямые порты)
**Приоритет:** Средний

---

## Резюме

Два сервиса (`decision-engine` и `ml-model-registry`) успешно работают и доступны напрямую через проброшенные порты (8001, 8002). Однако маршрутизация через Traefik (порт 80) не работает из-за проблем с Docker socket в Windows.

---

## Достигнутые результаты ✅

| Компонент | Статус | Детали |
|-----------|--------|--------|
| **decision-engine** | ✅ Healthy | Порт 8001, `/health` → `{"status":"healthy"}` |
| **ml-model-registry** | ✅ Healthy | Порт 8002, `/health` → `{"service":"ml-model-registry"}` |
| **Прямой доступ** | ✅ Работает | `http://localhost:8001`, `http://localhost:8002` |
| **Traefik routing** | ❌ Не работает | 404 на `/decision-engine`, `/ml-registry` |

---

## Проблема с Traefik

### Ошибка

```
ERR Failed to retrieve information of the docker client and server host
error="Error response from daemon: " providerName=docker
```

Traefik не может подключиться к Docker daemon внутри контейнера.

### Причины

1. **Docker Socket mount в Windows** — нестабильная работа `/var/run/docker.sock` в Docker Desktop для Windows (WSL2)
2. **Сетевой isolation** — возможные проблемы с сетевым namespace
3. **Версия Traefik v3.0** — потенциальная несовместимость с Docker Desktop

### Верификация

```bash
# Контейнеры в сети ✅
docker network inspect portfolio-system-architect_portfolio-network
# → decision-engine, ml-model-registry, postgres, redis, traefik

# Доступ из Traefik ✅
docker exec portfolio-gateway wget -qO- http://decision-engine:8001/health
# → {"status":"healthy"}

# Маршрутизация ❌
curl http://localhost/decision-engine/health
# → 404 page not found
```

---

## Текущее решение: Прямые порты

### Конфигурация

```yaml
# docker-compose.yml
decision-engine:
  ports:
    - "8001:8001"  # Direct access

ml-model-registry:
  ports:
    - "8002:8002"  # Direct access
```

### Преимущества

- ✅ **Надёжность** — работает стабильно
- ✅ **Простота** — минимум конфигурации
- ✅ **Отладка** — легко тестировать (`curl http://localhost:8001/health`)
- ✅ **Производительность** — без дополнительного hop через Traefik

### Недостатки

- ❌ **Много портов** — 8001, 8002, 8100, 8501, 6379, 8080...
- ❌ **Нет единой точки входа** — усложняет firewall rules
- ❌ **Не production-ready** — в production нужен API Gateway
- ❌ **Конфликты портов** — риск занятости портов на хосте

---

## Варианты решения

### Вариант 1: Исправить Traefik (приоритет: средний)

**Подход:** Отладить Docker socket mount в Windows

**Шаги:**
```bash
# 1. Проверить mount сокет
docker exec portfolio-gateway ls -la /var/run/docker.sock

# 2. Проверить Docker Desktop настройки
# Settings → Resources → WSL Integration → включить вашу дистрибуцию

# 3. Перезапустить Docker Desktop
# Иногда помогает пересоздание сети
docker network rm portfolio-system-architect_portfolio-network
docker-compose up -d
```

**Риски:** Может потребовать переустановки Docker Desktop

---

### Вариант 2: nginx вместо Traefik (приоритет: низкий)

**Подход:** Использовать nginx с явной конфигурацией (не требует Docker socket)

**Конфигурация:**
```nginx
# nginx.conf
upstream decision_engine {
    server decision-engine:8001;
}

upstream ml_registry {
    server ml-model-registry:8002;
}

server {
    listen 80;

    location /decision-engine {
        proxy_pass http://decision_engine;
    }

    location /ml-registry {
        proxy_pass http://ml_registry;
    }
}
```

**Плюсы:**
- ✅ Стабильная работа в Windows
- ✅ Простая конфигурация
- ✅ Production-ready

**Минусы:**
- ❌ Ручное управление маршрутами (нет auto-discovery)
- ❌ Нужно перезагружать nginx при изменении конфигурации

---

### Вариант 3: Оставить как есть (прямые порты) (приоритет: низкий)

**Подход:** Использовать прямые порты для разработки, добавить Traefik/nginx только для production

**Докumentация:**
```markdown
## Доступ к сервисам

### Разработка (локально)
- Decision Engine: http://localhost:8001
- ML Registry: http://localhost:8002
- Auth Service: http://localhost:8100
- IT Compass: http://localhost:8501

### Production
Через API Gateway (Traefik/nginx):
- /decision-engine → localhost:8001
- /ml-registry → localhost:8002
```

**Плюсы:**
- ✅ Минимальные затраты
- ✅ Работает сейчас

**Минусы:**
- ❌ Не масштабируется
- ❌ Требует ручного управления портами

---

## Рекомендация

**Для текущей стадии (разработка):** Оставить прямые порты ✅

**Причины:**
1. Оба сервиса работают стабильно
2. Прямой доступ упрощает отладку
3. Traefik не критичен для разработки
4. Можно добавить API Gateway позже

**Критерии перехода на Traefik/nginx:**
- [ ] Подготовка к production-деплою
- [ ] Появление 5+ сервисов (управление портами становится сложным)
- [ ] Требования к безопасности (единая точка входа, TLS, rate limiting)
- [ ] Необходимость load balancing

---

## Метрики

| Метрика | Значение |
|---------|----------|
| **Сервисов работает** | 2/2 (100%) |
| **Health checks** | 2/2 (healthy) |
| **Прямой доступ** | ✅ 8001, 8002 |
| **Traefik routing** | ❌ 404 |
| **Время на решение** | ~2 часа |
| **Влияние на разработку** | Минимальное |

---

## Следующие шаги

1. ✅ Закоммитить текущие изменения (прямые порты)
2. 📋 Документировать решение в `docs/TRAEFIK_ANALYSIS.md`
3. 🔧 При необходимости — исправить Traefik (см. Вариант 1)
4. 📦 Добавить nginx как альтернативу (см. Вариант 2)
5. 🚀 В production — обязательно использовать API Gateway

---

## История изменений

| Дата | Изменение | Автор |
|------|-----------|-------|
| 2026-05-15 | Конфликт портов (8001 → 8002) | Koda |
| 2026-05-15 | Исправлен Dockerfile (httpx) | Koda |
| 2026-05-15 | Добавлены прямые порты | Koda |
| 2026-05-15 | Создан анализ Traefik | Koda |
