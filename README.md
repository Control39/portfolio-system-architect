# 🧠 Cognitive Architecture: Systems for Thinking

> **Это не портфолио. Это архитектурное доказательство трансформации: от нуля в IT до production-grade экосистемы за 2 года.**

*Compositional Architecture в действии. Построено в коллаборации с ИИ-агентами.*  
**Быстрые цифры:** 18 сервисов • 610+ тестов • 0 уязвимостей • 2 года от нуля до production.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Services](https://img.shields.io/badge/Services-18-green?style=flat-square&logo=serverless)
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

## 🎯 Что это такое и почему это уникально

Это **не коллекция микросервисов**. Это **композиционная архитектура** на принципе **«Атомов и Молекул»**: переиспользуемые компоненты в `src/shared/`, `src/core/`, `src/security/` — **Атомы** — собираются в независимые сервисы `apps/` — **Молекулы** — каждая под свою задачу. Они общаются через **слабую связанность (Loose Coupling)**, не зная внутреннего устройства друг друга. Сервис может выглядеть минималистичным, потому что вся сложная логика живёт в Атомах. Это **фича**, а не баг.

**Кто я в IT?** Этот вопрос не давал мне покоя, пока я не создала **IT-Compass** — методологию объективных маркеров компетенций (83 маркера в 19 доменах), которая превращает субъективный опыт в измеримые данные. Но методология без практики — это просто таблица. Поэтому каждый сервис в этой экосистеме — это ответ на конкретную проблему, с которой я столкнулась на пути к ответу:

- `job-automation-agent` → «Как искать работу без опыта?»
- `thought-architecture` → «Как я вообще мыслю?»
- `career-development` → «Куда расти дальше?»
- `portfolio-organizer` → «Как доказать, что я умею, не просто сказав об этом?»

**Что это доказывает работодателю:** не заявления о навыках, а **система доказательств**:
- 🔒 **0 критических уязвимостей** (Trivy + Bandit + CodeQL)
- 🧪 **85%+ покрытие тестами** (610+ тестов, 98% проходят)
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

## 🏗️ Обзор архитектуры

### Ключевые принципы

| Принцип | Реализация | Бизнес-ценность |
|---------|------------|----------------|
| **Слабая связанность (Loose Coupling)** | Сервисы общаются через API/конфиги, а не прямые импорты | Изменения в одном сервисе не ломают другие; быстрее итерации |
| **Атомы → Молекулы** | Переиспользуемые компоненты (`src/shared/`) собираются в сервисы (`apps/*`) | Ускоренная разработка, консистентное качество, проще онбординг |
| **Документация как код** | ADR, runbooks, самодокументирующиеся сервисы | 0 расхождений между кодом и доками |
| **Безопасность по умолчанию** | Trivy, Bandit, CodeQL в CI/CD | 0 критических уязвимостей |
| **ИИ как соисполнитель** | MCP, RAG-пайплайны, промпт-инжиниринг | 15+ сервисов построено в коллаборации с ИИ |

### Основные компоненты (18 сервисов)

Все сервисы соответствуют **100% стандарту структуры** (main.py, README.md, Dockerfile, tests/).

| Сервис | Статус | Покрытие | Описание |
|--------|--------|----------|----------|
| **client/** | 🟢 Active | ~85% | **Frontend** (React 19 + TS) для чата с ИИ |
| **ai-config-manager** | 🟢 Core | ~90% | Централизованный менеджер конфигурации |
| **auth-service** | 🟢 Ready | ~95% | JWT-аутентификация |
| **career-development** | 🟢 Ready | 80.47% | Трекинг компетенций |
| **cognitive-agent** | 🟢 Core | ~85% | Автономный ИИ-агент |
| **decision-engine** | 🟢 Ready | ~85% | AI reasoning с RAG |
| **infra-orchestrator** | 🟢 Ready | ~75% | Оркестрация сервисов (Python/FastAPI) |
| **it-compass** | 🟢 Ready | ~85% | Методология IT-компетенций |
| **job-automation-agent** | 🟢 Ready | ~80% | Автоматизация поиска работы |
| **knowledge-graph** | 🟢 Ready | ~75% | Граф знаний (сущности/отношения) |
| **mcp-server** | 🟡 WIP | 46.68% | MCP-сервер для ИИ-агентов |
| **ml-model-registry** | 🟢 Ready | ~90% | Регистр ML-моделей |
| **portfolio-organizer** | 🟢 Ready | 92.24% | Сбор доказательств |
| **system-proof** | 🟢 Ready | ~75% | Валидация готовности |
| **thought-architecture** | 🟢 Ready | ~75% | Архитектура решений (ADR) |

> **🎉 18/18 сервисов (100%) соответствуют стандарту структуры!**  
> **🎉 11 из 15 сервисов имеют ≥80% покрытие тестами!**  
> **Всего тестов:** 610+ (98% прохождение, ~85% среднее покрытие).

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
cat docs/ARCHITECTURE.md

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
| ADR‑002 | [Интеграция компонентов в единую экосистему](docs/architecture/decisions/ADR-002-component-integration.md) |
| ADR‑003 | [Архитектура системы версионирования ML-моделей](docs/architecture/decisions/ADR-003-ml-model-versioning-system.md) |
| ADR‑007 | [Обоснование технологического стека](docs/architecture/decisions/ADR-007-technology-stack-justification.md) |
| ADR‑015 | [Граница между `src/` и `apps/`](docs/architecture/decisions/ADR-015-monorepo-boundary.md) |
| ADR‑016 | [Стандартизация документации](docs/architecture/decisions/ADR-016-standardize-documentation.md) |
| ADR‑017 | [Покрытие MCP Server](docs/architecture/decisions/ADR-017-mcp-server-coverage-decision.md) |

> **Зачем ADR?** Фиксирую **почему выбрано X, а не Y**. История решений для себя и команды.

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

* **Роль:** System Architect
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
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Технические специалисты | Детальная архитектура |

### Для HR и работодателей

| Документ | Для кого | Описание |
|----------|----------|----------|
| [`HIRING_BRIEF.md`](docs/HIRING_BRIEF.md) | HR, нанимающие менеджеры | Детали для найма |
| [`SOURCECRAFT_GRANT_APPLICATION.md`](docs/SOURCECRAFT_GRANT_APPLICATION.md) | Грантовые комитеты | Заявка на грант |
| [`FOR-EMPLOYER.md`](docs/FOR-EMPLOYER.md) | Работодатели | Презентация проекта |
| [`INTERVIEW-QA.md`](docs/INTERVIEW_QA.md) | Интервьюеры | Ответы на вопросы |

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

</div>

---

*Лицензия: Код — MIT, Методология — CC BY-ND 4.0 (© Екатерина Куделя)*  
*Production-ready, соответствует 152-ФЗ, использует российские ИИ-решения (GigaChat, Yandex GPT).*

*Последнее обновление: май 2026*
