# Runbook: Откат деплоя

> **Уровень критичности:** HIGH
> **Время восстановления (целевое):** <5 минут
> **Автор:** Ekaterina Kudelya
> **Обновлено:** 18 мая 2026

---

## 🚨 Сценарий

После деплоя новая версия сервиса работает некорректно.

---

## 🔍 Диагностика

### Шаг 1: Проверить статус деплоя

```bash
# Docker
docker-compose ps

# Kubernetes
kubectl rollout status deployment/<service-name> -n production
```

### Шаг 2: Проверить логи новой версии

```bash
docker-compose logs <service-name> --tail=50
# или
kubectl logs <pod-name> -n production --tail=50
```

---

## 🛠️ Откат

### Docker Compose

```bash
# Остановить текущую версию
docker-compose stop <service-name>

# Удалить контейнер
docker rm <service-name>

# Запустить предыдущую версию
docker-compose up -d <service-name>

# Если используется тег latest - указать конкретную версию
# Изменить docker-compose.yml:
# image: service-name:1.2.3  # вместо latest
docker-compose up -d <service-name>
```

---

### Kubernetes

```bash
# Откат на предыдущую версию
kubectl rollout undo deployment/<service-name> -n production

# Откат на конкретную ревизию
kubectl rollout undo deployment/<service-name> --to-revision=3 -n production

# Проверка статуса
kubectl rollout status deployment/<service-name> -n production
```

---

## ✅ Проверка

```bash
# Health check
curl http://localhost:<port>/health

# Основной endpoint
curl http://localhost:<port>/api/v1/

# Проверка версии
curl http://localhost:<port>/api/v1/version
```

---

## 📝 Пост-мортем

Создать issue с:
1. Что было изменено в новой версии
2. Почему откатили
3. Как предотвратить в будущем

---

*Last updated: 18 мая 2026*
