# Аудит скриптов `scripts/`

**Дата:** 2026-06-01  
**Цель:** Полный аудит Python-скриптов после миграции kebab-case → snake_case

---

## 📊 Резюме

| Категория | Количество |
|-----------|------------|
| **Всего Python файлов** | 72 |
| ✅ **Snake Case** (корректно) | ~45 |
| ⚠️ **Kebab Case / Mixed** (требует переименования) | ~20 |
| ❌ **Дубликаты / Legacy** | ~7 |
| **Скриптов с kebab-case сервисами внутри** | 28 |

---

## 🗂️ Детальный список по категориям

### ✅ Snake Case (Корректные имена)

| Путь | Назначение | Зависимости от сервисов |
|------|------------|------------------------|
| `scripts/__init__.py` | Модуль scripts | Нет |
| `scripts/ai/run_gigacode_update.py` | Обновление GigaCode | Нет |
| `scripts/ai/update_gigacode_token.py` | Обновление токена GigaCode | Нет |
| `scripts/analyze_code_organization.py` | Анализ организации кода | Нет |
| `scripts/analyze_nesting.py` | Анализ вложенности | Нет |
| `scripts/check_ports.py` | Проверка портов | Нет |
| `scripts/check_service_structure.py` | Проверка структуры сервисов | Нет |
| `scripts/quick_test.py` | Минимальный health check | Нет |
| `scripts/restore_coverage.py` | Восстановление покрытия тестов | Нет |
| `scripts/automation/auto_fix_service_structure.py` | Исправление структуры | Нет |
| `scripts/automation/cleanup_root.py` | Очистка корня | Нет |
| `scripts/automation/consolidate_adrs.py` | Консолидация ADR | Нет |
| `scripts/automation/create_init_files.py` | Создание __init__.py | ⚠️ 3 упоминания |
| `scripts/automation/create_issue.py` | Создание GitHub Issue | ⚠️ 4 упоминания |
| `scripts/automation/create_service.py` | Создание сервиса | ⚠️ 1 упоминание |
| `scripts/automation/demo_integration.py` | Демонстрация интеграции | Нет |
| `scripts/automation/integrate_ai_config_manager.py` | Интеграция AI Config | Нет |
| `scripts/automation/phase1_2_config.py` | Конфигурация фазы 1.2 | ⚠️ 9 упоминаний |
| `scripts/automation/phase1_3_src.py` | Конфигурация фазы 1.3 | ⚠️ 4 упоминания |
| `scripts/automation/phase1_4_standardize.py` | Стандартизация фазы 1.4 | ⚠️ 7 упоминаний |
| `scripts/automation/start_dev.py` | Запуск разработки | Нет |
| `scripts/automation/start_server.py` | Запуск сервера | Нет |
| `scripts/ci/check_all_readme_links.py` | Проверка ссылок README | Нет |
| `scripts/ci/check_badge_urls.py` | Проверка URL бейджей | Нет |
| `scripts/ci/check_config.py` | Проверка конфигов | Нет |
| `scripts/ci/check_ports.py` | Проверка портов (дубликат?) | Нет |
| `scripts/ci/check_readme_quality.py` | Качество README | Нет |
| `scripts/ci/check_root_structure.py` | Структура корня | Нет |
| `scripts/ci/check_service_structure.py` | Структура сервисов | Нет |
| `scripts/ci/check_yaml_fixed.py` | Проверка YAML | Нет |
| `scripts/ci/validate_dependabot.py` | Валидация Dependabot | Нет |
| `scripts/dev/setup-vscode-extensions.py` | Установка VS Code расширений | Нет |
| `scripts/dev/vscode-extensions-manager.py` | Менеджер расширений | Нет |
| `scripts/diagnostics/analyze_code_organization.py` | Анализ организации | Нет |
| `scripts/diagnostics/analyze_nesting.py` | Анализ вложенности | Нет |
| `scripts/diagnostics/collect_metrics.py` | Сбор метрик | Нет |
| `scripts/diagnostics/collect_test_metrics.py` | Сбор метрик тестов | Нет |
| `scripts/diagnostics/complete_diagnostic.py` | Полный диагностикум | ⚠️ 10 упоминаний |
| `scripts/diagnostics/deep_test_analysis.py` | Глубокий анализ тестов | Нет |
| `scripts/diagnostics/health_check.py` | Health check | Нет |
| `scripts/generators/bulk_test_generator.py` | Генератор тестов | ⚠️ 5 упоминаний |
| `scripts/generators/enhance-badge-links.py` | Улучшение бейджей | Нет |
| `scripts/generators/generate_badges.py` | Генерация бейджей | Нет |
| `scripts/generators/generate_integration_tests.py` | Интеграционные тесты | ⚠️ 12 упоминаний |
| `scripts/generators/generate_readme.py` | Генерация README | Нет |
| `scripts/generators/generate_root_structure.py` | Структура корня | Нет |
| `scripts/generators/generate_routes.py` | Генерация маршрутов | Нет |
| `scripts/generators/generate_stats.py` | Статистика | Нет |
| `scripts/generators/generate_todo_report.py` | Отчёт TODO | Нет |
| `scripts/generators/rename_integration_tests.py` | Переименование тестов | ⚠️ 4 упоминания |
| `scripts/generators/run_enhanced_tests.py` | Запуск тестов | ⚠️ 11 упоминаний |
| `scripts/generators/run_enhanced_tests_individual.py` | Индивидуальные тесты | ⚠️ 11 упоминаний |
| `scripts/generators/run_integration_tests.py` | Запуск интеграции | ⚠️ 4 упоминания |
| `scripts/generators/update_readme_badges.py` | Обновление бейджей | Нет |
| `scripts/generators/update_service_readmes.py` | Обновление README сервисов | ⚠️ 11 упоминаний |
| `scripts/generators/update-coverage-badge.py` | Обновление бейджа покрытия | Нет |
| `scripts/python/healthcheck.py` | Health check | ⚠️ 3 упоминания |
| `scripts/python/migrate-sqlite-to-postgres.py` | Миграция БД | Нет |
| `scripts/python/test_yandex_gpt_integration.py` | Тест Yandex GPT | Нет |
| `scripts/security/scan_secrets.py` | Сканирование секретов | Нет |
| `scripts/utils/count_markers.py` | Подсчёт маркеров | ⚠️ 1 упоминание |
| `scripts/utils/quick_test.py` | Быстрый тест | Нет |
| `scripts/utils/restore_coverage.py` | Восстановление покрытия | Нет |
| `scripts/utils/run_cd_tests.py` | CD тесты | Нет |
| `scripts/utils/test_orchestrator.py` | Оркестратор тестов | Нет |

---

### ⚠️ Kebab Case / Mixed (Требует переименования)

| Путь | Предложенное имя | Назначение |
|------|-----------------|------------|
| `scripts/automation/auto-create-config-tests.py` | `auto_create_config_tests.py` | Авто-тесты конфигов |
| `scripts/automation/auto-integrate-config-manager.py` | `auto_integrate_config_manager.py` | Авто-интеграция AI Config |
| `scripts/ci/check-badges-health.py` | `check_badges_health.py` | Проверка здоровья бейджей |
| `scripts/ci/check-dependency-updates.py` | `check_dependency_updates.py` | Проверка обновлений зависимостей |
| `scripts/collect-readmes.py` | `collect_readmes.py` | Сбор README |
| `scripts/create_init_files.py` | *уже есть в automation/* | ❌ Дубликат |
| `scripts/dev/setup-vscode-extensions.py` | *уже есть в корневой* | ❌ Дубликат |
| `scripts/diagnostics/health-check-agents-codeassistant.py` | `health_check_cognitive_agent.py` | Health check (устаревшее имя) |
| `scripts/generators/enhance-badge-links.py` | `enhance_badge_links.py` | Улучшение ссылок бейджей |
| `scripts/generators/generate-workflow-diagram.py` | `generate_workflow_diagram.py` | Генерация диаграммы workflow |
| `scripts/generators/update-badges-enhanced.py` | `update_badges_enhanced.py` | Обновление бейджей (enhanced) |
| `scripts/migration/collect-readmes.py` | `collect_readmes.py` | Сбор README (migration) |
| `scripts/migration/fix-imports-after-migration.py` | `fix_imports_after_migration.py` | Исправление импортов |
| `scripts/migration/fix-old-imports.py` | `fix_old_imports.py` | Исправление старых импортов |
| `scripts/python/migrate-sqlite-to-postgres.py` | *оставить (migration script)* | OK |
| `scripts/python/sync-from-my-ecosystem.py` | *оставить (sync script)* | OK |
| `scripts/python/translate-docs.py` | *оставить (translation script)* | OK |
| `scripts/setup-vscode-extensions.py` | *дубликат dev/* | ❌ Удалить |
| `scripts/create_init_files.py` | *дубликат automation/* | ❌ Удалить |

---

### ❌ Дубликаты / Legacy (Рекомендуется удалить)

| Путь | Причина | Действие |
|------|---------|----------|
| `scripts/create_init_files.py` | Дубликат `scripts/automation/create_init_files.py` | Удалить |
| `scripts/setup-vscode-extensions.py` | Дубликат `scripts/dev/setup-vscode-extensions.py` | Удалить |
| `scripts/quick_test.py` | Дубликат `scripts/utils/quick_test.py` | Удалить |
| `scripts/restore_coverage.py` | Дубликат `scripts/utils/restore_coverage.py` | Удалить |
| `scripts/check_ports.py` | Дубликат `scripts/ci/check_ports.py` | Удалить |
| `scripts/analyze_code_organization.py` | Дубликат `scripts/diagnostics/analyze_code_organization.py` | Удалить |
| `scripts/analyze_nesting.py` | Дубликат `scripts/diagnostics/analyze_nesting.py` | Нет |
| `scripts/collect-readmes.py` | Дубликат `scripts/migration/collect-readmes.py` | Удалить |
| `scripts/ci/check_ports.py` | Тот же что `scripts/check_ports.py` | Удалить один |

---

## 📋 Скрипты с kebab-case именами сервисов (требуют исправления)

| Путь | Количество упоминаний | Приоритет |
|------|---------------------|-----------|
| `scripts/migration/fix-old-imports.py` | 24 | 🔴 Высокий |
| `scripts/migration/collect-readmes.py` | 24 | 🔴 Высокий |
| `scripts/collect-readmes.py` | 24 | 🔴 Высокий |
| `scripts/migration/fix-imports-after-migration.py` | 14 | 🔴 Высокий |
| `scripts/generators/generate_integration_tests.py` | 12 | 🟡 Средний |
| `scripts/generators/run_enhanced_tests.py` | 11 | 🟡 Средний |
| `scripts/generators/run_enhanced_tests_individual.py` | 11 | 🟡 Средний |
| `scripts/diagnostics/health-check-agents-codeassistant.py` | 11 | 🔴 Высокий (legacy имя) |
| `scripts/generators/enhanced_test_generator.py` | 11 | 🟡 Средний |
| `scripts/generators/update_service_readmes.py` | 11 | 🟡 Средний |
| `scripts/generators/generate_enhanced_tests.py` | 11 | 🟡 Средний |
| `scripts/diagnostics/complete_diagnostic.py` | 10 | 🟡 Средний |
| `scripts/automation/phase1_2_config.py` | 9 | 🟢 Низкий (migration script) |
| `scripts/automation/phase1_4_standardize.py` | 7 | 🟢 Низкий (migration script) |
| `scripts/python/sync-from-my-ecosystem.py` | 6 | 🟢 Низкий (sync script) |
| `scripts/generators/bulk_test_generator.py` | 5 | 🟢 Низкий |
| `scripts/automation/comprehensive_fix_pr84.py` | 5 | 🟢 Низкий |
| `scripts/generators/run_integration_tests.py` | 4 | 🟢 Низкий |
| `scripts/automation/create_issue.py` | 4 | 🟢 Низкий |
| `scripts/automation/phase1_3_src.py` | 4 | 🟢 Низкий |
| `scripts/generators/rename_integration_tests.py` | 4 | 🟢 Низкий |
| `scripts/generators/generate-workflow-diagram.py` | 4 | 🟢 Низкий |
| `scripts/automation/create_init_files.py` | 3 | 🟢 Низкий |
| `scripts/python/healthcheck.py` | 3 | 🟢 Низкий |
| `scripts/create_init_files.py` | 3 | 🟢 Низкий (удалить) |
| `scripts/utils/count_markers.py` | 1 | 🟢 Низкий |
| `scripts/automation/consolidate_adrs.py` | 1 | 🟢 Низкий |
| `scripts/automation/create_service.py` | 1 | 🟢 Низкий |

---

## 🔧 Рекомендации

### 1. Приоритет: Удалить дубликаты
```bash
# Удалить из Git
git rm scripts/create_init_files.py
git rm scripts/setup-vscode-extensions.py
git rm scripts/quick_test.py
git rm scripts/restore_coverage.py
git rm scripts/check_ports.py
git rm scripts/analyze_code_organization.py
git rm scripts/analyze_nesting.py
```

### 2. Приоритет: Переименовать kebab-case в snake-case
```bash
# Python скрипты
git mv scripts/automation/auto-create-config-tests.py scripts/automation/auto_create_config_tests.py
git mv scripts/automation/auto-integrate-config-manager.py scripts/automation/auto_integrate_config_manager.py
git mv scripts/ci/check-badges-health.py scripts/ci/check_badges_health.py
git mv scripts/ci/check-dependency-updates.py scripts/ci/check_dependency_updates.py
git mv scripts/collect-readmes.py scripts/collect_readmes.py
git mv scripts/generators/enhance-badge-links.py scripts/generators/enhance_badge_links.py
git mv scripts/generators/generate-workflow-diagram.py scripts/generators/generate_workflow_diagram.py
git mv scripts/generators/update-badges-enhanced.py scripts/generators/update_badges_enhanced.py
git mv scripts/migration/collect-readmes.py scripts/migration/collect_readmes.py
```

### 3. Приоритет: Исправить kebab-case сервисы в коде
Для скриптов с высоким приоритетом заменить:
- `cognitive-agent` → `cognitive_agent`
- `ai-config-manager` → `ai_config_manager`
- `decision-engine` → `decision_engine`
- `infra-orchestrator` → `infra_orchestrator`
- `job-automation-agent` → `job_automation_agent`
- `mcp-server` → `mcp_server`
- `thought-architecture` → `thought_architecture`
- `portfolio-organizer` → `portfolio_organizer`
- `system-proof` → `system_proof`
- `it-compass` → `it_compass`
- `knowledge-graph` → `knowledge_graph`
- `ml-model-registry` → `ml_model_registry`
- `auth-service` → `auth_service`
- `template-service` → `template_service`
- `career-development` → `career_development`

### 4. Приоритет: Удалить устаревшие migration скрипты
После завершения миграции:
- `scripts/automation/phase1_*.py` - устаревшие
- `scripts/migration/*` - если миграция завершена

---

## 📝 Примечания

1. **PS/BAT/SH файлы** не включены в этот анализ (только Python)
2. **Migration скрипты** (`phase1_*`) могут быть устаревшими - проверить актуальность
3. **health-check-agents-codeassistant.py** - использовать устаревшее имя, переименовать в `health_check_cognitive_agent.py`
4. Некоторые скрипты в `scripts/python/` - утилиты, могут требовать пересмотра

---

**Отчет сгенерирован:** 2026-06-01  
**Всего файлов:** 72 Python скрипта в `scripts/`
