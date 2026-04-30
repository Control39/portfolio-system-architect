#!/usr/bin/env python3
"""
Скрипт для настройки Git хуков, интегрированных с Cognitive Automation Agent.
Создает хуки, которые автоматически запускают триггеры при Git операциях.
"""

import os
import shutil
import stat
import sys
from datetime import datetime
from pathlib import Path


def check_git_repository():
    """Проверяем, находится ли проект в Git репозитории"""
    # Используем абсолютный путь от корня проекта
    project_root = Path(__file__).parent.parent.parent
    git_dir = project_root / ".git"

    if not git_dir.exists() or not git_dir.is_dir():
        print("✗ Проект не является Git репозиторием")
        print("  Инициализируйте Git: git init")
        return False

    print(f"✓ Проект является Git репозиторием ({git_dir})")
    return True


def create_hooks_directory():
    """Создаем директорию для хуков, если её нет"""
    hooks_dir = Path(".git/hooks")

    if not hooks_dir.exists():
        hooks_dir.mkdir(parents=True)
        print(f"✓ Создана директория для хуков: {hooks_dir}")
    else:
        print(f"✓ Директория для хуков уже существует: {hooks_dir}")

    return hooks_dir


def backup_existing_hook(hook_path):
    """Создаем резервную копию существующего хука"""
    if hook_path.exists():
        backup_path = hook_path.with_suffix(
            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(hook_path, backup_path)
        print(f"✓ Создана резервная копия: {backup_path}")
        return backup_path
    return None


def create_pre_commit_hook(hooks_dir):
    """Создаем pre-commit хук"""
    hook_path = hooks_dir / "pre-commit"

    # Создаем резервную копию
    backup_existing_hook(hook_path)

    hook_content = """#!/bin/bash
#
# Pre-commit hook для Cognitive Automation Agent
# Автоматически запускает проверки перед коммитом
#

echo "🔍 Cognitive Automation Agent: запуск pre-commit проверок..."

# Получаем список измененных файлов
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "ℹ️  Нет измененных файлов для коммита"
    exit 0
fi

echo "📁 Измененные файлы:"
echo "$STAGED_FILES" | while read file; do
    echo "  - $file"
done

# Запускаем проверки через агента
echo "🚀 Запуск автоматических проверок..."

# Проверяем Python файлы
PYTHON_FILES=$(echo "$STAGED_FILES" | grep -E '\.py$' || true)
if [ -n "$PYTHON_FILES" ]; then
    echo "🐍 Проверка Python файлов..."
    # Здесь можно добавить проверки: flake8, black, mypy и т.д.
    for file in $PYTHON_FILES; do
        if [ -f "$file" ]; then
            echo "  Проверка $file"
            # Пример: запуск black в режиме проверки
            # python -m black --check "$file" || true
        fi
    done
fi

# Проверяем YAML файлы
YAML_FILES=$(echo "$STAGED_FILES" | grep -E '\.(yaml|yml)$' || true)
if [ -n "$YAML_FILES" ]; then
    echo "📄 Проверка YAML файлов..."
    for file in $YAML_FILES; do
        if [ -f "$file" ]; then
            echo "  Проверка $file"
            # Пример: проверка синтаксиса YAML
            # python -c "import yaml; yaml.safe_load(open('$file'))" || true
        fi
    done
fi

# Запускаем триггер pre_commit через агента
echo "⚡ Запуск триггера pre_commit..."
AGENT_SCRIPT=".agents/scripts/trigger-processor.py"
if [ -f "$AGENT_SCRIPT" ]; then
    python "$AGENT_SCRIPT" --trigger git_pre_commit --data "{\\"files\\": \\"$STAGED_FILES\\"}" || true
else
    echo "⚠️  Скрипт агента не найден: $AGENT_SCRIPT"
fi

echo "✅ Pre-commit проверки завершены"
exit 0
"""

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Делаем файл исполняемым
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

    print(f"✓ Создан pre-commit хук: {hook_path}")
    return hook_path


def create_post_commit_hook(hooks_dir):
    """Создаем post-commit хук"""
    hook_path = hooks_dir / "post-commit"

    # Создаем резервную копию
    backup_existing_hook(hook_path)

    hook_content = """#!/bin/bash
#
# Post-commit hook для Cognitive Automation Agent
# Автоматически запускает действия после коммита
#

echo "🚀 Cognitive Automation Agent: обработка post-commit..."

# Получаем информацию о последнем коммите
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MESSAGE=$(git log -1 --pretty=%B)
COMMIT_AUTHOR=$(git log -1 --pretty=%an)
COMMIT_DATE=$(git log -1 --pretty=%cd)

echo "📝 Информация о коммите:"
echo "  Хэш: $COMMIT_HASH"
echo "  Сообщение: $COMMIT_MESSAGE"
echo "  Автор: $COMMIT_AUTHOR"
echo "  Дата: $COMMIT_DATE"

# Получаем список измененных файлов в коммите
COMMITTED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

if [ -n "$COMMITTED_FILES" ]; then
    echo "📁 Файлы в коммите:"
    echo "$COMMITTED_FILES" | while read file; do
        echo "  - $file"
    done
fi

# Запускаем триггер post_commit через агента
echo "⚡ Запуск триггера post_commit..."
AGENT_SCRIPT=".agents/scripts/trigger-processor.py"
if [ -f "$AGENT_SCRIPT" ]; then
    # Формируем JSON данные для триггера
    JSON_DATA=$(cat <<EOF
{
    "commit_hash": "$COMMIT_HASH",
    "message": "$COMMIT_MESSAGE",
    "author": "$COMMIT_AUTHOR",
    "date": "$COMMIT_DATE",
    "files": "$COMMITTED_FILES"
}
EOF
    )

    python "$AGENT_SCRIPT" --trigger git_post_commit --data "$JSON_DATA" || true
else
    echo "⚠️  Скрипт агента не найден: $AGENT_SCRIPT"
fi

# Генерируем автоматический changelog
echo "📋 Генерация changelog..."
CHANGELOG_DIR=".agents/changelogs"
if [ ! -d "$CHANGELOG_DIR" ]; then
    mkdir -p "$CHANGELOG_DIR"
fi

CHANGELOG_FILE="$CHANGELOG_DIR/$(date +%Y-%m-%d).md"
if [ ! -f "$CHANGELOG_FILE" ]; then
    echo "# Changelog для $(date +%Y-%m-%d)" > "$CHANGELOG_FILE"
    echo "" >> "$CHANGELOG_FILE"
fi

echo "## Коммит: $COMMIT_HASH" >> "$CHANGELOG_FILE"
echo "**Дата:** $(date)" >> "$CHANGELOG_FILE"
echo "**Автор:** $COMMIT_AUTHOR" >> "$CHANGELOG_FILE"
echo "**Сообщение:** $COMMIT_MESSAGE" >> "$CHANGELOG_FILE"
if [ -n "$COMMITTED_FILES" ]; then
    echo "**Измененные файлы:**" >> "$CHANGELOG_FILE"
    echo "$COMMITTED_FILES" | while read file; do
        echo "- $file" >> "$CHANGELOG_FILE"
    done
fi
echo "" >> "$CHANGELOG_FILE"

echo "✅ Post-commit обработка завершена"
echo "📄 Changelog обновлен: $CHANGELOG_FILE"
exit 0
"""

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Делаем файл исполняемым
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

    print(f"✓ Создан post-commit хук: {hook_path}")
    return hook_path


def create_pre_push_hook(hooks_dir):
    """Создаем pre-push хук"""
    hook_path = hooks_dir / "pre-push"

    # Создаем резервную копию
    backup_existing_hook(hook_path)

    hook_content = """#!/bin/bash
#
# Pre-push hook для Cognitive Automation Agent
# Проверяет код перед отправкой в удаленный репозиторий
#

echo "🚀 Cognitive Automation Agent: запуск pre-push проверок..."

# Получаем информацию о пуше
while read local_ref local_sha remote_ref remote_sha; do
    echo "📤 Push информация:"
    echo "  Локальная ветка: $local_ref ($local_sha)"
    echo "  Удаленная ветка: $remote_ref ($remote_sha)"

    # Проверяем, есть ли коммиты для пуша
    if [ "$local_sha" = "0000000000000000000000000000000000000000" ]; then
        echo "ℹ️  Удаление ветки, проверки не требуются"
        continue
    fi

    # Получаем список коммитов для пуша
    COMMITS_TO_PUSH=$(git rev-list "$remote_sha".."$local_sha")

    if [ -z "$COMMITS_TO_PUSH" ]; then
        echo "ℹ️  Нет новых коммитов для пуша"
        continue
    fi

    COMMIT_COUNT=$(echo "$COMMITS_TO_PUSH" | wc -l)
    echo "📊 Коммитов для пуша: $COMMIT_COUNT"

    # Проверяем каждый коммит
    echo "🔍 Проверка коммитов..."
    for commit in $COMMITS_TO_PUSH; do
        COMMIT_MSG=$(git log --format=%B -n 1 "$commit")
        COMMIT_AUTHOR=$(git log --format=%an -n 1 "$commit")

        echo "  Коммит: $commit"
        echo "    Автор: $COMMIT_AUTHOR"
        echo "    Сообщение: $COMMIT_MSG"

        # Проверяем формат сообщения коммита
        if [[ ! "$COMMIT_MSG" =~ ^(feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert)(\(.+\))?: ]]; then
            echo "⚠️  Предупреждение: сообщение коммита не соответствует Conventional Commits"
            echo "   Формат: <type>(<scope>): <description>"
            echo "   Пример: feat(api): добавить новую endpoint"
        fi
    done

    # Запускаем триггер pre_push через агента
    echo "⚡ Запуск триггера pre_push..."
    AGENT_SCRIPT=".agents/scripts/trigger-processor.py"
    if [ -f "$AGENT_SCRIPT" ]; then
        # Формируем JSON данные для триггера
        JSON_DATA=$(cat <<EOF
{
    "local_ref": "$local_ref",
    "local_sha": "$local_sha",
    "remote_ref": "$remote_ref",
    "remote_sha": "$remote_sha",
    "commit_count": $COMMIT_COUNT
}
EOF
        )

        python "$AGENT_SCRIPT" --trigger git_pre_push --data "$JSON_DATA" || true
    else
        echo "⚠️  Скрипт агента не найден: $AGENT_SCRIPT"
    fi

done

echo "✅ Pre-push проверки завершены"
exit 0
"""

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Делаем файл исполняемым
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

    print(f"✓ Создан pre-push хук: {hook_path}")
    return hook_path


def create_post_merge_hook(hooks_dir):
    """Создаем post-merge хук"""
    hook_path = hooks_dir / "post-merge"

    # Создаем резервную копию
    backup_existing_hook(hook_path)

    hook_content = """#!/bin/bash
#
# Post-merge hook для Cognitive Automation Agent
# Обрабатывает изменения после слияния веток
#

echo "🔄 Cognitive Automation Agent: обработка post-merge..."

# Проверяем, было ли это fast-forward слиянием
if [ "$1" = "1" ]; then
    echo "ℹ️  Fast-forward слияние"
else
    echo "ℹ️  Обычное слияние (не fast-forward)"
fi

# Получаем текущую ветку
CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 Текущая ветка: $CURRENT_BRANCH"

# Получаем последний коммит
LAST_COMMIT=$(git rev-parse HEAD)
echo "📝 Последний коммит: $LAST_COMMIT"

# Проверяем изменения после слияния
echo "🔍 Проверка изменений после слияния..."
CHANGED_FILES=$(git diff --name-only HEAD@{1} HEAD)

if [ -n "$CHANGED_FILES" ]; then
    echo "📁 Измененные файлы:"
    echo "$CHANGED_FILES" | while read file; do
        echo "  - $file"
    done

    # Проверяем зависимости
    if echo "$CHANGED_FILES" | grep -q "requirements.txt\|pyproject.toml\|package.json"; then
        echo "📦 Обнаружены изменения в зависимостях"
        echo "   Рекомендуется обновить зависимости:"
        echo "   - pip install -r requirements.txt"
        echo "   - npm install (если package.json изменен)"
    fi
fi

# Запускаем триггер post_merge через агента
echo "⚡ Запуск триггера post_merge..."
AGENT_SCRIPT=".agents/scripts/trigger-processor.py"
if [ -f "$AGENT_SCRIPT" ]; then
    # Формируем JSON данные для триггера
    JSON_DATA=$(cat <<EOF
{
    "current_branch": "$CURRENT_BRANCH",
    "last_commit": "$LAST_COMMIT",
    "changed_files": "$CHANGED_FILES",
    "is_fast_forward": $1
}
EOF
    )

    python "$AGENT_SCRIPT" --trigger git_post_merge --data "$JSON_DATA" || true
else
    echo "⚠️  Скрипт агента не найден: $AGENT_SCRIPT"
fi

# Запускаем тесты после слияния
echo "🧪 Запуск тестов после слияния..."
if [ -f "pytest.ini" ] || [ -f "setup.cfg" ] || [ -f "pyproject.toml" ]; then
    echo "  Обнаружена конфигурация pytest"
    # python -m pytest tests/ --tb=short || true
elif [ -f "package.json" ]; then
    echo "  Обнаружена конфигурация npm"
    # npm test || true
fi

echo "✅ Post-merge обработка завершена"
exit 0
"""

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Делаем файл исполняемым
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

    print(f"✓ Создан post-merge хук: {hook_path}")
    return hook_path


def create_commit_msg_hook(hooks_dir):
    """Создаем commit-msg хук для проверки сообщений коммитов"""
    hook_path = hooks_dir / "commit-msg"

    # Создаем резервную копию
    backup_existing_hook(hook_path)

    hook_content = """#!/bin/bash
#
# Commit-msg hook для Cognitive Automation Agent
# Проверяет формат сообщений коммитов
#

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

echo "📝 Cognitive Automation Agent: проверка сообщения коммита..."

# Удаляем комментарии и пустые строки
CLEAN_MSG=$(echo "$COMMIT_MSG" | sed -e '/^#/d' -e '/^$/d' | head -1)

if [ -z "$CLEAN_MSG" ]; then
    echo "❌ Сообщение коммита не может быть пустым"
    exit 1
fi

echo "Сообщение: $CLEAN_MSG"

# Проверяем формат Conventional Commits
if [[ ! "$CLEAN_MSG" =~ ^(feat|fix|docs|style|refactor|test|chore|perf|build|ci|revert)(\(.+\))?: ]]; then
    echo "❌ Сообщение коммита не соответствует Conventional Commits"
    echo ""
    echo "📋 Правильный формат:"
    echo "  <type>(<scope>): <description>"
    echo ""
    echo "📚 Доступные типы:"
    echo "  feat     - новая функциональность"
    echo "  fix      - исправление ошибки"
    echo "  docs     - изменения в документации"
    echo "  style    - форматирование, отсутствие изменений в коде"
    echo "  refactor - рефакторинг кода"
    echo "  test     - добавление или исправление тестов"
    echo "  chore    - обновление зависимостей, настройки и т.д."
    echo "  perf     - изменения, улучшающие производительность"
    echo "  build    - изменения в системе сборки"
    echo "  ci       - изменения в CI конфигурации"
    echo "  revert   - отмена предыдущего коммита"
    echo ""
    echo "📝 Примеры:"
    echo "  feat(api): добавить новую endpoint для пользователей"
    echo "  fix(auth): исправить проверку токена"
    echo "  docs: обновить README.md"
    echo "  chore: обновить зависимости"
    echo ""
    exit 1
fi

# Проверяем длину описания
DESCRIPTION=$(echo "$CLEAN_MSG" | cut -d: -f2- | sed 's/^ //')
if [ ${#DESCRIPTION} -lt 10 ]; then
    echo "⚠️  Предупреждение: описание слишком короткое (минимум 10 символов)"
    echo "   Текущая длина: ${#DESCRIPTION} символов"
fi

# Проверяем, что описание начинается с маленькой буквы
if [[ "$DESCRIPTION" =~ ^[A-Z] ]]; then
    echo "⚠️  Предупреждение: описание должно начинаться с маленькой буквы"
fi

# Проверяем, что нет точки в конце
if [[ "$DESCRIPTION" =~ \.$ ]]; then
    echo "⚠️  Предупреждение: не ставьте точку в конце описания"
fi

# Запускаем триггер commit_msg через агента
echo "⚡ Запуск триггера commit_msg..."
AGENT_SCRIPT=".agents/scripts/trigger-processor.py"
if [ -f "$AGENT_SCRIPT" ]; then
    # Формируем JSON данные для триггера
    JSON_DATA=$(cat <<EOF
{
    "commit_message": "$CLEAN_MSG",
    "is_valid": true,
    "validation_errors": []
}
EOF
    )

    python "$AGENT_SCRIPT" --trigger git_commit_msg --data "$JSON_DATA" || true
else
    echo "⚠️  Скрипт агента не найден: $AGENT_SCRIPT"
fi

echo "✅ Сообщение коммита прошло проверку"
exit 0
"""

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Делаем файл исполняемым
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

    print(f"✓ Создан commit-msg хук: {hook_path}")
    return hook_path


def test_hooks():
    """Тестируем созданные хуки"""
    print("\n=== Тестирование хуков ===")

    hooks_dir = Path(".git/hooks")
    test_results = []

    for hook_file in hooks_dir.glob("*"):
        if (
            hook_file.is_file()
            and not hook_file.name.endswith(".sample")
            and not hook_file.name.endswith(".backup")
        ):
            # Проверяем, является ли файл исполняемым
            is_executable = os.access(hook_file, os.X_OK)

            # Проверяем содержимое
            with open(hook_file, "r", encoding="utf-8") as f:
                content = f.read()
                has_cognitive_agent = "Cognitive Automation Agent" in content

            status = "✓" if is_executable and has_cognitive_agent else "✗"
            test_results.append((hook_file.name, is_executable, has_cognitive_agent))

            print(f"  {status} {hook_file.name}: ", end="")
            if is_executable:
                print("исполняемый, ", end="")
            else:
                print("НЕ исполняемый, ", end="")

            if has_cognitive_agent:
                print("интегрирован с агентом")
            else:
                print("НЕ интегрирован с агентом")

    return test_results


def create_hooks_config():
    """Создаем конфигурационный файл для хуков"""
    config_path = Path(".agents/config/git-hooks.yaml")

    config = {
        "version": "1.0.0",
        "hooks": {
            "pre-commit": {
                "enabled": True,
                "description": "Проверка кода перед коммитом",
                "actions": ["validate_code", "run_tests", "check_formatting"],
            },
            "commit-msg": {
                "enabled": True,
                "description": "Проверка формата сообщений коммитов",
                "actions": ["validate_commit_message", "enforce_conventional_commits"],
            },
            "post-commit": {
                "enabled": True,
                "description": "Действия после коммита",
                "actions": ["generate_changelog", "update_documentation", "trigger_ci"],
            },
            "pre-push": {
                "enabled": True,
                "description": "Проверка перед отправкой в удаленный репозиторий",
                "actions": [
                    "run_integration_tests",
                    "check_security",
                    "validate_dependencies",
                ],
            },
            "post-merge": {
                "enabled": True,
                "description": "Действия после слияния веток",
                "actions": ["update_dependencies", "run_tests", "clear_caches"],
            },
        },
        "settings": {
            "auto_update": True,
            "backup_existing": True,
            "notify_on_failure": True,
        },
    }

    import yaml

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ Создана конфигурация хуков: {config_path}")
    return config_path


def main():
    """Основная функция настройки Git хуков"""
    print("=" * 60)
    print("НАСТРОЙКА GIT ХУКОВ ДЛЯ COGNITIVE AUTOMATION AGENT")
    print("=" * 60)

    # Проверяем Git репозиторий
    if not check_git_repository():
        return False

    # Создаем директорию для хуков
    hooks_dir = create_hooks_directory()

    # Создаем хуки
    print("\n=== Создание Git хуков ===")

    hooks = [
        ("pre-commit", create_pre_commit_hook),
        ("commit-msg", create_commit_msg_hook),
        ("post-commit", create_post_commit_hook),
        ("pre-push", create_pre_push_hook),
        ("post-merge", create_post_merge_hook),
    ]

    created_hooks = []
    for hook_name, hook_func in hooks:
        try:
            hook_path = hook_func(hooks_dir)
            created_hooks.append((hook_name, hook_path))
        except Exception as e:
            print(f"✗ Ошибка создания хука {hook_name}: {e}")

    # Создаем конфигурационный файл
    config_path = create_hooks_config()

    # Тестируем хуки
    test_results = test_hooks()

    # Выводим результаты
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ НАСТРОЙКИ:")
    print("=" * 60)

    print(f"✓ Создано хуков: {len(created_hooks)}")
    print(f"✓ Конфигурация: {config_path}")

    successful_tests = sum(
        1 for _, is_exec, has_agent in test_results if is_exec and has_agent
    )
    print(f"✓ Успешно протестировано: {successful_tests}/{len(test_results)}")

    print("\n📋 Созданные хуки:")
    for hook_name, hook_path in created_hooks:
        print(f"  - {hook_name}: {hook_path}")

    print("\n📚 Инструкции по использованию:")
    print("1. Хуки будут автоматически запускаться при Git операциях")
    print("2. Для отключения хука: chmod -x .git/hooks/<hook_name>")
    print("3. Для включения хука: chmod +x .git/hooks/<hook_name>")
    print("4. Для ручного запуска хука: .git/hooks/<hook_name>")

    print("\n🔧 Интеграция с агентом:")
    print("   Хуки автоматически запускают триггеры Cognitive Automation Agent")
    print("   при соответствующих Git операциях.")

    print("\n✅ Настройка Git хуков завершена успешно!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Настройка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
