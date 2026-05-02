# Infra-Orchestrator Framework 🔧

> 🟢 **Status:** Production-ready (core) | 🟡 Beta (AI providers) | 🔴 Alpha (diagnostics)
> **Role:** PowerShell as an orchestration language for infrastructure automation
> **Approach:** I design modular interfaces, security contracts, and AI-integration points; code is generated under architectural guidance and validated via tests
> **Result:** A containerized, self-auditing library for managing AI workflows, secrets, and DevOps processes

**Автор:** Екатерина Куделя, архитектор когнитивных систем
**Лицензия:** CC BY-ND 4.0 (методология), MIT (код)

---

## 🎬 Пример использования за 30 секунд

### Вариант 1: Через Docker (без клонирования) ✨
```powershell
# Просто скопируй и вставь — работает сразу:
docker run --rm ghcr.io/control39/infra-orchestrator:latest Start-InfraOrchestrator -Version
```

### Вариант 2: Локально (если хочешь изучить код)
```powershell
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect/apps/infra-orchestrator
Import-Module ./InfraOrchestrator.psm1 -Force
Start-InfraOrchestrator -Health
```

> 💡 **Совет:** Все команды поддерживают `-WhatIf` для «сухого прогона» без реальных изменений.

---

## 🎯 Назначение

**Arch-Compass Framework** — это библиотека PowerShell-модулей для оркестрации AI-рабочих процессов и инфраструктурной автоматизации.

**Основная функция:** Единая точка управления для распределённой экосистемы микросервисов.

**Ключевые возможности:**
- **AI Provider Abstraction** — управление разнородными LLM-провайдерами (OpenAI, YandexGPT, LocalLLM) через единый интерфейс `IAiProvider`
- **Configuration & Secrets Management** — валидация конфигураций и безопасное хранение секрентов перед выполнением операций
- **Observability** — экспорт метрик в Prometheus-формате для мониторинга инфраструктуры как кода
- **Architectural Compliance** — генерация отчётов о соответствии архитектурным контрактам (Mermaid/PlantUML)
- **Self-Audit** — автоматическая проверка здоровья всех модулей и их зависимостей

> 💡 **Архитектурная философия:** PowerShell используется как язык оркестрации (orchestration language), где каждый модуль имеет явный контракт, тесты на Pester и точку интеграции в CI/CD. Это не «админские скрипты», а инфраструктурный код уровня enterprise.

---

## 🚀 Быстрый старт

### Локально (PowerShell 7+)
```powershell
Import-Module ./InfraOrchestrator.psm1 -Force
Start-InfraOrchestrator -Environment development -Help
```

### В контейнере (Docker)
```bash
docker run --rm infra-orchestrator:latest
# Или интерактивно:
docker run -it --rm infra-orchestrator:latest pwsh
```

### Проверка состояния (self-audit)
```powershell
Start-InfraOrchestrator -Health -Detailed
```

---

## 🏗️ Архитектурные особенности

| Аспект | Реализация | Доказательство |
|--------|-----------|---------------|
| **Модульность** | Динамическая загрузка подмодулей через массив `$modules` | `InfraOrchestrator.psm1`, строки 6–24 |
| **Контракты** | Интерфейсы в `src/core/contracts/` (IModule, IAiProvider) | `Validate-Contract.ps1` + Pester-тесты |
| **Безопасность** | SecretManager + gitleaks + маскирование в логах | `.gitleaks.toml`, `SecurityScanner.psm1` |
| **Наблюдаемость** | Экспорт метрик в Prometheus-формат | `MetricsExporter.psm1`, `EXPOSE 9091` в Dockerfile |
| **Тестируемость** | Pester + PSScriptAnalyzer в CI | `tests/*.Tests.ps1` (15+ тестов), GitHub Actions |
| **AI-оркестрация** | 3 провайдера (OpenAI, YandexGPT, LocalLLM) через фабрику | `src/ai/providers/`, `AiProviderFactory.psm1` |

---

## 🔐 Безопасность (детали)

### Управление секретами
- **SecretManager.psm1**: хранение в зашифрованном виде, поддержка Azure Key Vault / HashiCorp Vault (заглушки)
- **Маскирование**: автоматическое скрытие значений в логах через `StructuredLogger.psm1`
- **Валидация**: проверка на хардкод перед выполнением команд

### Сканирование уязвимостей
```powershell
# Запуск gitleaks с кастомными правилами
Start-InfraOrchestrator -RunSecurityTests

# Локальное сканирование репозитория
gitleaks detect --source . --config .gitleaks.toml --report-path reports/gitleaks.json
```

### Интеграция с CI/CD
Файл `.github/workflows/infra-orchestrator-ci.yml` (если есть) или пример:
```yaml
- name: Run security scan
  run: pwsh -Command "Import-Module ./InfraOrchestrator.psm1; Start-InfraOrchestrator -RunSecurityTests"
```

---

## 🤖 AI-провайдеры

Фреймворк поддерживает три провайдера LLM через единый интерфейс `IAiProvider`:

| Провайдер | Описание | Поддерживает | Сценарий использования |
|-----------|----------|--------------|------------------------|
| **OpenAI** | GPT-4o, GPT-3.5 | Completion, Embeddings | Продуктивные задачи, высокое качество |
| **YandexGPT** | Yandex Cloud (РФ) | Completion | 152-ФЗ compliance, русскоязычные задачи |
| **LocalLLM** | Ollama, vLLM, LM Studio | Completion, Embeddings | Оффлайн-режим, приватность |

### Использование

```powershell
# OpenAI
$openai = Get-AiProvider -Name 'OpenAI' -Config @{
    ApiKey = 'your-api-key'
    Model = 'gpt-4o'
}
Invoke-Completion -Prompt "Архитектурный анализ..."

# YandexGPT (для российских enterprise-кейсов)
$yandex = Get-AiProvider -Name 'YandexGPT' -Config @{
    ApiKey = 'yandex-api-key'
    FolderId = 'your-folder-id'
}

# LocalLLM (полная приватность)
$local = Get-AiProvider -Name 'LocalLLM' -Config @{
    Endpoint = 'http://localhost:11434'
    Model = 'llama3'
}
```

### Тесты

Все провайдеры покрыты Pester-тестами:
```powershell
Invoke-Pester -Path './tests/OpenAiProvider.Tests.ps1'
Invoke-Pester -Path './tests/YandexGptProvider.Tests.ps1'
Invoke-Pester -Path './tests/LocalLlmProvider.Tests.ps1'
Invoke-Pester -Path './tests/AiProviderFactory.Tests.ps1'
```

---

## 🔗 Интеграции в экосистеме

| Компонент | Назначение | Ссылка (относительная) |
|-----------|-----------|------------------------|
| **IT-Compass** | Передаёт маркеры компетенций для аудита использования фреймворка | [`../../apps/it-compass/`](../../apps/it-compass/) |
| **Cloud-Reason** | Получает контекст для валидации архитектурных решений | [`../../apps/decision-engine/`](../../apps/decision-engine/) |
| **Portfolio-Organizer** | Принимает отчёты о выполнении команд для генерации доказательств | [`../../apps/portfolio_organizer/`](../../apps/portfolio_organizer/) |
| **Terraform modules** | Деплой инфраструктуры (GCP GKE, Yandex Cloud) | [`../../deployment/terraform/`](../../deployment/terraform/) |

> ⚠️ Пути относительные от `apps/infra-orchestrator/README.md`. На GitHub они кликабельны.

---

## 📊 Статус компонента

| Модуль | Статус | Тесты | Docker | Готовность |
|--------|--------|-------|--------|-----------|
| Core (ConfigurationManager, InputValidator) | ✅ Стабильно | ✅ Pester | ✅ | Production |
| Security (SecretManager, SecurityScanner) | ✅ Стабильно | ✅ Pester + gitleaks | ✅ | Production |
| AI Providers (OpenAI, YandexGPT, LocalLLM) | ✅ Готово | ✅ Pester (15+ тестов) | ✅ | Beta → Ready |
| Diagnostics (HealthCheck, MetricsExporter) | 🟢 Новый | ✅ Базовые | ✅ | Alpha |
| Integrations (CompassAudit) | 🔴 Концепт | ❌ | ❌ | Prototype |

**Общая готовность:** ✅ Контейнеризирован, self-audit работает, AI-провайдеры протестированы, можно демонстрировать.

---

## 🧭 Как использовать в портфолио

### Для работодателя (коротко):
> «Infra-Orchestrator: PowerShell-библиотека для оркестрации ИИ и инфраструктуры. Контейнеризирована, имеет self-audit, экспортирует метрики в Prometheus. Доказывает, что я проектирую интерфейсы и контракты, а не просто пишу скрипты.»

### Для технического собеседования (детали):
- Покажи `InfraOrchestrator.psm1` → динамическая загрузка модулей
- Покажи `src/core/contracts/` → явные интерфейсы
- Запусти `Start-InfraOrchestrator -Health` → само-аудит в действии
- Открой `Dockerfile` → минималистичный, переносимый образ

### Для грантовой комиссии:
- Ссылка на методологию: [`../../docs/methodology/`](../../docs/methodology/)
- Ссылка на кейс инфраструктурного харденинга: [`../../docs/cases/infra-sync-hardening-2026.md`](../../docs/cases/infra-sync-hardening-2026.md)

---

## 📁 Структура (кратко)

```
infra-orchestrator/
├── InfraOrchestrator.psd1 / psm1   # Манифест и точка входа
├── src/
│   ├── core/                 # ConfigurationManager, InputValidator, contracts/
│   ├── infrastructure/       # SecretManager, SecurityScanner, GitHelper
│   ├── ai/providers/         # IAiProvider + реализации
│   └── diagnostics/          # HealthCheck, MetricsExporter, ArchitectureReport
├── tests/                    # Pester-тесты + pester.config.ps1
├── .gitleaks.toml           # Правила сканирования секретов
├── Dockerfile                # Минималистичный, переносимый образ
└── README.md                # Этот файл
```

---

## 🤝 Вклад и развитие

- **Хочешь добавить провайдера?** Реализуй интерфейс `IAiProvider` в `src/ai/providers/YourProvider.psm1`
- **Нашёл уязвимость?** Открой Issue с меткой `security` или напиши на `leadarchitect@yandex.ru`
- **Предложение по архитектуре?** Обсудим в `docs/architecture/decisions/`

---

📩 **Контакты**: [GitHub](https://github.com/Control39/portfolio-system-architect) | `leadarchitect@yandex.ru
