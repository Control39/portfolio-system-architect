# RUNBOOK — Операционные процедуры

> **Версия:** 1.0.0
> **Дата:** 18 мая 2026 г.
> **Владелец:** Portfolio System Architect Team

---

## 📋 Содержание

1. [Восстановление сервиса при падении](#1-восстановление-сервиса-при-падении)
2. [Восстановление базы данных](#2-восстановление-базы-данных)
3. [Откат деплоя](#3-откат-деплоя)
4. [Реакция на инциденты](#4-реакция-на-инциденты)
5. [Daily Checks](#5-daily-checks)
6. [Контакты и эскалация](#6-контакты-и-эскалация)

---

## 1. Восстановление сервиса при падении

### 1.1 Диагностика

```bash
# Проверка состояния всех сервисов
docker-compose ps

# Проверка логов конкретного сервиса
docker-compose logs -f <service-name> --tail=100

# Проверка здоровья сервиса
curl http://localhost:<port>/health
```

### 1.2 Типичные проблемы и решения

#### Проблема: Сервис не запускается (ошибка зависимостей)

```bash
# 1. Проверить логи
docker-compose logs <service-name>

# 2. Пересобрать образ
docker-compose build <service-name>

# 3. Очистить кэш Docker
docker system prune -f

# 4. Перезапустить сервис
docker-compose up -d <service-name>
```

#### Проблема: Ошибка подключения к БД

```bash
# 1. Проверить состояние БД
docker-compose ps postgresql
docker-compose ps redis

# 2. Перезапустить БД
docker-compose restart postgresql redis

# 3. Проверить подключение
docker exec -it postgresql psql -U postgres -c "SELECT 1"

# 4. Перезапустить сервис
docker-compose restart <service-name>
```

#### Проблема: Высокая нагрузка (CPU/Memory)

```bash
# 1. Проверить ресурсы
docker stats <service-name>

# 2. Увеличить количество реплик (если используется Kubernetes)
kubectl scale deployment <service-name> --replicas=3

# 3. Или перезапустить сервис
docker-compose restart <service-name>
```

#### Проблема: Ошибка валидации конфигурации

```bash
# 1. Проверить конфигурацию
python check_config.py

# 2. Перезагрузить конфигурацию
curl -X POST http://localhost:8100/api/v1/config/reload

# 3. Проверить логи AI Config Manager
docker-compose logs ai-config-manager
```

### 1.3 Полный цикл восстановления

```bash
# 1. Остановить сервис
docker-compose stop <service-name>

# 2. Очистить контейнер
docker rm <service-name>

# 3. Пересобрать образ
docker-compose build <service-name>

# 4. Запустить с проверкой логов
docker-compose up -d <service-name>
docker-compose logs -f <service-name>

# 5. Проверить здоровье (повторить 5 раз)
for i in {1..5}; do
  curl http://localhost:<port>/health
  sleep 2
done
```

---

## 2. Восстановление базы данных

### 2.1 PostgreSQL

#### Бэкап

```bash
# Создать бэкап
docker exec postgresql pg_dump -U postgres portfolio_db > backup_$(date +%Y%m%d).sql

# Сохранить в безопасное место
cp backup_$(date +%Y%m%d).sql /secure/backup/location/
```

#### Восстановление

```bash
# Остановить сервисы, использующие БД
docker-compose stop auth_service portfolio_organizer

# Восстановить из бэкапа
docker exec -i postgresql psql -U postgres -d portfolio_db < backup_20260518.sql

# Запустить сервисы
docker-compose start auth_service portfolio_organizer

# Проверить целостность
docker exec -it postgresql psql -U postgres -c "SELECT COUNT(*) FROM users;"
```

#### Сброс (для разработки)

```bash
# Остановить БД
docker-compose stop postgresql

# Удалить том данных
docker volume rm portfolio-system-architect_postgres_data

# Запустить заново
docker-compose up -d postgresql

# Инициализировать схему
docker exec -it postgresql psql -U postgres -c "CREATE DATABASE portfolio_db;"
```

### 2.2 Redis

#### Очистка кэша

```bash
# Подключиться к Redis
docker exec -it redis redis-cli

# Очистить все ключи
FLUSHALL

# Или конкретную базу
SELECT 0
FLUSHDB
```

#### Восстановление после сбоя

```bash
# Проверить состояние
docker exec redis redis-cli INFO

# Перезапустить
docker-compose restart redis

# Проверить подключение
curl http://localhost:6379
```

### 2.3 ChromaDB (векторная БД)

#### Восстановление индекса

```bash
# Остановить сервисы
docker-compose stop knowledge_graph decision_engine

# Сохранить текущие данные (если нужно)
cp -r data/chroma data/chroma_backup

# Очистить индекс
rm -rf data/chroma/*

# Запустить сервисы
docker-compose up -d knowledge_graph decision_engine

# Перестроить индекс (если есть скрипт)
python scripts/rebuild_rag_index.py
```

---

## 3. Откат деплоя

### 3.1 Откат Docker-образов

```bash
# 1. Посмотреть историю образов
docker images | grep <service-name>

# 2. Остановить текущую версию
docker-compose stop <service-name>

# 3. Запустить предыдущую версию
docker tag <service-name>:previous-version <service-name>:latest
docker-compose up -d <service-name>

# 4. Проверить здоровье
curl http://localhost:<port>/health
```

### 3.2 Откат в Kubernetes

```bash
# 1. Посмотреть историю деплоев
kubectl rollout history deployment/<service-name>

# 2. Откатить на предыдущую версию
kubectl rollout undo deployment/<service-name>

# 3. Проверить статус
kubectl rollout status deployment/<service-name>

# 4. Проверить поды
kubectl get pods -l app=<service-name>
```

### 3.3 Откат конфигурации

```bash
# 1. Найти предыдущую версию конфига
git log config/ai-config.yaml

# 2. Откатить файл
git checkout <commit-hash> config/ai-config.yaml

# 3. Подтвердить изменения
git commit -m "rollback: откат конфигурации к версии X"

# 4. Перезагрузить конфигурацию
curl -X POST http://localhost:8100/api/v1/config/reload
```

---

## 4. Реакция на инциденты

### 4.1 Классификация инцидентов

| Уровень | Описание | Время реакции | Примеры |
|---------|----------|---------------|---------|
| **P1** | Критический | < 15 мин | Все сервисы недоступны, потеря данных |
| **P2** | Высокий | < 1 час | Основной функционал не работает |
| **P3** | Средний | < 4 часа | Частичная функциональность |
| **P4** | Низкий | < 24 часа | UI баги, косметические проблемы |

### 4.2 Процесс реагирования

#### Шаг 1: Идентификация

```bash
# Проверить мониторинг
open http://localhost:3000  # Grafana

# Проверить алерты
docker-compose logs | grep -i "error\|critical\|fatal"

# Проверить health checks
for service in $(docker-compose ps -q); do
  echo "Checking $service"
  docker inspect --format='{{.State.Health.Status}}' $service
done
```

#### Шаг 2: Изоляция

```bash
# Если сервис вызывает каскадные сбои
docker-compose stop <problematic-service>

# Или ограничить трафик через Traefik
# (редактировать docker-compose.yml или K8s манифесты)
```

#### Шаг 3: Диагностика

```bash
# Проверить логи
docker-compose logs -f <service-name> --tail=200

# Проверить метрики
curl http://localhost:<port>/metrics

# Воспроизвести проблему (если возможно)
# См. docs/TESTING_STRATEGY.md
```

#### Шаг 4: Восстановление

```bash
# Применить решение из раздела 1
# Или откатить версию из раздела 3
```

#### Шаг 5: Пост-мортем

После устранения инцидента создать отчёт:

```markdown
# Пост-мортем инцидента [ДАТА]

## Краткое описание
[Что произошло]

## Время линии
- [HH:MM] Обнаружение
- [HH:MM] Реакция
- [HH:MM] Изоляция
- [HH:MM] Восстановление
- [HH:MM] Завершение

## Причина
[Корневая причина]

## Действия по предотвращению
1. [Действие 1]
2. [Действие 2]

## Ответственные
- [Имя] — [Задача]
```

---

## 5. Daily Checks

### 5.1 Утренний чек (5 минут)

```bash
# 1. Проверить все сервисы
docker-compose ps

# Ожидаемый результат: все сервисы "Up"

# 2. Проверить ошибки в логах (последние 24 часа)
docker-compose logs --since=24h | grep -i "error\|critical"

# 3. Проверить диск
df -h

# 4. Проверить мониторинг
open http://localhost:3000/d/services

# 5. Проверить алерты
open http://localhost:9090/alerts
```

### 5.2 Еженедельный чек (15 минут)

```bash
# 1. Проверить покрытие тестами
pytest --cov=apps --cov-report=term-missing

# 2. Проверить уязвимости
trivy fs .

# 3. Проверить бэкапы
ls -lh /secure/backup/location/

# 4. Проверить метрики производительности
# См. Grafana dashboard "Performance Overview"

# 5. Очистить старые логи
docker system prune -f --filter "until=24h"
```

### 5.3 Чек-лист

```markdown
## Ежедневный чек-лист [ДАТА]

- [ ] Все сервисы Up (docker-compose ps)
- [ ] Нет критических ошибок в логах
- [ ] Диск < 80% заполнен
- [ ] Метрики в норме (Grafana)
- [ ] Нет активных алертов (Prometheus)
- [ ] Бэкапы актуальны

Подпись: ____________
```

---

## 6. Контакты и эскалация

### 6.1 Команда

| Роль | Имя | Контакт | Время доступности |
|------|-----|---------|-------------------|
| **Tech Lead** | [Имя] | [email/telegram] | 24/7 |
| **DevOps** | [Имя] | [email/telegram] | 9-18 |
| **Backend Lead** | [Имя] | [email/telegram] | 9-18 |

### 6.2 Эскалация

1. **P1 инцидент:**
   - Сразу: Telegram-чат команды
   - Через 15 мин: Звонок Tech Lead
   - Через 30 мин: Звонок CTO

2. **P2 инцидент:**
   - Сразу: Telegram-чат команды
   - Через 1 час: Уведомление Tech Lead

3. **P3/P4 инцидент:**
   - Создать Issue в GitHub
   - Назначить ответственного

### 6.3 Важные ссылки

| Ресурс | URL | Назначение |
|--------|-----|------------|
| **Grafana** | http://localhost:3000 | Мониторинг |
| **Prometheus** | http://localhost:9090 | Метрики |
| **Traefik Dashboard** | http://localhost:8080 | API Gateway |
| **GitHub Issues** | [ссылка] | Трекинг багов |
| **Документация** | [ссылка] | ADR, архитектура |

---

## Приложения

### A. Команды быстрого доступа

```bash
# Перезапустить все сервисы
docker-compose restart

# Посмотреть логи всех сервисов
docker-compose logs -f

# Остановить всё
docker-compose down

# Полная очистка
docker-compose down -v
docker system prune -f

# Проверить сеть
docker network inspect portfolio-system-architect_default

# Проверить тома
docker volume ls
```

### B. Порты сервисов

| Сервис | Порт | Health Check |
|--------|------|--------------|
| cognitive-agent | 8001 | /health |
| decision_engine | 8002 | /health |
| auth_service | 8100 | /health |
| portfolio_organizer | 8200 | /health |
| system_proof | 8300 | /health |
| knowledge_graph | 8400 | /health |
| thought-architecture | 8500 | /health |
| infra-orchestrator | 8200 | /health |
| ai-config-manager | 8100 | /health |
| it_compass | 8501 | /health |
| mcp_server | 8000 | /health |
| ml_model_registry | 8003 | /health |
| career_development | 8004 | /health |
| job-automation-agent | 8005 | /health |
| template-service | 8900 | /health |

---

*Последнее обновление: 18 мая 2026 г.*
*Следующее обновление: после каждого значимого инцидента*
