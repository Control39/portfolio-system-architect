# Portfolio System Architect

> **Cognitive Systems Architect** | 14 микросервисов | 83 маркера компетенций | Production-ready

[![CI](https://img.shields.io/github/actions/workflow/status/Control39/portfolio-system-architect/ci.yml?logo=github&style=flat-square)](https://github.com/Control39/portfolio-system-architect/actions)
[![Coverage](https://img.shields.io/codecov/c/github/Control39/portfolio-system-architect?logo=codecov&style=flat-square)](https://app.codecov.io/github/Control39/portfolio-system-architect)
[![K8s](https://img.shields.io/badge/Kubernetes-ready-326CE5?logo=kubernetes&style=flat-square)](deployment/k8s/README.md)
[![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo&style=flat-square)](deployment/gitops/README.md)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&style=flat-square)](docker-compose.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&style=flat-square)](https://python.org)
[![License](https://img.shields.io/github/license/Control39/portfolio-system-architect?style=flat-square)](LICENSE)

---

## 🎯 Для HR и Hiring Manager

**[📄 One-Pager (3 min read)](docs/ONE-PAGER.md)** | **[💼 Полное портфолио](docs/FOR-EMPLOYER.md)** | **[📊 Бизнес-кейсы](docs/cases/business-impact/)**

**Ключевые достижения:**
- Трансформация из **non-IT** в **Cognitive Systems Architect** за 2 года
- 14 интегрированных микросервисов, 12 контейнеризированы, Kubernetes-ready
- 83 верифицируемых маркера компетенций (IT-Compass методология)
- 95%+ покрытие тестами, полный мониторинг (Prometheus/Grafana)

**Позиция:** Solutions Architect / Platform Architect / Tech Lead
**Локация:** Москва (удалённо / гибридно)
**Зарплатные ожидания:** 300-400k ₽

---

## 🏗️ Архитектура

### Основные компоненты

| Компонент | Описание | Статус |
|-----------|----------|--------|
| **Cognitive Automation Agent** (`apps/cognitive-agent/`) | Автономная автоматизация DevOps: тесты, деплои, сканы безопасности | ✅ |
| **IT-Compass** (`apps/it_compass/`) | Методология измерения компетенций: 83 маркера в 19 доменах | ✅ |
| **Decision Engine** (`apps/decision-engine/`) | AI-принятие решений с объяснимой логикой (RAG + reasoning) | ✅ |
| **Portfolio Organizer** (`apps/portfolio_organizer/`) | Автоматический сбор доказательств компетенций | ✅ |
| **System Proof** (`apps/system-proof/`) | Валидация production-ready критериев | ✅ |
| **ML Model Registry** (`apps/ml-model-registry/`) | Версионирование ML-моделей с A/B тестированием | ✅ |
| **Auth Service** (`apps/auth_service/`) | JWT аутентификация и авторизация | ✅ |
| **MCP Server** (`mcp-server/`) | Unified AI agent interface (Claude Desktop, VS Code, Koda) | ✅ |
| **12+ микросервисов** | FastAPI, PostgreSQL, ChromaDB, Redis, Traefik | ✅ |

### Инфраструктура

- **CI/CD:** GitHub Actions + GitOps (Kustomize)
- **Деплой:** [Docker Compose → Kustomize → GitOps (ArgoCD)](deployment/README.md)
- **Dev Environment:** [Dev Container](.devcontainer/) — полная среда разработки в VS Code (Python 3.12, Docker-in-Docker, Terraform, все extensions)
- **Оркестрация:** Kubernetes (Kustomize overlays: dev/staging/prod)
- **Мониторинг:** Prometheus + Grafana + AlertManager
- **Безопасность:** Trivy, Bandit, Sealed Secrets, network policies
- **База данных:** PostgreSQL 16, ChromaDB (векторная), Redis 7

---

## 🚀 Быстрый старт

```bash
# Установка
make install

# Запуск всех сервисов локально
make dev

# Тесты (95%+ покрытие)
make test

# CI/CD проверка
make ci

# Деплой в Kubernetes (staging)
kubectl apply -k deployment/k8s/overlays/staging
```

> 💡 **Dev Container:** Открой проект в VS Code → «Reopen in Container» — получишь полностью настроенную среду (Python 3.12, Docker, Terraform, все extensions) без установки зависимостей на хост. Подробности в [`.devcontainer/README.md`](.devcontainer/README.md).
```

📖 **Полная документация:** [`docs/QUICKSTART.md`](docs/QUICKSTART.md)
🚀 **Стратегия деплоя:** [`deployment/README.md`](deployment/README.md)
💬 **Питч для собеседований:** [`docs/interview/deployment-pitch.md`](docs/interview/deployment-pitch.md)

---

## 📊 Метрики качества

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Покрытие тестами** | 95%+ | ✅ |
| **Безопасность** | Trivy, Bandit, Sealed Secrets | ✅ |
| **CI/CD** | GitHub Actions + GitOps | ✅ |
| **Мониторинг** | Prometheus + Grafana | ✅ |
| **Документация** | ADR, OPENAPI, методология | ✅ |

📈 **Детальные метрики:** [`docs/quality-gates.md`](docs/quality-gates.md)

---

## 🧠 Методология

### IT-Compass
- **83 проверочных маркера** в **19 IT-доменах**
- Модульный Python-пакет с JSON-схемой
- Streamlit UI для визуализации
- Психологическая поддержка (профилактика выгорания)

### Reasoning System
- Объяснимые архитектурные решения (ADR)
- Интерактивная визуализация логических цепочек
- Цветовое кодирование по направлениям (DevOps, MLOps, Analytics)

### AI Orchestration
- **ИИ как исполнительный слой** под строгим архитектурным контролем
- Contract-first дизайн
- Автоматическая валидация и тестирование

📚 **Методология:** [`docs/methodology/`](docs/methodology/)
🧠 **Архитектурные решения:** [`docs/architecture/decisions/`](docs/architecture/decisions/)

---

## 📁 Структура проекта

```
```
portfolio-system-architect/
├── apps/                    # 14 микросервисов — независимые deployable-юниты [правила](apps/README.md)
│   ├── auth_service/        # JWT аутентификация
│   ├── decision-engine/     # RAG + reasoning API
│   ├── it_compass/          # IT Compass UI
│   ├── ml-model-registry/   # Реестр ML моделей
│   └── ... (ещё 10 сервисов)
├── src/                     # Общие ядра и библиотеки — импортируются apps/ [правила](src/README.md)
│   ├── common/              # health_check, async_helpers
│   ├── config/              # загрузка конфигураций
│   ├── embedding_agent/     # RAG/эмбеддинги
│   └── security/            # компоненты безопасности
├── deployment/              # Kubernetes, GitOps, Sealed Secrets — [стратегия деплоя](deployment/README.md)
├── monitoring/              # Prometheus, Grafana
├── docs/                    # Документация, кейсы, методология
├── tools/                   # Утилиты аудита, CI/CD, security
└── .codeassistant/          # AI валидация и анализ
```

> 📋 **Граница `src/` vs `apps/`:** `src/` — общие библиотеки (2+ импортёра), `apps/` — независимые сервисы с Dockerfile. Подробности в [ADR-015](docs/architecture/decisions/ADR-015-monorepo-boundary.md).
```

---

## 📈 Кейсы и доказательства

### 🔧 Infrastructure Sync & Hardening (2026-04)
**Проблема:** Diverged remotes, ~65k строк технического долга.
**Решение:** Branch audit, ручное разрешение конфликтов, protected branch cleanup.
**Результат:** `-65 510` строк, полная синхронизация, security patches.
[📄 Читать кейс](docs/cases/infra-sync-hardening-2026.md)

### 🧠 AI Orchestration Success
**Проблема:** Ограниченные контекстные окна в free AI (4K-8K токенов).
**Решение:** Модульная декомпозиция, contract-first дизайн, итеративная валидация.
**Результат:** 12 интегрированных компонентов, 95%+ покрытие, 10+ ADR.
[📄 ADR](docs/architecture/decisions/)

---

## 🤝 Вклад и сообщество

Приветствуются:
- **Фидбек** по архитектурным решениям
- **Коллаборация** по issue и feature requests
- **Обсуждение** AI orchestration и system thinking

📖 [`CONTRIBUTING.md`](CONTRIBUTING.md) | [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)

---

## 📄 Лицензия

MIT License - см. [`LICENSE`](LICENSE)

---

## 📞 Контакты

**Екатерина Куделя** — Cognitive Systems Architect
📧 leadarchitect@yandex.ru
🌐 [GitHub](https://github.com/Control39) | [SourceCraft](https://sourcecraft.dev/leadarchitect-ai)

---

*Последнее обновление: Май 2026*
