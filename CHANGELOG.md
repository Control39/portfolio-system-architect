# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`navigate.ps1`** — PowerShell скрипт навигации по проекту (15 сервисов, инструменты, статус)
- **`START_HERE.md`** — Обновлённое руководство для новичков с актуальными метриками
- **`NEXT_STEPS.md`** — Приоритеты на будущее (TIER 1-3, 90-дневный план)
- AI Config Manager интеграция для **14/14 сервисов** (централизованная конфигурация)
- **5 новых микросервисов** (итого 15): infra-orchestrator, template-service, system-proof, knowledge_graph, thought-architecture
- Методология **Objective Competency Markers** в README.md

### Changed
- **Миграция `infra-orchestrator`** с PowerShell на Python/FastAPI (Dockerfile: `python:3.11-slim`)
- **README.md** — Гибридная версия: методология + GitHub-бейджи + архитектура
- Обновлены метрики: 15 сервисов, ~85% покрытие, 14 ADR, 0 уязвимостей
- Обновлены все упоминания "12 сервисов" → "15 сервисов" в документации
- Исправлены 13 битых ADR-ссылок в README.md
- **START_HERE.md** — Обновлён с актуальными путями и командами PowerShell
- **NEXT_STEPS.md** — Добавлены приоритеты на 2026-05-18

### Fixed
- Удалена битая директория `c:Projectsai-config-manager/`
- Исправлены ссылки на несуществующие скрипты в документации
- Обновлены контакты (email: leadarchitect@yandex.ru)
- Исправлены упоминания дат (15 May → 18 May 2026)

### Removed
- PowerShell файлы `infra-orchestrator/InfraOrchestrator.psd1` и `.psm1`
- Устаревшие упоминания "14 сервисов" в документации

## [0.1.0] - 2026-04-30

### Added
- Initial repository structure with 8 microservices
- Cognitive Automation Agent (CAA) with 5 autonomous skills
- SourceCraft Agent Skills for architectural analysis
- Comprehensive CI/CD pipeline with 25+ GitHub Actions workflows
- Production-ready Kubernetes deployment configurations
- Monitoring stack (Prometheus, Grafana, AlertManager)
- Security scanning (Bandit, Trivy, pip-audit, gitleaks)

### Changed
- Refactored project structure for better modularity
- Standardized coding standards across all components
- Improved test coverage to 85%+

### Fixed
- Technical debt from legacy code
- Security vulnerabilities in dependencies
- Infrastructure synchronization issues

## [0.1.0] - 2026-04-30

### Added
- Initial repository structure with 8 microservices
- Cognitive Automation Agent (CAA) with 5 autonomous skills
- SourceCraft Agent Skills for architectural analysis
- Comprehensive CI/CD pipeline with 25+ GitHub Actions workflows
- Production-ready Kubernetes deployment configurations
- Monitoring stack (Prometheus, Grafana, AlertManager)
- Security scanning (Bandit, Trivy, pip-audit, gitleaks)

### Changed
- Refactored project structure for better modularity
- Standardized coding standards across all components
- Improved test coverage to 85%+

### Fixed
- Technical debt from legacy code
- Security vulnerabilities in dependencies
- Infrastructure synchronization issues

---

## Versioning Policy

- **Major version (X.0.0)**: Breaking changes to architecture or APIs
- **Minor version (0.X.0)**: New features without breaking changes
- **Patch version (0.0.X)**: Bug fixes and security patches

## Release Frequency

- **Monthly**: Minor releases with new features
- **Weekly**: Patch releases for bug fixes
- **As needed**: Security patches within 48 hours of discovery

## How to Update This File

1. For each release, add a new `## [X.Y.Z] - YYYY-MM-DD` section
2. Group changes under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, or `Security`
3. Use bullet points for individual changes
4. Include links to relevant issues or pull requests
5. Update the `Unreleased` section as work progresses

## Links

- [GitHub Releases](https://github.com/Control39/portfolio-system-architect/releases)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Repository Audit Checklist](reports/audit/REPOSITORY_AUDIT_CHECKLIST.md)
