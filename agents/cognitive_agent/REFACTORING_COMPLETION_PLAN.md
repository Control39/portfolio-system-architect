# План завершения рефакторинга Cognitive Agent

**Дата создания:** 2026-06-20
**Текущий статус:** ~70% завершено
**Цель:** Довести до 95%+ completion

---

## 📊 Текущее состояние

### ✅ Выполнено (70%)
1. **BaseCognitiveAgent** создан в `src/base_agent.py`
2. Обе версии агента наследуются от базового класса
3. Единая система логирования (`src/logging_config.py`)
4. Система кэширования исправлена (MemoryAwareCache, LRUCache, CacheManager)
5. 14/14 тестов в test_memory_management.py проходят
6. Базовая документация создана

### ❌ Осталось сделать (30%)

---

## 🎯 Приоритет 1: Критические проблемы (Week 1)

### Task 1.1: Устранить дублирование кода между версиями агентов
**Проблема:**
- `autonomous_agent.py` (1147 lines) - стандартная версия
- `autonomous_agent_enterprise.py` (652 lines) - enterprise версия с заглушками
- Много дублирующегося кода, особенно в методах безопасности и сканирования

**Анализ:**
```python
# autonomous_agent.py имеет:
- _load_guardrails() - полная реализация
- execute_task() - полная реализация
- scan_project() - полная реализация
- self_testing_module integration

# autonomous_agent_enterprise.py имеет:
- execute_task() - ЗАГЛУШКА (stub)
- Минимальная реализация для README automation
- Дублирует инициализацию code_analyzer, doc_analyzer, test_analyzer
```

**Решение:**
1. Перенести ВСЮ общую логику в `BaseCognitiveAgent`:
   - `_load_guardrails()`
   - `_validate_task()`
   - `_check_file_access()`
   - `scan_project()` базовая версия
   - `execute_task()` базовый framework

2. Стандартная версия должна только расширять base:
   ```python
   class AutonomousCognitiveAgent(BaseCognitiveAgent):
       def __init__(self, project_path=None):
           super().__init__(project_path)
           # Только специфичные дополнения
   ```

3. Enterprise версия должна быть ЧЕСТНОЙ реализацией, не заглушкой:
   - Либо удалить если не нужна
   - Либо реализовать полностью с enterprise фичами:
     - MetricsCollector
     - SelfHealingSystem
     - TaskPlanner с графами зависимостей
     - StateManager с snapshots

**Усилия:** 8-12 часов
**Зависимости:** None
**Риск:** Средний - нужно тщательно протестировать после рефакторинга

---

### Task 1.2: Решить структурную проблему с двумя директориями
**Проблема:**
- `agents/cognitive_agent/` - рабочая версия (71 items)
- `apps/cognitive_agent/` - пустая заглушка (только README + пустые dirs)

**Варианты решения:**

**Option A (Рекомендуется):** Удалить `apps/cognitive_agent/`
```bash
# apps/cognitive_agent явно устарел/не используется
rm -rf apps/cognitive_agent/
```
Причина: Вся функциональность в `agents/cognitive_agent/`, apps версия пустая

**Option B:** Если apps/cognitive_agent нужен как service endpoint:
- Создать FastAPI wrapper в apps/cognitive_agent/
- Импортировать логику из agents/cognitive_agent/
- Добавить API endpoints

**Решение:** Option A - удалить apps/cognitive_agent/

**Усилия:** 1 час
**Зависимости:** Проверить что ничего не ссылается на apps/cognitive_agent
**Риск:** Низкий

---

### Task 1.3: Исправить импорт paths глобально
**Проблема:**
- Некоторые файлы используют `from cognitive_agent.common import ...`
- Другие используют `from agents.cognitive_agent.common import ...`
- Это создает путаницу и ошибки импорта

**Решение:**
1. Стандартизировать на `agents.cognitive_agent.*` везде
2. Найти все файлы с неправильными импортами:
   ```bash
   grep -r "from cognitive_agent\." agents/cognitive_agent/ --include="*.py"
   ```
3. Исправить их все
4. Обновить conftest.py чтобы поддерживать оба варианта временно
5. Добавить lint rule чтобы предотвратить регрессию

**Файлы для проверки:**
- Все тесты в tests/
- modules/ поддиректории
- scripts/

**Усилия:** 3-4 часа
**Зависимости:** Task 1.2
**Риск:** Низкий

---

## 🎯 Приоритет 2: Завершить TODO и incomplete implementations (Week 2)

### Task 2.1: Audit всех TODO/FIXME комментариев
**Найдено:** 25+ TODO комментариев

**Категории:**

#### A. Критические (должны быть сделаны сейчас)
1. **modules/git_health/__init__.py**:
   - Line 117: `"last_commit": "unknown"` - получить реальное время
   - Line 156: GitHub API интеграция
   - Lines 347-357: Расчет метрик коммитов

   **Решение:** Реализовать или удалить модуль если не нужен

2. **modules/security/__init__.py**:
   - Line 179: Интеграция с реальным сканером секретов
   - Line 184: Сканер зависимостей
   - Line 189: Сканер кода
   - Lines 276-281: Реализовать исправление/митигацию

   **Решение:** Интегрировать bandit/safety/trivy или удалить заглушки

#### B. Тестовые заглушки (nice-to-have)
3. **tests/test_integration_cognitive_agent.py**:
   - 10+ мест с `# TODO: Implement actual integration test logic`

   **Решение:** Либо реализовать тесты, либо пометить как @pytest.mark.skip

4. **tests/test_integrations.py**:
   - 8+ TODO в тестах интеграции

   **Решение:**同上

#### C. API Endpoints (medium priority)
5. **src/api/endpoints.py**:
   - Line 81: `# TODO: Интегрировать scanner_main.py`
   - Line 96: `# TODO: Интегрировать planner_main.py + AI`
   - Line 106: `# TODO: Интегрировать выполнение skills`
   - Line 121: `# TODO: Интегрировать learning_main.py`
   - Line 130: `# TODO: Сканировать scripts/ папку`

   **Решение:** Реализовать endpoints или удалить файл если API не нужен

**План действий:**
1. Пройтись по каждому TODO
2. Для каждого решить: Implement / Remove / Defer
3. Создать issues для deferred items
4. Реализовать critical items

**Усилия:** 12-16 часов
**Зависимости:** None
**Риск:** Средний - некоторые TODO могут требовать значительной работы

---

### Task 2.2: Завершить incomplete modules
**Проблема:** В `modules/` есть частично реализованные модули

**Список модулей:**
```
modules/
├── architecture/ (1 item) - неполный
├── code_quality/ (1 item) - неполный
├── core/ (0 items) - пустой!
├── decision_maker/ (1 item) - неполный
├── documentation/ (0 items) - пустой!
├── execution/ (0 items) - пустой!
├── git_health/ (1 item) - TODO внутри
├── memory/ (1 item) - ?
├── mentor/ (1 item) - ?
├── monitoring/ (0 items) - пустой!
├── planning/ (0 items) - пустой!
├── reflexion/ (1 item) - ?
├── reporting/ (0 items) - пустой!
├── repository_history/ (1 item) - ?
├── security/ (1 item) - TODO внутри
└── test_coverage/ (1 item) - ?
```

**Решение:**
1. Для каждого модуля решить:
   - Реализовать полностью
   - Удалить (если не нужен)
   - Переместить в backlog

2. Пустые директории удалить:
   - core/, documentation/, execution/, monitoring/, planning/, reporting/

3. Неполные модули либо завершить, либо удалить

**Усилия:** 8-10 часов
**Зависимости:** Task 2.1
**Риск:** Средний

---

## 🎯 Приоритет 3: Улучшения качества (Week 3)

### Task 3.1: Упростить конфигурацию
**Проблема:** Конфигурация слишком сложная

**Файлы конфигурации:**
- `config/agent-config.yaml` - основной конфиг
- `config/mcp.json` - MCP config
- `config/prompts/` - промпты
- `.env.example` - environment variables

**Что упростить:**
1. Объединить разрозненные конфиги где возможно
2. Добавить валидацию схемы (Pydantic models)
3. Создать template для генерации конфигов
4. Документировать все параметры
5. Добавить defaults для всех опциональных параметров

**Усилия:** 6-8 часов
**Зависимости:** None
**Риск:** Низкий

---

### Task 3.2: Усилить безопасность
**Из DEEP_ANALYSIS_REPORT:**
- Path traversal vulnerabilities possible
- Need stricter input validation
- Add security audit for critical operations

**Конкретные задачи:**
1. Добавить валидацию путей файлов:
   ```python
   def _validate_path(self, path: str) -> bool:
       resolved = Path(path).resolve()
       return str(resolved).startswith(str(self.project_path))
   ```

2. Sanitize all user inputs before passing to shell/AI

3. Add rate limiting for AI calls

4. Implement command whitelist/blacklist более строго

5. Add security logging for all sensitive operations

**Усилия:** 6-8 часов
**Зависимости:** None
**Риск:** Средний - может сломать существующий функционал

---

### Task 3.3: Оптимизировать производительность ProjectScanner
**Проблемы:**
- Возможны утечки памяти при больших кодовых базах
- Нужен лучший caching mechanism

**Решения:**
1. Implement streaming file processing вместо загрузки всего в память
2. Use the new MemoryAwareCache для результатов сканирования
3. Add progress tracking для long scans
4. Parallelize file analysis where safe
5. Add scan result persistence (save/load between runs)

**Усилия:** 8-10 часов
**Зависимости:** Task 1.3 (imports fixed)
**Риск:** Средний

---

### Task 3.4: Дополнить документацию
** gaps identified:**
1. Многие файлы в `scripts/` имеют минимальную документацию
2. Не все навыки имеют SKILL.md
3. Сложные функции без комментариев

**План:**
1. Создать template для документации скриптов
2. Пройтись по всем public API и добавить docstrings
3. Обновить README.md с актуальной архитектурой
4. Создать CONTRIBUTING.md для разработчиков
5. Добавить примеры использования для основных функций

**Усилия:** 10-12 часов
**Зависимости:** None
**Риск:** Низкий

---

## 🎯 Приоритет 4: Тестирование (Week 4)

### Task 4.1: Улучшить тестовое покрытие
**Текущее состояние:**
- test_memory_management.py: 14/14 ✅
- Но много тестов - заглушки с TODO

**Задачи:**
1. Реализовать integration tests (сейчас stubs)
2. Добавить unit tests для новых компонентов:
   - MemoryAwareCache
   - LRUCache
   - CacheManager
3. Добавить performance tests для scanner
4. Добавить security tests
5. Aim for 80%+ code coverage

**Усилия:** 12-16 часов
**Зависимости:** Task 2.1, 2.2
**Риск:** Низкий

---

### Task 4.2: CI/CD improvements
**Добавить:**
1. Pre-commit hooks для linting
2. Automated testing on PR
3. Coverage reporting
4. Security scanning (bandit, safety)
5. Performance benchmarks

**Усилия:** 4-6 часов
**Зависимости:** Task 4.1
**Риск:** Низкий

---

## 📋 Roadmap Summary

### Week 1: Critical Fixes (20-25 hours)
- [ ] Task 1.1: Deduplicate agent code (8-12h)
- [ ] Task 1.2: Remove apps/cognitive_agent (1h)
- [ ] Task 1.3: Fix import paths (3-4h)
- [ ] Testing & verification (4-8h)

### Week 2: Complete TODOs (20-26 hours)
- [ ] Task 2.1: Audit and resolve all TODOs (12-16h)
- [ ] Task 2.2: Complete/remove incomplete modules (8-10h)

### Week 3: Quality Improvements (28-38 hours)
- [ ] Task 3.1: Simplify configuration (6-8h)
- [ ] Task 3.2: Enhance security (6-8h)
- [ ] Task 3.3: Optimize scanner performance (8-10h)
- [ ] Task 3.4: Complete documentation (10-12h)

### Week 4: Testing & Polish (16-22 hours)
- [ ] Task 4.1: Improve test coverage (12-16h)
- [ ] Task 4.2: CI/CD improvements (4-6h)

**Total Estimated Effort:** 84-111 hours (~2.5-3 weeks full-time)

---

## ⚠️ Risks & Mitigation

### Risk 1: Breaking changes during deduplication
**Mitigation:**
- Comprehensive test suite before starting
- Feature flags for gradual rollout
- Rollback plan documented

### Risk 2: Removing wrong TODOs/modules
**Mitigation:**
- Code review for each removal
- Check git history for usage
- Keep backups before deletion

### Risk 3: Performance optimizations introduce bugs
**Mitigation:**
- Benchmark before/after
- Extensive testing with large codebases
- Gradual optimization (profile first)

### Risk 4: Documentation becomes outdated quickly
**Mitigation:**
- Automate docs generation where possible
- Include docs in code review checklist
- Regular docs audit (monthly)

---

## ✅ Success Criteria

Рефакторинг считается завершенным когда:

1. **Code Quality:**
   - [ ] No code duplication between agent versions
   - [ ] Zero TODO/FIXME comments in production code
   - [ ] All public APIs have docstrings
   - [ ] Configuration validated with Pydantic

2. **Testing:**
   - [ ] 80%+ code coverage
   - [ ] All integration tests implemented
   - [ ] Performance benchmarks established
   - [ ] Security tests passing

3. **Architecture:**
   - [ ] Single source of truth (no apps/cognitive_agent confusion)
   - [ ] Consistent import patterns everywhere
   - [ ] Clear separation of concerns
   - [ ] Modules either complete or removed

4. **Documentation:**
   - [ ] README.md up to date
   - [ ] Architecture diagram current
   - [ ] API documentation complete
   - [ ] Contributing guide written

5. **Security:**
   - [ ] Path traversal prevented
   - [ ] Input validation comprehensive
   - [ ] Security audit logging active
   - [ ] No hardcoded secrets

---

## 🚀 Quick Wins (Start Here!)

Если хотите быстрые результаты, начните с:

1. **Task 1.2** - Удалить apps/cognitive_agent (1 hour, immediate clarity)
2. **Task 1.3** - Исправить импорты (3-4 hours, prevents future bugs)
3. **Task 2.1 Category B** - Удалить/пропустить тестовые TODO (2 hours, cleaner codebase)
4. **Task 3.4 partial** - Добавить docstrings к public API (4 hours, better DX)

Эти 4 задачи займут ~10 часов и дадут заметное улучшение качества кода.

---

## 📝 Next Steps

1. **Review this plan** с командой/stakeholders
2. **Prioritize** based on business needs
3. **Create GitHub issues** for each task
4. **Start with Quick Wins** для momentum
5. **Track progress** weekly against success criteria

---

**Last Updated:** 2026-06-20
**Status:** Plan created, awaiting approval
