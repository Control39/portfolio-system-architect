# РУЧНАЯ ОРГАНИЗАЦИЯ РЕПОЗИТОРИЯ
# План действий для перемещения файлов в новые категории

# Проверка текущего состояния
cd C:/repo
git status

# ========================================
# 1. СОЗДАНИЕ НОВЫХ КАТЕГОРИЙ
# ========================================

# Создать структуру utilities/
mkdir utilities\onboarding
mkdir utilities\helpers
mkdir utilities\learning

# Создать новые категории для scripts/
mkdir scripts\maintenance
mkdir scripts\migrations
mkdir scripts\backup

# Создать новые категории для tools/
mkdir tools\analyzers
mkdir tools\debuggers
mkdir tools\automation

# ========================================
# 2. ПЕРЕМЕЩЕНИЕ ФАЙЛОВ (НЕ-АГЕНТНЫЕ)
# ========================================

# 2.1 maintenance/ (из scripts/utils/)
move scripts\utils\check_status.ps1 scripts\maintenance\
move scripts\utils\quick_test.py scripts\maintenance\
move scripts\utils\restore_coverage.py scripts\maintenance\

# 2.2 backup/ (из scripts/)
move scripts\search_backup.ps1 scripts\backup\
move scripts\verify_hashes.ps1 scripts\backup\

# 2.3 analyzers/ (из tools/)
move tools\check_duplicates.py tools\analyzers\
move tools\check_rules.py tools\analyzers\
move tools\check_skills.py tools\analyzers\
move tools\check_skills_duplicates.py tools\analyzers\
move tools\check_teacher_duplicates.py tools\analyzers\
move tools\workspace_analyzer.py tools\analyzers\

# 2.4 debuggers/ (из scripts/diagnostics/)
move scripts\diagnostics\health_check.py tools\debuggers\
move scripts\diagnostics\complete_diagnostic.py tools\debuggers\
move scripts\diagnostics\debug_pytest_config.py tools\debuggers\

# 2.5 automation/ (из scripts/automation/)
move scripts\automation\consolidate_adrs.py tools\automation\
move scripts\automation\consolidate_cases.py tools\automation\
move scripts\automation\start_dev.py tools\automation\

# ========================================
# 3. ПРОВЕРКА ИЗМЕНЕНИЙ
# ========================================

# Проверить статус git
git status

# Проверить дифф
git diff --stat

# ========================================
# 4. КОММИТ И ПУШ
# ========================================

# Добавить только перемещенные файлы (git add -u для удаленных)
git add -u

# Добавить новые файлы
git add utilities\
git add scripts\maintenance\
git add scripts\migrations\
git add scripts\backup\
git add tools\analyzers\
git add tools\debuggers\
git add tools\automation\

# Если включить скрипт для фикса consolidate_adrs.py
git add scripts\automation\consolidate_adrs.py

# Закоммитить
git commit -m "organize: restructure repository into logical categories

- Created utilities/ directory with onboarding/helpers/learning subdirs
- Moved maintenance scripts to scripts/maintenance/
- Moved backup scripts to scripts/backup/
- Moved analyzer tools to tools/analyzers/
- Moved diagnostic tools to tools/debuggers/
- Moved automation tools to tools/automation/
- Preserved all agent-related scripts in their original locations

All file moves completed manually."

# Запушить
git push origin main
git push ssh.sourcecraft.dev main
