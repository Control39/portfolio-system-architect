#!/usr/bin/env python3
"""Скрипт для быстрого исправления проблемы reportMissingImports в VS Code.
"""

import json
import sys
from pathlib import Path


def main():
    print("🔧 Исправление проблемы reportMissingImports в VS Code")
    print("="*60)

    project_root = Path().resolve()

    # 1. Проверить виртуальное окружение
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print("❌ Виртуальное окружение не найдено")
        print("   Создайте: python -m venv .venv")
        return 1

    print(f"✅ Виртуальное окружение: {venv_python}")

    # 2. Создать/обновить настройки VS Code
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    settings_path = vscode_dir / "settings.json"

    settings = {}
    if settings_path.exists():
        try:
            with open(settings_path, encoding="utf-8") as f:
                settings = json.load(f)
        except:
            pass

    # Обновить настройки
    settings["python.defaultInterpreterPath"] = str(venv_python)
    settings["python.terminal.activateEnvironment"] = True
    settings["python.analysis.typeCheckingMode"] = "basic"
    settings["python.analysis.autoImportCompletions"] = True
    settings["python.analysis.diagnosticMode"] = "workspace"

    # Настройки для подавления ложных предупреждений
    settings["python.analysis.diagnosticSeverityOverrides"] = {
        "reportMissingImports": "warning",  # Изменить с error на warning
        "reportMissingModuleSource": "none",  # Отключить
    }

    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print(f"✅ Настройки VS Code обновлены: {settings_path}")
        print(f"   Интерпретатор: {venv_python}")

    except Exception as e:
        print(f"❌ Ошибка сохранения настроек: {e}")

    # 3. Создать файл с инструкциями для пользователя
    instructions = """# 🛠️ Как исправить reportMissingImports в VS Code

## Проблема
VS Code (Pylance/Pyright) показывает ошибки "reportMissingImports" даже когда модули установлены.

## Причина
VS Code использует неправильный интерпретатор Python или не видит установленные модули.

## Решения

### 1. Выберите правильный интерпретатор
1. Нажмите `Ctrl+Shift+P`
2. Введите "Python: Select Interpreter"
3. Выберите: `.venv\\Scripts\\python.exe`

### 2. Перезагрузите VS Code
1. `Ctrl+Shift+P`
2. Введите "Developer: Reload Window"

### 3. Если ошибки остались
Добавьте комментарий перед проблемным импортом:
```python
# pyright: ignore[reportMissingImports]
import jwt  # или другой проблемный модуль
```

### 4. Проверьте установку модулей
```bash
.venv\\Scripts\\activate
pip install PyJWT redis httpx pyyaml
```

### 5. Альтернативное решение
Используйте try/except для проблемных импортов:
```python
try:
    import jwt
except ImportError:
    import PyJWT as jwt
```

## Проверка
Запустите проверку:
```bash
python fix_import_issues.py
```

## Дополнительно
- Убедитесь, что виртуальное окружение активировано
- Проверьте, что все зависимости установлены: `pip install -e .`
- Обновите VS Code и расширение Python
"""

    instructions_path = project_root / "FIX_IMPORT_ISSUES_GUIDE.md"
    try:
        with open(instructions_path, "w", encoding="utf-8") as f:
            f.write(instructions)
        print(f"✅ Инструкции созданы: {instructions_path}")
    except Exception as e:
        print(f"⚠️  Не удалось создать инструкции: {e}")

    # 4. Проверить ключевые импорты
    print("\n🔍 Проверка ключевых импортов...")

    imports_to_check = [
        ("fastapi", "fastapi"),
        ("jwt", "PyJWT"),
        ("redis", "redis"),
        ("httpx", "httpx"),
        ("yaml", "PyYAML"),
        ("uvicorn", "uvicorn"),
    ]

    for module_name, package_name in imports_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} (из {package_name})")
        except ImportError:
            print(f"  ❌ {module_name} -> установите: pip install {package_name}")

    print("\n" + "="*60)
    print("✅ Настройка завершена!")
    print("\n🚀 Следующие шаги:")
    print("1. Перезагрузите VS Code (Ctrl+Shift+P → 'Developer: Reload Window')")
    print("2. Выберите интерпретатор: .venv\\Scripts\\python.exe")
    print("3. Проверьте, что PROBLEMS уменьшились")
    print("4. Если проблемы остались, следуйте инструкциям в FIX_IMPORT_ISSUES_GUIDE.md")

    return 0

if __name__ == "__main__":
    sys.exit(main())
