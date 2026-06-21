# Расширенные функции Cognitive Agent

## 1. AI Provider Manager и выбор моделей

Cognitive Agent использует sophisticated систему выбора AI-провайдера, основанную на конфигурации и условиях:

- **Стратегия выбора**: Агент автоматически выбирает модель в зависимости от типа задачи:
  - `gigachat-lite` для повседневных задач (кодирование, рефакторинг, тестирование)
  - `gigachat-pro` для сложных архитектурных задач
  - `ollama-qwen2.5-coder` для офлайн-режима или быстрых правок

- **Fallback-цепочка**: Агент использует цепочку fallback-моделей при недоступности основной:
  - Если GigaChat недоступен → переключается на Ollama
  - Если задача сложная → использует GigaChat Pro/Max
  - Если все модели недоступны → использует YandexGPT

- **Настройки таймаутов**: Каждая модель имеет свои таймауты и лимиты повторных попыток

## 2. Система безопасности (Guardrails)

Система безопасности включает несколько уровней:

- **Input Sanitization**: Блокировка опасных паттернов (например, `rm -rf`, `eval()`, `os.system()`)
- **Контекстно-зависимые проверки**: Автоматическое одобрение для багфиксов, рефакторинга и новых фич
- **Enterprise Guardrails**: RBAC-модель с ролями (admin, developer, auditor) и разграничением прав
- **Проверка важных файлов**: Требует подтверждения для модификации конфигурационных файлов
- **Гибкие настройки**: Правила можно настраивать через YAML-конфигурации

Базовая функциональность безопасности реализована в [BaseSecurityChecker](file:///c:/repo/agents/cognitive_agent/common/base_security.py), что позволяет использовать общие проверки в обеих версиях агента.

## 3. Система логирования

Агент использует структурированное логирование с использованием `structlog`:

- **JSON-формат**: Все логи сохраняются в JSON-формате для удобства анализа
- **Контекстная информация**: Каждая запись содержит контекст выполнения задачи
- **Аудит-логирование**: Все действия агента фиксируются в отдельном аудит-логе
- **Пример лога**: При выполнении задачи генерируется запись с информацией о задаче, типе, проекте и контексте

Базовая функциональность логирования реализована в [BaseLogger](file:///c:/repo/agents/cognitive_agent/common/base_logger.py), что позволяет использовать общие подходы к логированию в обеих версиях агента.

## 4. Интеграция с ChromaDB

Агент использует ChromaDB для RAG (Retrieval-Augmented Generation):

- **Индексация документов**: Сканирует и индексирует текстовые файлы проекта
- **Семантический поиск**: Позволяет находить релевантные фрагменты кода по запросу
- **Контекст для AI**: Использует найденные документы для улучшения качества ответов
- **Метаданные**: Сохраняет информацию о пути файла, расширении, размере и дате модификации

## Система безопасности (Guardrails)

### Примеры правил безопасности

Агент использует многоуровневую систему безопасности:

#### 1. Input Sanitization (guardrails-enterprise.yaml)
```yaml
input_sanitization:
  enabled: true
  patterns:
    - pattern: "rm\\s+-rf"
      severity: "critical"
      action: "block"
      reason: "Potential destructive command"

    - pattern: "(eval|exec|compile)\\s*\\("
      severity: "high"
      action: "block"
      reason: "Code execution function"

    - pattern: "(os\\.system|subprocess\\.)"
      severity: "high"
      action: "block"
      reason: "System command execution"
```

#### 2. Контекстно-зависимая проверка
```python
def _check_guardrail(self, action: str, path: str, context: dict = None) -> bool:
    # Если это исправление бага — разрешаем автоматически
    if context and context.get("type") in ["bugfix", "hotfix", "typo"]:
        logger.info(f"✅ Auto-approve bugfix: {action} → {path}")
        return True

    # Если это рефакторинг — разрешаем (но логируем)
    if context and context.get("type") in ["refactor", "optimize", "cleanup"]:
        logger.info(f"✅ Auto-approve refactor: {action} → {path}")
        self._log_action("refactor_auto_approved", {"path": path, "action": action})
        return True

    # Если это добавление фичи — разрешаем (но логируем)
    if context and context.get("type") == "feature":
        logger.info(f"✅ Auto-approve feature: {action} → {path}")
        self._log_action("feature_auto_approved", {"path": path, "action": action})
        return True

    # Проверяем важные файлы
    important_files = ["config.yaml", "settings.py", "requirements.txt", "Dockerfile", "docker-compose.yml"]
    if any(important in path for important in important_files):
        if action.lower() in ["modify", "write", "delete"]:
            logger.info(f"⚠️ Important file requires approval: {path}")
            return False  # Требует подтверждения
```

#### 3. Enterprise Guardrails с RBAC
```yaml
roles:
  admin:
    permissions:
      - "execute_any_code"
      - "modify_system_files"
      - "access_secrets"
      - "bypass_guardrails"

  developer:
    permissions:
      - "read_code"
      - "write_application_code"
      - "run_tests"
      - "modify_docs"
    restrictions:
      - "no_access_to_secrets"
      - "no_system_file_modification"
```

### Гибкость настройки

Правила безопасности можно настраивать через:
- [config/guardrails.yaml](file:///c:/repo/agents/cognitive_agent/config/guardrails.yaml) - базовые правила
- [config/guardrails-enterprise.yaml](file:///c:/repo/agents/cognitive_agent/config/guardrails-enterprise.yaml) - enterprise правила
- Runtime API для динамического изменения правил

## Система логирования

### Структурированное логирование через structlog

Агент использует структурированное логирование для удобства анализа:

```python
# Глобальная конфигурация structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)
```

### Пример лога при выполнении задачи

```json
{
  "timestamp": "2026-06-19T03:04:35.123456",
  "level": "info",
  "event": "Task received",
  "task": "Fix authentication bug",
  "agent_id": "agent-20260619-030435",
  "project_path": "c:/repo",
  "context": {
    "type": "bugfix",
    "complexity": "medium",
    "auto_approve": false
  }
}
```

### Аудит-логирование

Агент поддерживает полное аудит-логирование всех действий:

```python
class AuditLogger:
    def log_action(self, action: str, details: dict, status: str = "success"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "details": details,
            "status": status,
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

Пример записи в аудит-логе:
```json
{
  "timestamp": "2026-06-19T03:05:12.789012",
  "agent_id": "agent-20260619-030435",
  "action": "file_access_attempt",
  "details": {
    "path": "src/auth.py",
    "action": "modify",
    "user_role": "developer"
  },
  "status": "approved"
}
```

## Интеграция с ChromaDB

### Как агент использует векторный поиск

Агент использует ChromaDB для RAG (Retrieval-Augmented Generation):

#### 1. Индексация документов
```python
def index_project_documents(self, force: bool = False) -> dict[str, Any]:
    """
    Индексировать документы проекта в ChromaDB для семантического поиска.
    """
    # Собираем документы для индексации
    for file_path in self.project_path.rglob("*"):
        if file_path.is_file() and not self._is_excluded(file_path):
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            documents.append(content)
            metadatas.append({
                "path": str(file_path.relative_to(self.project_path)),
                "extension": file_path.suffix,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            })
```

#### 2. Поиск похожих документов
```python
def search_similar_documents(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """
    Поиск семантически похожих документов через ChromaDB.
    """
    results = self.chroma_indexer.query(query, top_k=top_k)

    formatted_results = []
    for i, (doc, metadata, distance) in enumerate(
        zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0],
            strict=False,
        )
    ):
        formatted_results.append({
            "rank": i + 1,
            "score": 1 - distance,  # Конвертируем расстояние в релевантность (0-1)
            "path": metadata.get("path", "unknown"),
            "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
            "metadata": metadata,
        })
```

### Для чего агент накапливает данные в ChromaDB

1. **Контекст для AI**: При выполнении задач агент извлекает релевантные фрагменты кода
2. **Поиск по проекту**: Быстрый семантический поиск по всему проекту
3. **Понимание архитектуры**: Анализ связей между компонентами проекта
4. **Документирование**: Поиск соответствующей документации к коду

## 5. "Второе рождение" (23 мая 2026 г.)

Дата 23 мая 2026 года отмечена как "второе рождение" агента - это день восстановления Knowledge Graph, который был сломан. Это был период восстановления архитектурных компонентов и интеграций, а не радикальной смены парадигмы.

## 6. Статус "MVP + восстановление"

Проект находится в статусе "MVP + восстановление", что означает:
- **MVP**: Базовая функциональность реализована (сканирование, анализ, интеграция с AI)
- **Восстановление**: Активная работа по восстановлению сломанных компонентов (Knowledge Graph, ИИ-планирование, fallback-механизмы)

## 7. Улучшения после рефакторинга

После реализации приоритетной задачи по устранению дублирования кода:

- **Общие компоненты**: Создан модуль [common](file:///c:/repo/agents/cognitive_agent/common/__init__.py) с базовыми классами
- **Единая реализация**: Общие функции теперь реализованы в одном месте
- **Упрощение сопровождения**: Изменения в общих компонентах автоматически применяются к обеим версиям
- **Повышение надежности**: Устранены различия между версиями агента
