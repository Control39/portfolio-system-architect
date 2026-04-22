# Arch-Compass-Framework 🧭

> 🟢 **Status:** Production-ready (core) | 🟡 Beta (AI providers) | 🔴 Alpha (diagnostics)  
> **Role:** PowerShell as an orchestration language for cognitive architecture  
> **Approach:** I design modular interfaces, security contracts, and AI-integration points; code is generated under architectural guidance and validated via tests  
> **Result:** A containerized, self-auditing framework for managing AI workflows, secrets, and DevOps processes

**Автор:** Екатерина Куделя, архитектор когнитивных систем  
**Лицензия:** CC BY-ND 4.0 (методология), MIT (код)

---

## 🎬 Пример использования за 30 секунд

### Вариант 1: Через Docker (без клонирования) ✨
```powershell
# Просто скопируй и вставь — работает сразу:
docker run --rm ghcr.io/control39/arch-compass:latest Start-ArchCompass -Version
```

### Вариант 2: Локально (если хочешь изучить код)
```powershell
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect/apps/arch-compass-framework
Import-Module ./ArchCompass.psm1 -Force
Start-ArchCompass -Health
```

> 💡 **Совет:** Все команды поддерживают `-WhatIf` для «сухого прогона» без реальных изменений.

---

## 🎯 Назначение

Arch-Compass — это **инфраструктурный оркестратор**, а не бизнес-приложение. Он позволяет:
- Управлять ИИ-провайдерами через единый интерфейс (`Get-AiProvider`)
- Валидировать конфигурации и секреты до выполнения команд
- Экспортировать метрики в Prometheus-формат для наблюдаемости
- Генерировать архитектурные отчёты (Mermaid/PlantUML) автоматически

> 💡 **Ключевая идея:** PowerShell здесь — не «админка для Windows», а язык описания оркестра, где каждый модуль имеет контракт, тесты и точку интеграции.

---

## 🚀 Быстрый старт

### Локально (PowerShell 7+)
```powershell
Import-Module ./ArchCompass.psm1 -Force
Start-ArchCompass -Environment development -Help
```

### В контейнере (Docker)
```bash
docker run --rm arch-compass:latest
# Или интерактивно:
docker run -it --rm arch-compass:latest pwsh
```

### Проверка состояния (self-audit)
```powershell
Start-ArchCompass -Health -Detailed
```

---

## 🏗️ Архитектурные особенности

| Аспект | Реализация | Доказательство |
|--------|-----------|---------------|
| **Модульность** | Динамическая загрузка подмодулей через массив `$modules` | `ArchCompass.psm1`, строки 6–24 |
| **Контракты** | Интерфейсы в `src/core/contracts/` (IModule, IAiProvider) | `Validate-Contract.ps1` + Pester-тесты |
| **Безопасность** | SecretManager + gitleaks + маскирование в логах | `.gitleaks.toml`, `SecurityScanner.psm1` |
| **Наблюдаемость** | Экспорт метрик в Prometheus-формат | `MetricsExporter.psm1`, `EXPOSE 9091` в Dockerfile |
| **Тестируемость** | Pester + PSScriptAnalyzer в CI | `tests/test_archcompass.Tests.ps1`, GitHub Actions |

---

## 🔐 Безопасность (детали)

### Управление секретами
- **SecretManager.psm1**: хранение в зашифрованном виде, поддержка Azure Key Vault / HashiCorp Vault (заглушки)
- **Маскирование**: автоматическое скрытие значений в логах через `StructuredLogger.psm1`
- **Валидация**: проверка на хардкод перед выполнением команд

### Сканирование уязвимостей
```powershell
# Запуск gitleaks с кастомными правилами
Start-ArchCompass -RunSecurityTests

# Локальное сканирование репозитория
gitleaks detect --source . --config .gitleaks.toml --report-path reports/gitleaks.json
```

### Интеграция с CI/CD
Файл `.github/workflows/arch-compass-ci.yml` (если есть) или пример:
```yaml
- name: Run security scan
  run: pwsh -Command "Import-Module ./ArchCompass.psm1; Start-ArchCompass -RunSecurityTests"
```

---

## 🔗 Интеграции в экосистеме

| Компонент | Назначение | Ссылка (относительная) |
|-----------|-----------|------------------------|
| **IT-Compass** | Передаёт маркеры компетенций для аудита использования фреймворка | [`../../apps/it-compass/`](../../apps/it-compass/) |
| **Cloud-Reason** | Получает контекст для валидации архитектурных решений | [`../../apps/cloud-reason/`](../../apps/cloud-reason/) |
| **Portfolio-Organizer** | Принимает отчёты о выполнении команд для генерации доказательств | [`../../apps/portfolio-organizer/`](../../apps/portfolio-organizer/) |
| **Terraform modules** | Деплой инфраструктуры (GCP GKE, Yandex Cloud) | [`../../deployment/terraform/`](../../deployment/terraform/) |

> ⚠️ Пути относительные от `apps/arch-compass-framework/README.md`. На GitHub они кликабельны.

---

## 📊 Статус компонента

| Модуль | Статус | Тесты | Docker | Готовность |
|--------|--------|-------|--------|-----------|
| Core (ConfigurationManager, InputValidator) | ✅ Стабильно | ✅ Pester | ✅ | Production |
| Security (SecretManager, SecurityScanner) | ✅ Стабильно | ✅ Pester + gitleaks | ✅ | Production |
| AI Providers (OpenAI, заглушки Yandex/Local) | 🟡 Рефакторинг под контракты | ⚠️ Частично | ✅ | Beta |
| Diagnostics (HealthCheck, MetricsExporter) | 🟢 Новый, требует документирования | ✅ Базовые | ✅ | Alpha |
| Integrations (CompassAudit) | 🔴 Концепт | ❌ | ❌ | Prototype |

**Общая готовность:** ✅ Контейнеризирован, само-аудит работает, можно демонстрировать.

---

## 🧭 Как использовать в портфолио

### Для работодателя (коротко):
> «Arch-Compass: PowerShell-фреймворк для оркестрации ИИ и инфраструктуры. Контейнеризирован, имеет self-audit, экспортирует метрики в Prometheus. Доказывает, что я проектирую интерфейсы и контракты, а не просто пишу скрипты.»

### Для технического собеседования (детали):
- Покажи `ArchCompass.psm1` → динамическая загрузка модулей
- Покажи `src/core/contracts/` → явные интерфейсы
- Запусти `Start-ArchCompass -Health` → само-аудит в действии
- Открой `Dockerfile` → минималистичный, переносимый образ

### Для грантовой комиссии:
- Ссылка на методологию: [`../../docs/methodology/`](../../docs/methodology/)
- Ссылка на кейс инфраструктурного харденинга: [`../../docs/cases/infra-sync-hardening-2026.md`](../../docs/cases/infra-sync-hardening-2026.md)

---

## 📁 Структура (кратко)

```
arch-compass-framework/
├── ArchCompass.psd1 / psm1   # Манифест и точка входа
├── src/
│   ├── core/                 # ConfigurationManager, InputValidator, contracts/
│   ├── infrastructure/       # SecretManager, SecurityScanner, GitHelper
│   ├── ai/providers/         # IAiProvider + реализации (рефакторинг в процессе)
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