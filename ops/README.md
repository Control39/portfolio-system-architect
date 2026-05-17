# Ops — Операционная документация

> **Цель:** Быстрое восстановление при инцидентах, стандартизация процессов

---

## 📚 Runbooks

| Runbook | Назначение | Время восстановления |
|---------|------------|---------------------|
| [service-down.md](runbooks/service-down.md) | Восстановление упавшего сервиса | <5 мин |
| [db-recovery.md](runbooks/db-recovery.md) | Восстановление PostgreSQL | <10 мин |
| [deployment-rollback.md](runbooks/deployment-rollback.md) | Откат деплоя | <5 мин |
| [incident-response.md](runbooks/incident-response.md) | Процесс реагирования на инциденты | <5 мин (реакция) |
| [checklist.md](runbooks/checklist.md) | Ежедневные проверки | ~10 мин |

---

## 🚨 Критические сценарии

### Сервис упал
1. `.
avigate.ps1 -Status` — проверить статус
2. `docker-compose logs <service> --tail=100` — посмотреть логи
3. `docker-compose restart <service>` — перезапустить
4. Если не помогло → [service-down.md](runbooks/service-down.md)

### База данных недоступна
1. `docker-compose ps postgresql` — проверить статус
2. `docker-compose logs postgresql` — посмотреть логи
3. `docker-compose restart postgresql` — перезапустить
4. Если не помогло → [db-recovery.md](runbooks/db-recovery.md)

### Проблема после деплоя
1. `kubectl rollout status` — проверить статус деплоя
2. `kubectl rollout undo` — откатить
3. См. [deployment-rollback.md](runbooks/deployment-rollback.md)

---

## 📊 Мониторинг

- **Grafana:** http://localhost:3000
- **Prometheus:** http://localhost:9090
- **AlertManager:** http://localhost:9093

---

## 📞 Контакты

| Роль | Контакт | Время реакции |
|------|---------|---------------|
| On-call | leadarchitect@yandex.ru | <5 мин |
| Tech Lead | Telegram: @yourhandle | <15 мин |
| CTO | Email | <1 час |

---

## 🔄 Процесс

1. **Обнаружение** (автоматическое через AlertManager)
2. **Оценка** (определить уровень P0-P3)
3. **Митигация** (восстановить сервис любым способом)
4. **Восстановление** (проверить все системы)
5. **Пост-мортем** (создать issue, предотвратить повторение)

---

## 📈 Метрики

- **MTTD** (Mean Time To Detect): Целевое <2 мин
- **MTTR** (Mean Time To Resolve): Целевое <15 мин
- **Инцидентов в месяц**: Целевое <5
- **P0 инциденты**: Целевое 0

---

*Last updated: 18 мая 2026*
