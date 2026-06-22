# 📋 План Перемещения Файлов

**Дата:** 2026-06-22  
**Агент:** GigaCode  
**Статус:** Ожидает подтверждения пользователя

---

## 🎯 Цель

Организовать репозиторий Portfolio System Architect по 4-слойной архитектуре с корректным распределением скриптов по жизненному циклу.

---

## 📝 Шаги Выполнения

### Шаг 1: Создать отчет диагностики ✅

- [x] Проанализировать корневые файлы
- [x] Проверить структуру scripts/
- [x] Определить зависимости файлов
- [x] Создать отчет `REFACTORING_DIAGNOSIS_REPORT.md`

### Шаг 2: Переместить корневые файлы

#### 2.1 Переместить `check_integrations.py`

**Источник:** `C:/repo/check_integrations.py`  
**Назначение:** `C:/repo/scripts/runtime/diagnostics/`  
**Команда:**
```bash
mkdir -p scripts/runtime/diagnostics
move check_integrations.py scripts/runtime/diagnostics/
```

**Обоснование:** Скрипт проверяет интеграции (ChromaDB, Job Agent), относится к диагностике runtime.

#### 2.2 Переместить `test_fallback_fix.py`

**Источник:** `C:/repo/test_fallback_fix.py`  
**Назначение:** `C:/repo/scripts/build/test/`  
**Команда:**
```bash
mkdir -p scripts/build/test
move test_fallback_fix.py scripts/build/test/
```

**Обоснование:** Скрипт тестирует fallback режим, относится к тестированию build.

### Шаг 3: Организовать scripts/ по жизненному циклу

#### 3.1 scripts/dev/ (разработка)

**Текущее состояние:** 26+ файлов, 8 подпапок  
**Действие:** Оставить как есть

**Содержимое (из git ls-tree):**
- activate-venv.ps1
- clean-vscode-settings.ps1
- install-pre-commit.ps1
- reorganize-structure.ps1
- setup-dev.ps1
- setup-environment.sh
- setup-profile.ps1
- setup-venv-alias.ps1
- setup-vscode-extensions.py
- vscode-extensions-manager.*
- bin/, config/, docs/

#### 3.2 scripts/build/ (сборка и тестирование)

**Текущее состояние:** Пуста (подпапки существуют, но пусты)  
**Действие:** Заполнить подпапки и переместить файлы

**План:**
```
scripts/build/
├── test/                 (новая папка)
│   └── test_fallback_fix.py
├── generate/             (новая папка)
│   └── из scripts/generators/
│       ├── generate_badges.py
│       ├── update_readme_badges.py
│       ├── generate_root_structure.py
│       └── ...
└── ci/                   (уже существует, пуста)
    └── из scripts/ci/
        ├── check_all_readme_links.py
        ├── check_badge_urls.py
        ├── check_badges_health.py
        └── ...
```

#### 3.3 scripts/deploy/ (развертывание)

**Текущее состояние:** Не существует  
**Действие:** Создать и заполнить

**План:**
```
scripts/deploy/
├── docker/               (новая папка)
│   └── из scripts/deployment/
│       ├── deploy.sh
│       └── deploy-azure.ps1
└── kubernetes/           (новая папка)
    └── k8s-*.ps1/*.sh (если есть)
```

#### 3.4 scripts/runtime/ (мониторинг и управление)

**Текущее состояние:** 80+ файлов  
**Действие:** Очистить от избыточных скриптов

**План:**
```
scripts/runtime/
├── diagnostics/          (новая папка)
│   ├── health_check.py
│   ├── health_check_cognitive_agent.py
│   ├── collect_metrics.py
│   └── check_integrations.py
├── management/           (уже существует)
│   ├── start-all.sh
│   ├── stop-all.sh
│   └── ...
└── security/             (уже существует)
    ├── scan_secrets.py
    ├── ci_security.sh
    └── security-check.sh
```

### Шаг 4: Обновить .gitignore

**Проверить текущее содержимое .gitignore**

```bash
git diff HEAD -- .gitignore
```

**Обновить, если нужно:**
- Добавить правила для новых папок (dev/, build/, deploy/, runtime/)
- Убедиться, что отчеты агента не игнорируются

### Шаг 5: Создать README.md для каждой папки

#### 5.1 scripts/dev/README.md
**Содержание:**
- Описание папки (временные скрипты)
- Список подпапок
- Инструкции по очистке

#### 5.2 scripts/build/README.md
**Содержание:**
- Описание папки (CI/CD, тестирование)
- Список подпапок
- Инструкции по запуску

#### 5.3 scripts/deploy/README.md
**Содержание:**
- Описание папки (развертывание)
- Список подпапок
- Инструкции по развертыванию

#### 5.4 scripts/runtime/README.md
**Содержание:**
- Описание папки (мониторинг, диагностика)
- Список подпапок
- Инструкции по использованию

### Шаг 6: Проверить git status

```bash
git status
git diff HEAD --stat
git diff HEAD
```

### Шаг 7: Создать commit

**Вариант 1: Стандартный commit**
```bash
git add .
git commit -m "refactor: переорганизация scripts/ по 4-слойной архитектуре"
```

**Вариант 2: Байпас пред-commit хуков**
```bash
git add .
git commit --no-verify -m "refactor: переорганизация scripts/ по 4-слойной архитектуре"
```

---

## 🛑 Важные Примечания

### Файлы, Которые НЕЛЬЗЯ Удалять

1. **agent_self_analysis_report.txt**  
   - Назначение: Отчет агента для самообучения
   - Статус: В корне, **ОБЯЗАТЕЛЕН К СОХРАНЕНИЮ**

2. **complete_strategic_report.txt**  
   - Назначение: Стратегический отчет
   - Статус: В корне, **ОБЯЗАТЕЛЕН К СОХРАНЕНИЮ**

3. **agent_self_analysis_report.json**  
   - Назначение: JSON-версия отчета агента
   - Статус: В корне, **ОБЯЗАТЕЛЕН К СОХРАНЕНИЮ**

4. **complete_strategic_report.json**  
   - Назначение: JSON-версия стратегического отчета
   - Статус: В корне, **ОБЯЗАТЕЛЕН К СОХРАНЕНИЮ**

### Файлы, Которые Требуют Особого Внимания

1. **config_integration.py**  
   - Много файлов с этим именем в разных папках
   - Проверить, не сломан ли синтаксис

2. **test_*.py**  
   - Проверить зависимости перед перемещением

3. **security_*.py**  
   - Проверить, не содержат ли они API ключи

---

## ✅ Контрольный Список

- [ ] Создан отчет диагностики
- [ ] Перемещен `check_integrations.py`
- [ ] Перемещен `test_fallback_fix.py`
- [ ] Создана новая структура scripts/ (build/, deploy/, runtime/)
- [ ] Обновлены README.md для каждой папки
- [ ] Обновлен .gitignore
- [ ] Проверен `git status`
- [ ] Успешно создан commit
- [ ] Отчеты агента сохранены

---

## 📊 Ожидаемый Результат

После выполнения плана:

- **Корневых Python файлов:** 0 (все перемещены)
- **Корневых txt файлов:** 4 (отчеты агента)
- **Корневых json файлов:** 8 (отчеты и конфиги)
- **scripts/dev/:** 26+ файлов (оставить как есть)
- **scripts/build/:** 30+ файлов (CI/CD, тестирование, генерация)
- **scripts/deploy/:** 10+ файлов (Docker, K8s)
- **scripts/runtime/:** 60+ файлов (мониторинг, диагностика, управление)
- **Общее количество скриптов:** ~126+ файлов

---

**Статус:** 🟡 В ожидании подтверждения пользователя  
**Последнее обновление:** 2026-06-22
