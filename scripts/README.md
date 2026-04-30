# Скрипты автоматизации VS Code Extensions

## 📋 Обзор

Эта папка содержит скрипты для автоматического управления расширениями VS Code в проекте `portfolio-system-architect`. Система обеспечивает:

- ✅ **Автоматическую проверку** соответствия расширений
- 🔄 **Синхронизацию** между разработчиками
- 🚀 **Интеграцию с CI/CD** для контроля качества
- 📊 **Отчеты** о соответствии и рекомендации

## 🚀 Быстрый старт

### Для всех платформ (рекомендуется)

```bash
# Перейдите в корень проекта
cd /path/to/portfolio-system-architect

# Проверьте текущее состояние
make check

# Синхронизируйте расширения
make sync

# Предварительный просмотр изменений
make dry-run
```

### Для Windows

```powershell
# Используйте PowerShell скрипт
.\scripts\vscode-extensions-manager.bat --check
.\scripts\vscode-extensions-manager.bat --sync
.\scripts\vscode-extensions-manager.bat --dry-run

# Или напрямую через PowerShell
powershell -ExecutionPolicy Bypass -File scripts\vscode-extensions-windows.ps1 -Check
```

### Для Linux/macOS

```bash
# Сделайте скрипт исполняемым
chmod +x scripts/vscode-extensions-unix.sh

# Запустите проверку
./scripts/vscode-extensions-unix.sh --check

# Синхронизируйте расширения
./scripts/vscode-extensions-unix.sh --sync
```

## 📁 Структура файлов

| Файл | Назначение | Платформа |
|------|------------|-----------|
| `vscode-extensions-manager.py` | Основной Python скрипт | Все |
| `vscode-extensions-windows.ps1` | PowerShell скрипт | Windows |
| `vscode-extensions-unix.sh` | Bash скрипт | Linux/macOS |
| `vscode-extensions-manager.bat` | Batch скрипт запуска | Windows |
| `Makefile` | Универсальный интерфейс | Все |

## ⚙️ Конфигурация

Конфигурация расширений находится в `../config/vscode/vscode-extensions.json`:

```json
{
  "required": ["ms-python.python", "ms-python.vscode-pylance"],
  "recommended": ["ms-python.isort", "njpwerner.autodocstring"],
  "optional": ["Continue.continue"],
  "excluded": ["vscjava.vscode-java-debug"]
}
```

## 🔧 Доступные команды

### Через Makefile

```bash
make help           # Показать справку
make check          # Проверить соответствие
make install        # Установить обязательные расширения
make sync           # Полная синхронизация
make report         # Сгенерировать отчет
make dry-run        # Предварительный просмотр
make test           # Запустить тесты
make clean          # Очистить временные файлы
make deps           # Проверить зависимости
make status         # Показать статус системы
```

### Через Python скрипт

```bash
python vscode-extensions-manager.py --action check
python vscode-extensions-manager.py --action sync
python vscode-extensions-manager.py --action sync --dry-run
python vscode-extensions-manager.py --action report
python vscode-extensions-manager.py --output-score  # Для CI/CD
```

## 📊 Оценка соответствия

Система рассчитывает оценку соответствия:

- **Обязательные расширения:** 70% оценки
- **Исключенные расширения:** -10% за каждое
- **Минимальный порог:** 90% (в CI/CD)

## 🛠️ Разработка и тестирование

### Запуск тестов

```bash
make test
```

### Проверка зависимостей

```bash
make deps
```

### Создание кастомных скриптов

```python
#!/usr/bin/env python3
# custom-script.py

import sys
sys.path.append('.')  # Добавляем текущую папку в путь

from vscode_extensions_manager import VSCodeExtensionManager

manager = VSCodeExtensionManager()
compliance = manager.check_compliance()

print(f"Оценка: {compliance['compliance_score']:.1f}%")
```

## 🔄 Интеграция с CI/CD

Система автоматически проверяется в GitHub Actions:

- **При пуше** в ветки `main` и `develop`
- **При пул-реквестах**
- **Еженедельно** по расписанию

Workflow файл: `.github/workflows/vscode-extensions-check.yml`

## 🐛 Устранение неполадок

### Ошибка "VS Code не найден"

```bash
# Проверьте, что VS Code установлен и в PATH
code --version

# Если команда не найдена:
# 1. Запустите VS Code
# 2. Нажмите Ctrl+Shift+P
# 3. Выполните "Shell Command: Install 'code' command in PATH"
```

### Ошибка "Permission denied"

```bash
# Linux/macOS: Запустите с sudo
sudo make sync

# Или установите расширения вручную через VS Code
```

### Ошибка сети

```bash
# Проверьте подключение к интернету
# Убедитесь, что Marketplace VS Code доступен
```

## 📈 Мониторинг

### Отчеты

Система генерирует отчеты в нескольких форматах:

1. **Консольный вывод** - для быстрого просмотра
2. **Markdown файлы** - для документации
3. **CI/CD артефакты** - в GitHub Actions

### Логи

Все действия логируются с уровнями:
- INFO: Информационные сообщения
- WARNING: Предупреждения
- ERROR: Критические ошибки

## 🤝 Вклад в развитие

### Добавление новых расширений

1. Отредактируйте `../config/vscode/vscode-extensions.json`
2. Добавьте расширение в соответствующую категорию
3. Запустите `make check` для проверки
4. Создайте pull request

### Улучшение скриптов

1. Создайте issue с описанием улучшения
2. Создайте ветку для разработки
3. Реализуйте изменения
4. Протестируйте с `make test`
5. Создайте pull request

## 📚 Дополнительные ресурсы

- [Полная документация](../docs/vscode-extensions-automation.md)
- [Конфигурация расширений](../config/vscode/vscode-extensions.json)
- [CI/CD Workflow](../.github/workflows/vscode-extensions-check.yml)
- [Исходный код](vscode-extensions-manager.py)

## 📞 Поддержка

- **Проблемы:** Создайте issue в репозитории
- **Вопросы:** Обратитесь к документации
- **Предложения:** Создайте issue с тегом `enhancement`

---

*Последнее обновление: 2026-04-10*
*Версия: 1.0.0*
