# Runbook: Восстановление упавшего сервиса

> **Уровень критичности:** HIGH
> **Время восстановления (целевое):** <5 минут
> **Автор:** Ekaterina Kudelya
> **Обновлено:** 18 мая 2026

---

## 🚨 Сценарий

Сервис перестал отвечать на запросы или вернул ошибку 5xx.

---

## 🔍 Диагностика

### Шаг 1: Проверить статус сервиса

```bash
# Через navigate.ps1
.\navigate.ps1 -Status

# Или через Docker
docker-compose ps

# Или через Kubernetes
kubectl get pods -n production
```

**Ожидаемый результат:** Сервис в статусе `running` / `Healthy`
**Фактический результат:** `exited` / `Restarting` / `Unhealthy`

---

### Шаг 2: Просмотреть логи

```bash
# Docker
docker-compose logs <service-name> --tail=100

# Kubernetes
kubectl logs <pod-name> -n production --tail=100

# Или через navigate.ps1
cd apps/<service-name>
docker-compose logs --tail=100
```

**Искать:**
- Stack traces
- Connection errors
- Out of memory
- Database connection failures

---

### Шаг 3: Проверить зависимости

```bash
# PostgreSQL
curl http://localhost:5432

# Redis
redis-cli ping

# Другие сервисы
curl http://localhost:<port>/health
```

---

## 🛠️ Восстановление

### Вариант A: Перезапуск сервиса

```bash
# Docker
docker-compose restart <service-name>

# Kubernetes
kubectl rollout restart deployment/<service-name> -n production

# Проверка
docker-compose ps
```

**Если не помогло → Вариант B**

---

### Вариант B: Полный перезапуск с очисткой кэша

```bash
# Остановить сервис
docker-compose stop <service-name>

# Удалить контейнер
docker rm <service-name>

# Очистить кэш (опционально)
docker system prune -f

# Запустить заново
docker-compose up -d <service-name>

# Проверить логи
docker-compose logs -f <service-name>
```

---

### Вариант C: Откат версии (если проблема после деплоя)

```bash
# Проверить историю образов
docker image ls | grep <service-name>

# Откатиться на предыдущую версию
docker-compose up -d --no-recreate <service-name>

# Или через Kubernetes
kubectl rollout undo deployment/<service-name> -n production
```

---

## ✅ Проверка восстановления

```bash
# Health check
curl http://localhost:<port>/health

# Основной endpoint
curl http://localhost:<port>/api/v1/

# Через navigate.ps1
.\navigate.ps1 -Service <service-name>
```

**Ожидаемый результат:** `{"status": "healthy"}`

---

## 📊 Если не восстановилось

### Эскалация

1. **Уровень 1** (5 мин): Перезапуск + проверка логов
2. **Уровень 2** (15 мин): Проверка зависимостей + откат версии
3. **Уровень 3** (30 мин): Полный аудит + создание issue

### Контакты

| Роль | Контакт | Время реакции |
|------|---------|---------------|
| On-call | leadarchitect@yandex.ru | <5 мин |
| Tech Lead | Telegram: @yourhandle | <15 мин |
| CTO | Email | <1 час |

---

## 📝 Пост-мортем

После восстановления создать issue с:

1. **Время инцидента:** Когда обнаружено / когда восстановлено
2. **Причина:** Что вызвало падение
3. **Действия:** Что сделали для восстановления
4. **Предотвращение:** Как избежать в будущем

**Шаблон:**
```markdown
## Инцидент: <service-name> упал

**Время:** 2026-05-18 14:30 UTC
**Длительность:** 12 минут
**Причина:** Database connection timeout

**Действия:**
- Перезапуск сервиса (не помогло)
- Проверка PostgreSQL (был перегруз)
- Откат версии (успешно)

**Предотвращение:**
- Добавить health checks для БД
- Увеличить pool connections
- Настроить алерты
```

---

## 🔗 Ссылки

- [Docker Compose Docs](https://docs.docker.com/compose/reference/)
- [Kubernetes Rollout](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Monitoring Dashboard](http://localhost:3000)
- [Service README](../apps/<service-name>/README.md)

---

*Last updated: 18 мая 2026*
