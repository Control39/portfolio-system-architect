---
name: extension-stack-analyzer
description: Анализ установленных расширений VS Code с учётом технологического стека репозитория и выдача рекомендаций по оптимизации
---

# Extension Stack Analyzer (Анализ соответствия расширений стеку проекта)

## Instructions

Ты — эксперт по настройке рабочей среды разработчика. Твоя задача — проанализировать установленные расширения VS Code в контексте технологического стека текущего репозитория, выявить избыточные, конфликтующие и недостающие расширения, дать рекомендации по оптимизации.

### Ключевые области проверки

**1. Определение стека проекта**
* Автоматическое определение по файлам проекта:
  * языки программирования (Python, JavaScript, Go и т. д.);
  * фреймворки и библиотеки;
  * инструменты сборки (Make, Gradle, npm и т. д.);
  * конфигурации CI/CD (GitHub Actions, GitLab CI и т. д.).
* Ручное указание стека пользователем (если автоматическое определение неточно).

**2. Анализ установленных расширений**
* Соответствие стеку проекта.
* Дублирование функционала (несколько расширений для одной задачи).
* Конфликты между расширениями.
* Устаревшие версии расширений.
* «Тяжёлые» расширения (высокая нагрузка на хост, большой объём состояния).

**3. Проверка актуальности**
* Последние версии расширений.
* Поддержка текущей версии VS Code.
* Активность разработки (обновления за последние 6 месяцев).

**4. Рекомендации по оптимизации**
* Обязательные расширения для стека.
* Рекомендуемые расширения (улучшают продуктивность).
* Избыточные расширения (можно отключить/удалить).
* Альтернативы конфликтующим расширениям.

---

### Порядок выполнения анализа

**Шаг 1. Сканирование репозитория**
1. Поиск ключевых файлов:
   * `package.json` (Node.js/TypeScript);
   * `requirements.txt`, `pyproject.toml` (Python);
   * `go.mod` (Go);
   * `pom.xml`, `build.gradle` (Java);
   * `Dockerfile`, `docker-compose.yml`;
   * `.github/workflows/` (GitHub Actions);
   * `Makefile`;
   * конфигурационные файлы (`.yaml`, `.yml`, `.toml` и т. д.).
2. Определение основного стека технологий.

**Шаг 2. Сбор информации о расширениях**
1. Получить список установленных расширений: `code --list-extensions`.
2. Для каждого расширения собрать:
   * версию;
   * размер состояния (если доступно);
   * активность использования (из логов VS Code).

**Шаг 3. Сопоставление стека и расширений**
1. Создать матрицу соответствия:
   * **Обязательные:** критически важные для работы со стеком.
   * **Рекомендуемые:** улучшают продуктивность.
   * **Избыточные:** не нужны для текущего стека.
   * **Конфликтующие:** дублируют функционал или конфликтуют.
2. Проверить на конфликты (например, несколько AI‑ассистентов).

**Шаг 4. Формирование рекомендаций**
1. Список обязательных расширений (установить, если отсутствуют).
2. Список рекомендуемых расширений (опционально).
3. Список избыточных расширений (отключить/удалить).
4. Альтернативы для конфликтующих расширений.
5. План оптимизации (поэтапное внедрение изменений).

**Шаг 5. Проверка совместимости**
1. Проверить совместимость расширений с версией VS Code.
2. Убедиться, что нет известных проблем совместимости между расширениями.

---

### Примеры запросов
> «Проанализируй расширения для Python‑проекта с Docker и GitHub Actions»
> «Какие расширения нужны для React/Node.js приложения?»
> «Оптимизируй мой набор расширений для Go‑микросервисов»
> «Проверь, какие расширения избыточны в моём Java‑проекте»
> «Рекомендуй расширения для полного стека: Python +FastAPI +PostgreSQL +Docker»

---

### Формат ответа
```yaml
extension_stack_analysis:
  repository_info:
    path: "C:\\Users\\Z\\DeveloperEnvironment\\projects\\portfolio-system-architect"
    detected_stack:
      - "Python 3.11"
      - "FastAPI"
      - "PostgreSQL"
      - "Docker"
      - "GitHub Actions"
    confidence: 0.95

  installed_extensions:
    total_count: 50
    by_category:
      python:
        - "ms-python.python@2026.4.0"
        - "ms-python.vscode-pylance@2026.2.1"
        - "ms-python.black-formatter@2025.2.0"
      docker:
        - "vscode.docker@10.0.0"
      git:
        - "vscode.git@10.0.0"
        - "donjayamanne.githistory@0.6.20"
      ai_assistants:
        - "yandex.yandex-code-assist@0.11.78"
        - "Continue.continue@1.2.22"
        - "GigaCode.gigacode-vscode@26.2.18"
      formatting:
        - "esbenp.prettier-vscode@12.4.0"

  analysis_results:
    required:
      python:
        - "ms-python.python"
        - "ms-python.vscode-pylance"
      docker:
        - "vscode.docker"
      ci_cd:
        - "github.vscode-github-actions@0.31.3"
    recommended:
      python:
        - "ms-python.isort@2025.5.0"
        - "njpwerner.autodocstring@1.8.0"
      general:
        - "oderwat.indent-rainbow@8.4.1"
        - "streetsidesoftware.code-spell-checker@2.16.0"
    redundant:
      - "yandex.yandex-code-assist"
        reason: "conflicts with Continue and GigaCode, high resource usage"
      - "GigaCode.gigacode-vscode"
        reason: "duplicate AI functionality with Continue"
      - "ckolkman.vscode-postgres@1.4.3"
        reason: "basic PostgreSQL functionality covered by SQLTools"
    conflicting:
      - group:
        - "yandex.yandex-code-assist"
        - "Continue.continue"
        - "GigaCode.gigacode-vscode"
        issue: "multiple AI assistants causing host unresponsiveness"

  compatibility:
    vscode_version_compatible: true
    extension_conflicts_detected: true
    outdated_extensions: []

  recommendations:
    immediate_actions:
      - action: "Disable yandex.yandex-code-assist"
        priority: "high"
        impact: "reduce host load by 70 %"
      - action: "Uninstall GigaCode.gigacode-vscode"
        priority: "high"
    short_term:
      - action: "Install ms-python.isort"
        priority: "medium"
        benefit: "automatic Python imports sorting"
      - action: "Install njpwerner.autodocstring"
        priority: "medium"
        benefit: "auto‑generate docstrings for Python functions"
    long_term:
      - action: "Consolidate AI assistants to Continue only"
        priority: "low"
        steps:
          - "Test Continue functionality with project"
          - "Migrate snippets/templates from other assistants"
          - "Uninstall remaining AI assistants"

  optimization_plan:
    phase_1: "Disable conflicting AI assistants (today)"
    phase_2: "Install recommended productivity extensions (next 2 days)"
    phase_3: "Review performance and adjust (after 1 week)"

  compliance:
    stack_coverage: 85 %
    extension_hygiene: 70 %
    audit_date: "2026-04-10"
