# 🧠 Cognitive Architecture: Systems for Thinking

> **Это не портфолио. Это архитектурное доказательство трансформации: от нуля в IT до production-grade экосистемы за 2 года.**

*Compositional Architecture в действии. Построено в коллаборации с ИИ-агентами.*
**Быстрые цифры:** 16 микросервисов • 779+ тестов • 0 уязвимостей • 2 года от нуля до production.

> **📖 Документация читается напрямую из Markdown-файлов на GitHub.** Это честнее, чем показывать устаревшие страницы MkDocs.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Services](https://img.shields.io/badge/Services-16-green?style=flat-square&logo=serverless)
![Test Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen?style=flat-square&logo=pytest)
![Vulnerabilities](https://img.shields.io/badge/Vulnerabilities-0-success?style=flat-square&logo=security)
![Last Updated](https://img.shields.io/github/last-commit/Control39/portfolio-system-architect/main?label=Last%20Updated&style=flat-square)
![CI/CD](https://img.shields.io/github/actions/workflow/status/Control39/portfolio-system-architect/ci.yml?logo=github-actions&label=CI%2FCD)
![License](https://img.shields.io/github/license/Control39/portfolio-system-architect?color=blue&logo=mit)

**Катя (Control39) — Cognitive Architect**
*Превращаю хаос в систему, рутину в автоматизацию, идеи в продукты*

[GitHub](https://github.com/Control39) · [Email](mailto:leadarchitect@yandex.ru) · [Issues](https://github.com/Control39/portfolio-system-architect/issues)

</div>

---

## 🎯 Architect, Not Coder

| Что я делаю | Что я не делаю | Почему это важно |
|-------------|----------------|----------------|
| Проектирую системы мышления, которые учатся и адаптируются | Не пишу код ради заранее определённых задач | Создаю масштабируемые, самообучающиеся архитектуры |
| Оркестрирую ИИ-агентов для реализации моих дизайнов | Не кодирую вручную каждую строку | Использую ИИ как слой исполнения, сохраняя архитектурный контроль |
| Определяю контракты и границы между компонентами | Не создаю монолитный, сильно связанный код | Позволяю компонентам эволюционировать независимо |
| Валидирую результаты против архитектурных принципов | Не принимаю сгенерированный ИИ код без проверки | Обеспечиваю качество, безопасность и соответствие стандартам |
| Интегрирую 16 микросервисов в единую экосистему | Не работаю с изолированными инструментами | Демонстрирую end-to-end системное мышление |

> **AI — это слой исполнения. Архитектура, валидация и ответственность — мои.**

---

## 🧭 Навигация по аудитории

| Вы | Читайте | Что внутри |
|----|---------|-----------|
| 🎯 **HR / Нанимающий менеджер** | [`docs/HIRING_BRIEF.md`](docs/HIRING_BRIEF.md) | Бизнес-ценность, доказательства компетенций, вопросы для интервью |
| 💻 **Техлид / Архитектор** | [`docs/architecture/decisions/`](docs/architecture/decisions/) | ADR, стандарты валидации, паттерны интеграции, ядро системы |
| 🛠️ **DevOps / SRE** | [`deployment/`](deployment/) + [`monitoring/`](monitoring/) | GitOps, K8s манифесты, sealed secrets, CI/CD пайплайны |
| 🏆 **Грантовые комитеты** | [`docs/SOURCECRAFT_GRANT_APPLICATION.md`](docs/SOURCECRAFT_GRANT_APPLICATION.md) | Доказательства влияния, масштабируемость, социальная ценность |
| 🌱 **Начинающие / Менторы** | [`apps/it-compass/`](apps/it-compass/) | Методология самооценки, трекинг роста, реальные кейсы |

---

## 🎯 Что это такое и почему это уникально

Это **не коллекция микросервисов**. Это **композиционная архитектура** на принципе **«Атомов и Молекул»**: переиспользуемые компоненты в `src/shared/`, `src/core/`, `src/security/` — **Атомы** — собираются в независимые сервисы `apps/` — **Молекулы** — каждая под свою задачу. Они общаются через **слабую связанность (Loose Coupling)**, не зная внутреннего устройства друг друга. Сервис может выглядеть минималистичным, потому что вся сложная логика живёт в Атомах. Это **фича**, а не баг.

**Кто я в IT?** Этот вопрос не давал мне покоя, пока я не создала **IT-Compass** — методологию объективных маркеров компетенций (83 маркера в 19 доменах), которая превращает субъективный опыт в измеримые данные. Но методология без практики — это просто таблица. Поэтому каждый сервис в этой экосистеме — это ответ на конкретную проблему, с которой я столкнулась на пути к ответу:

- `job-automation-agent` → «Как искать работу без опыта?»
- `thought-architecture` → «Как я вообще мыслю?»
- `career-development` → «Куда расти дальше?»
- `portfolio-organizer` → «Как доказать, что я умею, не просто сказав об этом?»

**Что это доказывает работодателю:** не заявления о навыках, а **система доказательств**:
- 🔒 **0 критических уязвимостей** (Trivy + Bandit + CodeQL)
- 🧪 **~85% покрытие тестами** (779+ тестов, 98% проходят)
- 🔄 **Полный CI/CD** + pre-commit hooks
- 📊 **Production monitoring** (Prometheus + Grafana)
- 🚀 **Kubernetes-ready** деплой (52 манифеста, GitOps)

Каждый компонент этой системы — одновременно работающий код и **объективный маркер компетенции**: проверяемый артефакт владения конкретной областью, от DevSecOps до проектирования распределённых систем. Это подтверждение уровня мышления **Senior/Architect**, зафиксированное не в резюме, а в репозитории.

---

## 💡 Инновация: Объективные маркеры компетенций

**Традиционный подход:**
> «Расскажите о вашем опыте с Docker»
> *Ответ: «Я знаю Docker»*

**Мой подход:**
> «Покажите, что вы реально сделали»
> *Ответ: «Создала Dockerfile для Python-приложения, отладила сеть в docker-compose, задеплоила на staging»*

**Это маркер.** Объективный, проверяемый, не требует лет опыта.

📖 Методология: [`docs/it-compass/METHODOLOGY.md`](docs/it-compass/METHODOLOGY.md)

---

## 🔄 Мой рабочий процесс: ИИ как слой исполнения

```mermaid
graph LR
    A[Архитектура и ограничения] --> B[Оркестрация ИИ]
    B --> C[Валидация и рефакторинг]
    C --> D[Интеграция и деплой]
    D --> E[Доказательства и аудит]

    style A fill:#1a73e8,stroke:#333,color:#fff
    style E fill:#0d47a1,stroke:#333,color:#fff
```

1. **Архитектура и ограничения** → Я определяю границы, контракты, метрики успеха и режимы отказа.
2. **Оркестрация ИИ** → Модели генерируют черновики реализации на основе моих спецификаций.
3. **Валидация и рефакторинг** → Я проверяю, отклоняю ошибочные подходы, исправляю краевые случаи и обеспечиваю стандарты.
4. **Интеграция и деплой** → Я связываю компоненты, настраиваю инфраструктуру, устанавливаю CI/CD и мониторинг.
5. **Доказательства и аудит** → Автоматически собираются через `portfolio-organizer`, проверяются через `repo-audit`.

---

## 🏗️ Обзор архитектуры

### Ключевые принципы

| Принцип | Реализация | Бизнес-ценность |
|---------|------------|----------------|
| **Слабая связанность (Loose Coupling)** | Сервисы общаются через API/конфиги, а не прямые импорты | Изменения в одном сервисе не ломают другие; быстрее итерации |
| **Атомы → Молекулы** | Переиспользуемые компоненты (`src/shared/`) собираются в сервисы (`apps/*`) | Ускоренная разработка, консистентное качество, проще онбординг |
| **Документация как код** | ADR, runbooks, самодокументирующиеся сервисы | 0 расхождений между кодом и доками |
| **Безопасность по умолчанию** | Trivy, Bandit, CodeQL в CI/CD | 0 критических уязвимостей |
| **ИИ как соисполнитель** | MCP, RAG-пайплайны, промпт-инжиниринг | 16+ сервисов построено в коллаборации с ИИ |

### Основные компоненты (16 микросервисов + frontend)

Все сервисы соответствуют **100% стандарту структуры** (main.py, README.md, Dockerfile, tests/).

| Сервис | Статус | Покрытие | Описание |
|--------|--------|----------|----------|
| **client/** | 🟢 Active | ~85% | **Frontend** (React 19 + TS) для чата с ИИ |
| **ai_config_manager** | 🟢 Core | ~90% | Централизованный менеджер конфигурации |
| **auth_service** | 🟢 Ready | ~95% | JWT-аутентификация |
| **career_development** | 🟢 Ready | 80.47% | Трекинг компетенций |
| **chat_backend** | 🟢 Ready | ~78% | WebSocket-сервер для чата |
| **cognitive_agent** | 🟢 Core | ~85% | Автономный ИИ-агент |
| **decision_engine** | 🟢 Ready | ~85% | AI reasoning с RAG |
| **infra_orchestrator** | 🟢 Ready | ~75% | Оркестрация сервисов (FastAPI) |
| **it_compass** | 🟢 Ready | ~85% | Методология IT-компетенций |
| **job_automation_agent** | 🟢 Ready | ~80% | Автоматизация поиска работы |
| **knowledge_graph** | 🟢 Ready | ~75% | Граф знаний (сущности/отношения) |
| **mcp_server** | 🟡 WIP | 46.68% | MCP-сервер для ИИ-агентов |
| **ml_model_registry** | 🟢 Ready | ~90% | Регистр ML-моделей |
| **portfolio_organizer** | 🟢 Ready | 92.24% | Сбор доказательств |
| **system_proof** | 🟢 Ready | ~75% | Валидация готовности |
| **template_service** | 🟡 WIP | ~60% | Генератор шаблонов и паттернов |
| **thought_architecture** | 🟢 Ready | ~75% | Архитектура решений (ADR) |

> **🎉 16/16 микросервисов (100%) соответствуют стандарту структуры!**
> **🎉 14 из 16 сервисов имеют ≥75% покрытие тестами!**
> **Всего тестов:** 779+ (98% прохождение, ~85% среднее покрытие).

---

## 🛠️ Инструменты разработки

| Инструмент | Назначение | Документация |
|------------|------------|--------------|
| **Koda** | Интеграция с IDE, анализ кода | [docs/TOOLS.md](docs/TOOLS.md) |
| **SourceCraft** | ИИ-агенты для автоматизации (17 скиллов) | [docs/TOOLS.md](docs/TOOLS.md) |
| **Continue** | AI pair programming (VS Code) | [docs/TOOLS.md](docs/TOOLS.md) |
| **MCP Server** | Оркестрация агентов, CI/CD | [docs/TOOLS.md](docs/TOOLS.md) |

**Новые инструменты:**
* **Генератор сервисов** — создание нового сервиса за 2 сек: `python scripts/create_service.py my-service --description="..."`
* **Проверка структуры** — авто-валидация: `python scripts/check_service_structure.py`
* **CI/CD проверки** — блокировка плохих PR в GitHub Actions

📖 Документация: [`docs/TOOLS.md`](docs/TOOLS.md), [`docs/SERVICE_GENERATOR.md`](docs/SERVICE_GENERATOR.md)

---

## 🚀 Быстрый старт

### Для новых разработчиков (5 мин)
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect

# 2. Настройте окружение IDE
# Копируйте шаблон настроек (опционально):
cp .vscode/settings-default.json .vscode/settings.json

# 3. Запустите Frontend + Backend
python apps/chat_backend/start_dev.py
# Или вручную:
# Терминал 1: cd client && npm run dev          # http://localhost:5173
# Терминал 2: cd apps/chat_backend && python app.py  # http://localhost:8005
```

### Настройка IDE (VS Code)

**Общие настройки** (в git, обязательны для всех):
* Форматирование: Black (Python), Prettier (JS/TS)
* Линтинг: Ruff, mypy
* Тестирование: pytest с покрытием
* PowerShell как терминал по умолчанию

**Личные настройки** (игнорируются в git):
* ИИ-ассистенты (Koda, Copilot, GigaCode)
* Тема, шрифты, цвета
* Горячие клавиши

**Шаблон:** `.vscode/settings-default.json`
**Личное:** `.vscode/settings.json` (не коммитить)

**Расширения:**
```bash
# Рекомендуемые (установите вручную или через extensions.json)
- ms-python.python
- ms-python.black-formatter
- ms-python.vscode-pylance
- redhat.vscode-yaml
- esbenp.prettier-vscode
```

---

### Для исследователей методологии (10 мин)
```bash
# Прочитайте методологию
cat docs/it-compass/METHODOLOGY.md

# Изучите архитектуру
cat ARCHITECTURE.md

# Посмотрите доказательства
cat docs/it-compass/PROJECT_ANALYSIS.md
```

### Доступ к сервисам

| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend (Chat UI)** | http://localhost:5173 | React-приложение с чатом ИИ |
| **Backend API** | http://localhost:5000/docs | Swagger UI для REST API |
| **Auth Service** | http://localhost:8100/docs | JWT-аутентификация |
| **IT-Compass UI** | http://localhost:8501 | Трекинг компетенций (Streamlit) |
| **Grafana** | http://localhost:3000 | Мониторинг (admin/admin) |

---

## 📜 Архитектурные решения (ADR)

| ADR | Описание |
|-----|----------|
| ADR‑001 | [Методология системного мышления](docs/architecture/decisions/ADR-001-system-thinking-methodology.md) |
| ADR‑002 | [Выбор технологического стека](docs/architecture/decisions/ADR-002-consolidated.md) |
| ADR‑003 | [Интеграция компонентов в единую экосистему](docs/architecture/decisions/ADR-003-component-integration.md) |
| ADR‑004 | [Формат диаграмм (Mermaid)](docs/architecture/decisions/ADR-004-diagram-format.md) |
| ADR‑005 | [Архитектура системы версионирования ML-моделей](docs/architecture/decisions/ADR-005-ml-model-versioning-system.md) |
| ADR‑006 | [Формат хранения маркеров компетенций](docs/architecture/decisions/ADR-006-data-storage-format.md) |
| ADR‑007 | [Выбор UI-технологии](docs/architecture/decisions/ADR-007-ui-technology-choice.md) |
| ADR‑008 | [Валидация данных](docs/architecture/decisions/ADR-008-data-validation-approach.md) |
| ADR‑009 | [Обоснование технологического стека](docs/architecture/decisions/ADR-009-technology-stack-justification.md) |
| ADR‑010 | [Service Discovery](docs/architecture/decisions/ADR-010-service-discovery.md) |
| ADR‑011 | [Базовые Docker-образы](docs/architecture/decisions/ADR-011-base-docker-images.md) |
| ADR‑012 | [Разделение настроек IDE](docs/architecture/decisions/ADR-012-vscode-settings-separation.md) |
| ADR‑014 | [Граница между `src/` и `apps/`](docs/architecture/decisions/ADR-014-monorepo-boundary.md) |
| ADR‑015 | [Стандартизация документации](docs/architecture/decisions/ADR-015-standardize-documentation.md) |
| ADR‑016 | [Покрытие MCP Server](docs/architecture/decisions/ADR-016-mcp-server-coverage-decision.md) |
| ADR‑017 | [Dependency Injection](docs/architecture/decisions/ADR-017-dependency-injection.md) |
| ADR‑018 | [Документация и аудит](docs/architecture/decisions/ADR-018-documentation-and-audit-standards.md) |
| ADR‑019 | [Local vs Cloud LLM](docs/architecture/decisions/ADR-019-local-vs-cloud-llm.md) |

> **Зачем ADR?** Фиксирую **почему выбрано X, а не Y**. История решений для себя и команды.

---

## 🧭 Гид для интервьюера

Этот репозиторий объёмный. Вот куда смотреть, чтобы оценить мои навыки:

| Что проверить | Где искать | Что это доказывает |
|---------------|------------|-------------------|
| **Архитектурное мышление** | [`docs/architecture/decisions/`](docs/architecture/decisions/) | Умение обосновывать выбор технологий |
| **Качество кода** | [`apps/auth_service/tests/`](apps/auth_service/tests/) | Покрытие тестами, обработка ошибок |
| **Безопасность** | [`src/security/`](src/security/) + [`.github/workflows/security.yml`](.github/workflows/security.yml) | Защита от уязвимостей, маскирование секретов |
| **DevOps** | [`docker-compose.yml`](docker-compose.yml) + [`deployment/k8s/`](deployment/k8s/) | Оркестрация, масштабирование |
| **Методология** | [`docs/it-compass/METHODOLOGY.md`](docs/it-compass/METHODOLOGY.md) | Системный подход к компетенциям |

---

## 🛣️ Roadmap (Что дальше?)

Система живая. Текущие приоритеты:

1. **Завершение MCP Server** — перевод из WIP в Stable для полноценной оркестрации агентов
2. **Нагрузочное тестирование** — бенчмарки для `decision-engine` и `knowledge-graph`
3. **Расширение CI/CD** — автоматический деплой в staging при мерже в `develop`
4. **Публичные кейсы внедрения** — гипотетические сценарии для компаний (Sber, Yandex и т.д.)

---

## 🎯 Для кого этот проект

### 👔 Для HR и нанимающих менеджеров

**Роли для найма:**
* **AI Systems Architect** — проектирование интеграции ИИ-компонентов
* **Technical Product Manager** — мост между продуктом и возможностями ИИ
* **Solutions Architect** — интеграция ИИ в legacy-системы
* **Knowledge Architect** — превращение хаоса в поисковую интеллектуальную систему

### 💼 Для российского корпоративного сектора

Компании вроде **Yandex, Sberbank, Tinkoff, VTB, Krok, IBS, Lanit** сталкиваются с теми же проблемами:
* Legacy-системы без документации
* Интеграция ИИ без архитектурной строгости
* Знания заперты в головах сотрудников
* Найм на роли, которых официально ещё нет

Эта система решает их все:
* **Knowledge capture** — превращает Slack, заметки и разговоры в поисковую интеллектуальную систему
* **AI orchestration** — интеграция с Yandex Cloud, Yandex GPT
* **Compliance** — аудит-трейлы, логирование решений, управление
* **Modernization** — как постепенно превращать хаос в систему

### 🏆 Для грантовых комитетов (SourceCraft Open Source)

**Почему это подходит:**
* ✅ **Новая методология** — «Objective Competency Markers» не существует больше нигде
* ✅ **Полностью документировано** — методология, архитектура, код, примеры
* ✅ **Ценность для сообщества** — любая организация может адаптировать этот паттерн
* ✅ **Работающая система** — не теория, а живой пример
* ✅ **Открытая лицензия** — CC BY-ND 4.0 для методологии, MIT для кода

📄 Детали гранта: [`docs/SOURCECRAFT_GRANT_APPLICATION.md`](docs/SOURCECRAFT_GRANT_APPLICATION.md)

---

## 🎯 Что я ищу

* **Роль:** System Architect, Senior Backend Engineer, DevSecOps Lead
* **Тип задач:** Сложные распределённые системы, микросервисы, автоматизация
* **Ценности:** Системное мышление, документация, автоматизация рутины, ИИ-усиление

**Готова обсудить:**
* Как автоматизация экономит 60% времени разработки
* Как ИИ помогает принимать архитектурные решения (не заменяет)
* Как создавать окружение, где код работает сам

---

## 🤝 Let's Connect

* 📧 **Email:** [leadarchitect@yandex.ru](mailto:leadarchitect@yandex.ru)
* 🐙 **GitHub Issues:** [Обсуждения и вопросы](https://github.com/Control39/portfolio-system-architect/issues)

---

## 📚 Дополнительная документация

### Основные руководства

| Документ | Для кого | Описание |
|----------|----------|----------|
| [`docs/TOOLS.md`](docs/TOOLS.md) | Все | Обзор инструментов (Koda, SourceCraft, Continue, MCP) |
| [`docs/SERVICE_GENERATOR.md`](docs/SERVICE_GENERATOR.md) | Разработчики | Как создавать новые сервисы за 2 сек |
| [`docs/SERVICE_STRUCTURE_STANDARD.md`](docs/SERVICE_STRUCTURE_STANDARD.md) | Разработчики | Стандарт структуры сервиса (100% соответствие) |
| [`docs/CI_CD_SERVICE_STRUCTURE.md`](docs/CI_CD_SERVICE_STRUCTURE.md) | DevOps | Настройка CI/CD |
| [`ops/RUNBOOK.md`](ops/RUNBOOK.md) | Ops | Руководство по операциям и инцидентам |

### Методология и архитектура

| Документ | Для кого | Описание |
|----------|----------|----------|
| [`docs/it-compass/METHODOLOGY.md`](docs/it-compass/METHODOLOGY.md) | Все | Методология объективных маркеров компетенций |
| [`docs/TOOLS_INTEGRATION.md`](docs/TOOLS_INTEGRATION.md) | Архитекторы | Как инструменты работают вместе |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Технические специалисты | Детальная архитектура |

### Для HR и работодателей

| Документ | Для кого | Описание |
|----------|----------|----------|
| [`HIRING_BRIEF.md`](docs/HIRING_BRIEF.md) | HR, нанимающие менеджеры | Детали для найма |
| [`SOURCECRAFT_GRANT_APPLICATION.md`](docs/SOURCECRAFT_GRANT_APPLICATION.md) | Грантовые комитеты | Заявка на грант |
| [`FOR-EMPLOYER.md`](docs/FOR-EMPLOYER.md) | Работодатели | Презентация проекта |
| [`INTERVIEW-QA.md`](docs/INTERVIEW-QA.md) | Интервьюеры | Ответы на вопросы |

---

<!-- GitHub Stats -->
<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=Control39&show_icons=true&theme=tokyonight&hide_border=true" alt="Stats" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Control39&layout=compact&theme=tokyonight&hide_border=true" alt="Languages" />
</p>

<p align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=Control39&theme=tokyonight&hide_border=true" alt="Streak" />
</p>

---

<div align="center">

**Cognitive Architect × AI-Augmented Developer × DevSecOps Enthusiast**
*Это не портфолио. Это доказательство того, что хаос может стать системой, а мышление — измеримым.*

_Последнее обновление: май 2026_

</div>

---

*Лицензия: Код — MIT, Методология — CC BY-ND 4.0 (© Екатерина Куделя)*
*Production-ready, соответствует 152-ФЗ, использует российские ИИ-решения (GigaChat, Yandex GPT).*
