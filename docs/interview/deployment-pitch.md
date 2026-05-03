# 💬 Питч: "Как устроен ваш деплой?"

> Готовые ответы для собеседований и презентаций портфолио.
> Не перечисляй инструменты — рассказывай историю.

---

## Коротко (30 секунд)

> «От локального docker-compose до GitOps в Kubernetes. Разработчик запускает `make dev`, а в продакшене изменение в Git автоматически деплоится через ArgoCD с мониторингом и безопасными секретами.»

---

## Подробно (2–3 минуты)

### 1. Локальная разработка — скорость
- **Docker Compose + Traefik** — одна команда `make dev` поднимает 14 микросервисов, PostgreSQL, Redis и мониторинг.
- Разработчик не тратит время на ручную настройку окружения.

### 2. Тестирование — гибкость
- **Kustomize overlays** (dev / staging / prod) подменяют конфиги, ресурсы и домены.
- Staging работает на GCP Free Tier — минимальные затраты, максимум проверок.

### 3. Продакшен — надёжность
- **GitOps (ArgoCD)** — единственный источник правды: Git.
- Изменение в репозитории = автоматический деплой в кластер.
- **Self-heal** — ArgoCD откатывает ручные правки в K8s.
- **HPA** — автомасштабирование под нагрузкой.
- **Sealed Secrets** — секреты хранятся в Git безопасно.

### 4. Облако — переносимость
- **Azure Web App** — при необходимости проект деплоится через GitHub Actions с OIDC (без долгоживущих секретов).
- Инфраструктура как код делает миграцию между облаками простой.

---

## Что это показывает интервьюеру

| Качество | Доказательство |
|----------|----------------|
| 🧠 **Архитектурное мышление** | Выбор инструмента под задачу: Compose → Kustomize → ArgoCD |
| 🔁 **Полный цикл CI/CD** | От commit до production — автоматизация на каждом шаге |
| 🛡️ **Security-first** | Sealed Secrets, OIDC, Network Policies |
| 📈 **Масштабируемость** | HPA, multi-environment, облако-агностичность |
| 🤝 **DevEx** | `make dev` — один вход для всей команды |

---

## Возможные уточняющие вопросы и ответы

**Q: Почему Kustomize, а не Helm?**
> «Kustomize проще для мульти-окружений без шаблонизаторов. Нам не нужен Jinja-подобный синтаксис — чистые YAML + патчи. Это снижает порог входа для команды и упрощает code review.»

**Q: Почему ArgoCD, а не Flux?**
> «ArgoCD даёт визуальный UI для синхронизации и отката — это удобно для команды. Flux тоже поддерживается через конфигурацию, но ArgoCD — наш основной выбор для GitOps.»

**Q: Как вы управляете секретами?**
> «Sealed Secrets — секреты шифруются публичным ключом кластера и хранятся в Git. Расшифровка только внутри кластера. Никаких `.env` в репозитории.»

**Q: Что при переносе в другое облако?**
> «Kustomize + контейнеры = облако-агностичность. Меняем только Ingress-контроллер и провайдер K8s. Вся логика деплоя остаётся прежней.»

---

## Ссылки

- [deployment/README.md](../../deployment/README.md) — полная документация по деплою
- [deployment/k8s/README.md](../../deployment/k8s/README.md) — руководство по Kubernetes
- [deployment/gitops/README.md](../../deployment/gitops/README.md) — настройка ArgoCD



В вашем проекте **Portfolio System Architect** доступны следующие инструменты и подходы к деплою:

---

## 1. Docker Compose (локальная разработка)

- **Файлы**: `docker-compose.yml`, `docker-compose.monitoring.yml`, `docker/docker-compose.*.yml`
- **Назначение**: локальный запуск всей экосистемы (14 микросервисов, PostgreSQL, Redis, Traefik, мониторинг)
- **Команды**:
  ```bash
  make dev          # запуск всех сервисов
  make docker-up    # алиас для docker-compose up
  make docker-build # сборка образов
  ```

---

## 2. Kubernetes + Kustomize

- **Путь**: `deployment/k8s/`
- **Структура**: `base/` + `overlays/` (dev / staging / prod)
- **Что разворачивается**:
  - 8 микросервисов (Deployment + Service + ConfigMap)
  - PostgreSQL (StatefulSet)
  - Ingress-роутинг
  - HPA (автомасштабирование)
  - Network Policies
- **Команды**:
  ```bash
  kubectl apply -k deployment/k8s/overlays/dev
  kubectl apply -k deployment/k8s/overlays/staging
  kubectl apply -k deployment/k8s/overlays/prod
  ```

---

## 3. GitOps (ArgoCD / Flux)

- **Путь**: `deployment/gitops/`
- **ArgoCD**: приложение `portfolio-system` с авто-синхронизацией и self-heal
- **FluxCD**: поддержка `flux bootstrap github`
- **GitHub Actions**: `.github/workflows/gitops-argocd.yml` — синхронизация приложения в кластере по пушу или вручную

---

## 4. GitHub Actions (CI/CD)

| Workflow | Назначение |
|----------|-----------|
| `ci.yml` | Тесты, покрытие, линтинг |
| `deploy-k8s.yml` | Сборка Docker-образов → деплой в K8s (staging / production) |
| `azure-deploy.yml` | Деплой в **Azure Web App** (OIDC, контейнеры) |
| `gitops-argocd.yml` | Синхронизация через ArgoCD |
| `deploy-pages.yml` | Деплой документации (MkDocs) |
| `security-scan.yml` | Trivy + Bandit сканирование |

---

## 5. Azure (облачный деплой)

- **Файл**: `.github/workflows/azure-deploy.yml`
- **Цель**: Azure Web App + Container Registry (GHCR)
- **Аутентификация**: OIDC (без секретов в репозитории)

---

## 6. Дополнительно

| Инструмент | Где находится | Для чего |
|------------|---------------|----------|
| **Traefik v3** | `docker-compose.yml` | API Gateway / Ingress локально |
| **Sealed Secrets** | `deployment/secrets/` | Безопасное хранение секретов в Git |
| **Kubectl + Helm** | `deployment/k8s/README.md` | Prometheus/Grafana в production |
| **Makefile** | корень | `make docker-up`, `make docker-build`, `make ci` |

---

Если хотите, могу показать конкретный пайплайн деплоя или помочь настроить новое окружение.
