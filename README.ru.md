# Экосистема когнитивной архитектуры

> **Роль:** Архитектор когнитивных систем и оркестратор ИИ
> **Подход:** Код генерируется ИИ под моим строгим архитектурным руководством. Я проектирую систему, создаю методологию, управляю ИИ-исполнителями, валидирую результаты, интегрирую компоненты, настраиваю CI/CD и контролирую качество.
> **Результат:** 14 интегрированных компонентов (12 контейнеризуемых), готовых к production и развёртыванию в Kubernetes.
> **Репозиторий:** [GitHub (Основной)](https://github.com/Control39/portfolio-system-architect) | [SourceCraft (Зеркало)](https://sourcecraft.dev/leadarchitect-ai/portfolio-system-architect)

<!-- Переключатель языка -->
<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/English-🇬🇧-blue?style=flat-square" alt="English"></a>
  <a href="README.ru.md"><img src="https://img.shields.io/badge/Русский-🇷🇺-red?style=flat-square" alt="Русский"></a>
</p>

<!-- Бейджи -->
<p align="center">
  <img src="https://img.shields.io/badge/✅-Production--Ready-blue?style=for-the-badge" alt="Готово к продакшену">
  <img src="https://img.shields.io/badge/✅-GitOps-orange?style=for-the-badge" alt="GitOps">
  <img src="https://img.shields.io/badge/✅-Observability-green?style=for-the-badge" alt="Наблюдаемость">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/CI-GitHub%20Actions-blue?style=flat-square&logo=github" alt="CI: GitHub Actions">
  <img src="https://img.shields.io/badge/Coverage-85%25-brightgreen?style=flat-square" alt="Покрытие тестами">
  <img src="https://img.shields.io/badge/Security-Trivy%20Scan-blue?style=flat-square&logo=trivy" alt="Безопасность: Trivy Scan">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="Лицензия: MIT">
  <img src="https://img.shields.io/badge/Python-3.13.5-blue?style=flat-square&logo=python" alt="Python 3.13.5">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus">
  <img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=for-the-badge&logo=vectorworks&logoColor=white" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
</p>

---

## 🧭 Навигация
| Аудитория | Ссылка | Что внутри |
|-----------|--------|------------|
| 🎯 **HR / Техлид** | [`docs/employer/`](docs/employer/) | Бизнес-ценность, доказательства компетенций, вопросы для интервью |
| 💻 **Инженеры / Архитекторы** | [`docs/architecture/decisions/`](docs/architecture/decisions/) + [`src/`](src/) | ADR, стандарты валидации, паттерны интеграции, ядро системы |
| 🛠️ **DevOps** | [`deployment/`](deployment/) + [`monitoring/`](monitoring/) | GitOps, манифесты K8s, sealed secrets, CI/CD |
| 🌱 **Новички в IT** | [`apps/it-compass/`](apps/it-compass/) + [`docs/cases/`](docs/cases/) | Методология самооценки, кейсы роста, трекинг компетенций |

## 📊 Техническая реализация
| Область | Реализация | Статус |
|---------|------------|--------|
| **Компоненты** | 14 интегрированных компонентов (12 контейнеризуемых) | ✅ Готово к продакшену |
| **CI/CD и GitOps** | GitHub Actions + Kustomize + автоматизация | ✅ Автоматизировано |
| **Наблюдаемость** | Prometheus + Grafana + AlertManager | ✅ Мониторинг активен |
| **Безопасность** | Trivy, Bandit, Sealed Secrets, сетевые политики | ✅ Соответствует стандартам |
| **Тестирование** | Unit, Integration, E2E, Load (85%+ покрытие) | ✅ Верифицировано |
| **Оркестрация ИИ** | RAG + Reasoning для валидации архитектуры | ✅ Операционально |

## 🔄 Мой рабочий процесс
1. **Архитектура и ограничения** → Я определяю границы, контракты, метрики успеха и возможные сбои.
2. **Оркестрация ИИ** → Модели генерируют черновики реализации по моим спецификациям.
3. **Валидация и рефакторинг** → Я проверяю, отклоняю неверные подходы, исправляю edge-cases и поддерживаю стандарты.
4. **Интеграция и деплой** → Я связываю компоненты, настраиваю инфраструктуру, CI/CD и мониторинг.
5. **Доказательства и аудит** → Автосбор через `portfolio-organizer`, проверка через `repo-audit`.

> *ИИ — это слой исполнения. Архитектура, валидация и ответственность — мои.*

## 📁 Структура проекта
```
├── apps/                    # 14 интегрированных микросервисов и компонентов
├── src/                     # Общее ядро, оркестрация ИИ, логика валидации
├── deployment/              # Kubernetes, GitOps, Sealed Secrets
├── monitoring/              # Prometheus, Grafana, AlertManager
├── docs/                    # Архитектурные решения, гайд для работодателя, методология
├── .codeassistant/skills/   # Стандарты валидации ИИ и архитектура промптов
└── tools/                   # Аудит репо, CI/CD, сканеры безопасности
```

## 📚 Кейсы
### 🔧 Синхронизация инфраструктуры и харденинг (2026-04)
**Задача:** Рассинхронизация remotes, конфликт миграции БД, ~65k строк техдолга.
**Решение:** Аудит веток, разрешение конфликта с `psycopg2.sql`, безопасный merge, очистка веток, пиннинг зависимостей.
**Результат:** Удалено 65 510 строк мусора, полная синхронизация, репозиторий чист.
**Полный кейс:** [`docs/cases/infra-sync-hardening-2026.md`](docs/cases/infra-sync-hardening-2026.md)

---
📩 **Контакты**: leadarchitect@yandex.ru | [GitHub](https://github.com/Control39/portfolio-system-architect) | [SourceCraft](https://sourcecraft.dev/leadarchitect-ai/portfolio-system-architect)
