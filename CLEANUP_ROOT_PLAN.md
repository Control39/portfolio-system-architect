# План очистки корня репозитория

## Цель
Очистить корень репозитория от временных файлов, архивов и отчётов, переместив отчёты в структурированную папку `reports/` и удалив ненужные файлы.

## Обоснование
В ходе аудита репозитория выявлены следующие проблемы:
1. Архивная папка `.archive-backup-20260425_181308/` занимает место и не должна быть в репозитории
2. Много отчётов в корне нарушают структуру проекта
3. Временные файлы (hello_world.py) не являются частью кодовой базы

## Детальный план действий

### Шаг 1: Создание структуры папок
```bash
# Создать папку для отчётов
mkdir -p reports/

# Создать подпапки для категоризации
mkdir -p reports/audit/
mkdir -p reports/quality/
mkdir -p reports/security/
mkdir -p reports/refactoring/
mkdir -p reports/setup/
```

### Шаг 2: Перемещение отчётов

#### Категория: Аудит (audit)
```bash
mv AUDIT_RESPONSE_ANALYSIS.md reports/audit/
mv REPOSITORY_AUDIT_CHECKLIST.md reports/audit/
mv REPOSITORY_AUDIT_IMPLEMENTATION_PLAN.md reports/audit/
mv AGENT_INTEGRATION_RECOMMENDATIONS.md reports/audit/
mv STRUCTURE_AUDIT_REPORT.md reports/audit/
```

#### Категория: Качество (quality)
```bash
mv quality-gates-report-20260416-1747.md reports/quality/
mv README_LINKS_REPORT.md reports/quality/
```

#### Категория: Безопасность (security)
```bash
mv SECURITY_VULNERABILITY_ANALYSIS_REPORT.md reports/security/
mv SECURITY.md reports/security/
mv SETUP_CODEQL_INSTRUCTIONS.md reports/security/
```

#### Категория: Рефакторинг (refactoring)
```bash
mv REFACTORING_SUMMARY.md reports/refactoring/
mv DUPLICATES_CLEANUP_REPORT.md reports/refactoring/
```

#### Категория: Настройка (setup)
```bash
mv PROFESSIONAL_ENVIRONMENT_SETUP_REPORT.md reports/setup/
```

### Шаг 3: Удаление архивной папки
```bash
# Проверить содержимое перед удалением
ls -la .archive-backup-20260425_181308/

# Удалить архивную папку
rm -rf .archive-backup-20260425_181308/
```

### Шаг 4: Удаление временных файлов
```bash
# Удалить тестовый файл
rm hello_world.py

# Проверить наличие других временных файлов
find . -maxdepth 1 -type f \( -name "*.tmp" -o -name "*.log" -o -name "*.bak" -o -name "*test*" \) | xargs rm -f
```

### Шаг 5: Обновление .gitignore
Добавить в `.gitignore` следующие паттерны:
```
# Временные файлы
*.tmp
*.log
*.bak
hello_world.py

# Архивные папки
.archive-backup-*/

# Отчёты (если не хотим их коммитить)
# reports/*.md
```

### Шаг 6: Создание CHANGELOG.md
Создать базовый файл CHANGELOG.md:
```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository audit system with comprehensive checklist
- Security policy and CodeQL setup instructions
- Structured reports directory for all audit reports

### Changed
- Cleaned up root directory by moving reports to reports/ folder
- Removed archive backup folder
- Updated .gitignore to exclude temporary files

### Fixed
- Security vulnerabilities in dependencies
- Repository structure issues identified in audit
EOF
```

### Шаг 7: Фиксация изменений
```bash
# Добавить все изменения
git add .

# Создать коммит
git commit -m "chore: clean up root directory

- Move all reports to reports/ directory
- Remove .archive-backup-20260425_181308/
- Delete hello_world.py and other temporary files
- Create CHANGELOG.md
- Update .gitignore"

# Отправить изменения
git push origin main
```

## Проверка после очистки

После выполнения всех шагов корень репозитория должен содержать только:
- Основные конфигурационные файлы (README.md, pyproject.toml, etc.)
- Директории проекта (apps/, src/, docs/, etc.)
- Папку reports/ с структурированными отчётами

## Риски и смягчение

1. **Потеря важных данных**: Архивная папка может содержать нужные файлы
   - **Смягчение**: Проверить содержимое перед удалением, создать backup вне репозитория при необходимости

2. **Сломанные ссылки**: Если другие файлы ссылаются на перемещённые отчёты
   - **Смягчение**: Обновить ссылки или создать символические ссылки

3. **История Git**: Удаление файлов не удаляет их из истории Git
   - **Смягчение**: Это нормально, файлы останутся в истории при необходимости восстановления

## Альтернативные варианты

1. **Оставить отчёты в корне**: Не рекомендуется, нарушает чистоту структуры
2. **Переместить в docs/reports/**: Более логично для документации, но reports/ более явно указывает на генерируемые отчёты
3. **Архивировать старые отчёты**: Можно сжать старые отчёты, но проще оставить в reports/

## Следующие шаги после очистки

1. Настроить автоматическую генерацию CHANGELOG.md из тегов
2. Реализовать auto-audit MVP на основе созданных чек-листов
3. Интегрировать аудит в CI/CD pipeline

---
*План создан: 2026-04-30*
*Статус: Ожидает реализации*
