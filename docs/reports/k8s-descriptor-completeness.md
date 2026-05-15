# Отчёт о комплектности Kubernetes-дескрипторов

**Дата:** 16 мая 2026 г.
**Цель:** Проверка соответствия между сервисами в `apps/` и их Kubernetes-дескрипторами

---

## 📊 Сводная таблица

| Сервис (apps/) | K8s Service | K8s Deployment | Ingress | Статус |
|----------------|-------------|----------------|---------|--------|
| `auth_service` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `it_compass` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `decision_engine` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `ml_model_registry` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `portfolio_organizer` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `system_proof` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `career_development` | ✅ | ✅ | ❌ | ⚠️ Нет Ingress |
| `cognitive-agent` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `infra-orchestrator` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `job-automation-agent` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `knowledge_graph` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `mcp_server` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `thought-architecture` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `ai-config-manager` | ❌ | ❌ | ❌ | 🔴 Отсутствует |
| `template-service` | ❌ | ❌ | ❌ | 🔴 Отсутствует (удалён) |

---

## ✅ Полностью описанные сервисы (7 шт)

### 1. auth-service
- **Service:** ✅ `deployment/k8s/base/services/auth-service/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/auth-service/deployment.yaml`
- **Порт:** 8100
- **Namespace:** portfolio

### 2. it-compass
- **Service:** ✅ `deployment/k8s/base/services/it-compass/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/it-compass/deployment.yaml`
- **Порт:** 8501
- **Namespace:** portfolio

### 3. decision-engine
- **Service:** ✅ `deployment/k8s/base/services/decision-engine/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/decision-engine/deployment.yaml`
- **Порт:** 8001
- **Namespace:** portfolio

### 4. ml-model-registry
- **Service:** ✅ `deployment/k8s/base/services/ml-model-registry/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/ml-model-registry/deployment.yaml`
- **Порт:** 8001 (⚠️ конфликт с decision-engine!)
- **Namespace:** portfolio

### 5. portfolio-organizer
- **Service:** ✅ `deployment/k8s/base/services/portfolio-organizer/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/portfolio-organizer/deployment.yaml`
- **Порт:** 8004
- **Namespace:** portfolio

### 6. system-proof
- **Service:** ✅ `deployment/k8s/base/services/system-proof/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/system-proof/deployment.yaml`
- **Порт:** 8003
- **Namespace:** portfolio

### 7. career-development
- **Service:** ✅ `deployment/k8s/base/services/career-development/service.yaml`
- **Deployment:** ✅ `deployment/k8s/base/services/career-development/deployment.yaml`
- **Порт:** 8000
- **Namespace:** portfolio

---

## 🔴 Сервисы без K8s дескрипторов (7 шт)

### Отсутствующие в deployment/k8s/:
1. **cognitive-agent** — главный продукт проекта, критично!
2. **infra-orchestrator** — оркестрация инфраструктуры
3. **job-automation-agent** — автоматизация поиска работы
4. **knowledge_graph** — граф знаний
5. **mcp_server** — MCP сервер
6. **thought-architecture** — архитектура решений
7. **ai-config-manager** — управление конфигурациями ИИ

---

## ⚠️ Выявленные проблемы

### 1. Конфликт портов
- **decision-engine** и **ml-model-registry** используют порт `8001`
- **Решение:** В `docker-compose.yml` ml-model-registry перенесён на порт 8002
- **Статус:** K8s дескрипторы не обновлены

### 2. Отсутствие Ingress для всех сервисов
- Единственный Ingress в `deployment/k8s/base/ingress/ingress.yaml`
- Нет маршрутизации по PathPrefix для отдельных сервисов

### 3. Несоответствие имен
- В `apps/`: дефисы (`job-automation-agent`) и подчёркивания (`auth_service`)
- В K8s: только дефисы (`auth-service`, `career-development`)
- **Риск:** путаница при развёртывании

---

## 📈 Метрики комплектности

| Категория | Всего | Есть | Процент |
|-----------|-------|------|---------|
| Сервисы в `apps/` | 14 | - | - |
| K8s Service | - | 7 | 50% |
| K8s Deployment | - | 7 | 50% |
| K8s Ingress | - | 0 (общий) | 0% |
| Полная комплектность | - | 7/14 | 50% |

---

## 🎯 Приоритеты исправлений

### Приоритет 1 (Критично):
1. ✅ Исправить порт `ml-model-registry` в K8s: 8001 → 8002
2. 🔴 Добавить дескрипторы для **cognitive-agent** (основной продукт!)

### Приоритет 2 (Высокий):
3. 🔴 Добавить дескрипторы для остальных 5 сервисов:
   - `infra-orchestrator`
   - `job-automation-agent`
   - `knowledge_graph`
   - `mcp_server`
   - `thought-architecture`

### Приоритет 3 (Средний):
4. 🔴 Добавить Ingress маршрутизацию для всех сервисов
5. 🔴 Стандартизировать имена (дефисы vs подчёркивания)

---

## 📁 Структура K8s

```
deployment/k8s/base/
├── kustomization.yaml           # Основные ресурсы
├── namespace/                   # Namespace "portfolio"
├── postgres/                    # PostgreSQL
│   ├── deployment.yaml
│   └── service.yaml
├── services/                    # Microservices
│   ├── kustomization.yaml       # Включает 7 сервисов
│   ├── auth-service/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── career-development/
│   ├── decision-engine/
│   ├── it-compass/
│   ├── ml-model-registry/
│   ├── portfolio-organizer/
│   └── system-proof/
├── ingress/
│   ├── ingress.yaml
│   ├── kustomization.yaml
│   └── network-policy.yaml
├── security/                    # Security policies
└── backup/                      # Backup конфигурации
```

---

## 📝 Следующие шаги

1. [ ] Исправить порт `ml-model-registry` в K8s (8001 → 8002)
2. [ ] Создать дескрипторы для `cognitive-agent`
3. [ ] Создать дескрипторы для остальных 5 сервисов
4. [ ] Добавить Ingress маршрутизацию (PathPrefix)
5. [ ] Обновить `kustomization.yaml` для включения новых сервисов
6. [ ] Стандартизировать имена сервисов (рекомендация: дефисы)

---

*Отчёт сгенерирован автоматически на основе анализа `apps/` и `deployment/k8s/`*
