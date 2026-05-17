# Runbook: Восстановление базы данных

> **Уровень критичности:** CRITICAL
> **Время восстановления (целевое):** <10 минут
> **Автор:** Ekaterina Kudelya
> **Обновлено:** 18 мая 2026

---

## 🚨 Сценарий

PostgreSQL не отвечает, данные повреждены или потеряны.

---

## 🔍 Диагностика

### Шаг 1: Проверить статус PostgreSQL

```bash
docker-compose ps postgresql
# или
kubectl get pods -l app=postgresql -n production
```

### Шаг 2: Проверить логи

```bash
docker-compose logs postgresql --tail=100
```

**Искать:**
- Out of memory
- Disk full
- Corruption errors
- Connection refused

---

## 🛠️ Восстановление

### Вариант A: Перезапуск PostgreSQL

```bash
docker-compose restart postgresql
docker-compose logs -f postgresql
```

---

### Вариант B: Восстановление из бэкапа

```bash
# Остановить сервисы
docker-compose stop

# Восстановить из бэкапа
docker exec -i postgresql psql -U postgres < /backups/latest.sql

# Или через volume
docker run --rm \
  -v postgres_data:/data \
  -v /backups:/backups \
  postgres:16 \
  pg_restore -U postgres -d postgres /backups/latest.dump

# Запустить сервисы
docker-compose up -d
```

---

### Вариант C: Инициализация новой БД (последний ресурс)

```bash
# Остановить всё
docker-compose down -v  # ВНИМАНИЕ: удалит все данные!

# Пересоздать volumes
docker volume create postgres_data

# Запустить заново
docker-compose up -d postgresql

# Подождать инициализации
sleep 30

# Проверить
docker-compose logs postgresql
```

---

## ✅ Проверка

```bash
docker exec -i postgresql psql -U postgres -c "SELECT version();"
docker exec -i postgresql psql -U postgres -c "SELECT count(*) FROM services;"
```

---

*Last updated: 18 мая 2026*
