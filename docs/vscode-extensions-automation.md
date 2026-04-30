# Система автоматизации управления расширениями VS Code

## Обзор

Система автоматизации управления расширениями VS Code предназначена для поддержания порядка и правильности настроек расширений в проекте. Она обеспечивает:

- **Автоматическую проверку** соответствия установленных расширений конфигурации проекта
- **Синхронизацию расширений** между разработчиками
- **Интеграцию с CI/CD** для контроля качества
- **Минимальное ручное вмешательство** благодаря полной автоматизации

## Архитектура системы

```
📁 portfolio-system-architect/
├── 📁 config/vscode/
│   ├── vscode-extensions.json          # Конфигурация расширений
│   └── vscode-recommended-extensions.json
├── 📁 scripts/
│   ├── vscode-extensions-manager.py    # Основной Python скрипт
│   ├── vscode-extensions-windows.ps1   # PowerShell скрипт для Windows
│   ├── vscode-extensions-unix.sh       # Bash скрипт для Unix
│   ├── vscode-extensions-manager.bat   # Batch скрипт для Windows
│   └── Makefile                        # Универсальный интерфейс
├── 📁 .github/workflows/
│   └── vscode-extensions-check.yml     # CI/CD проверка
└── 📁 docs/
    └── vscode-extensions-automation.md # Эта документация
```

## Быстрый старт

### 1. Проверка текущего состояния

```bash
# Используя Makefile (рекомендуется)
make check

# Или напрямую через Python
python scripts/vscode-extensions-manager.py --action check

# Или через PowerShell (Windows)
powershell -ExecutionPolicy Bypass -File scripts/vscode-extensions-windows.ps1 -Check
```

### 2. Синхронизация расширений

```bash
# Предварительный просмотр изменений
make dry-run

# Полная синхронизация
make sync

# Только установка обязательных расширений
make install
```

### 3. Генерация отчета

```bash
make report
```

## Конфигурация расширений

### Формат конфигурационного файла

Файл `config/vscode/vscode-extensions.json` содержит категории расширений:

```json
{
  "required": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter"
  ],
  "recommended": [
    "ms-python.isort",
    "njpwerner.autodocstring"
  ],
  "optional": [
    "Continue.continue",
    "yandex.yandex-code-assist"
  ],
  "excluded": [
    "vscjava.vscode-java-debug"
  ]
}
```

### Категории расширений

| Категория | Описание | Влияние на оценку |
|-----------|----------|-------------------|
| **required** | Обязательные расширения | Отсутствие снижает оценку на 70% |
| **recommended** | Рекомендуемые расширения | Не влияет на оценку, но отображается в отчете |
| **optional** | Опциональные расширения | Не влияет на оценку |
| **excluded** | Исключенные расширения | Наличие снижает оценку на 10% за каждое |

### Как найти ID расширения

1. Откройте VS Code
2. Перейдите в Marketplace расширений
3. Найдите нужное расширение
4. Скопируйте ID из URL или описания
   - Формат: `издатель.название`
   - Пример: `ms-python.python`

## Использование в CI/CD

### Автоматическая проверка

Система интегрирована с GitHub Actions и выполняет проверку:

1. **При каждом пуше** в ветки `main` и `develop`
2. **При каждом пул-реквесте**
3. **Еженедельно** по расписанию (понедельник, 9:00 UTC)

### Порог соответствия

По умолчанию минимальный порог соответствия установлен на **90%**. Если оценка ниже, workflow завершится с ошибкой.

### Ручной запуск

Вы можете запустить проверку вручную через GitHub Actions интерфейс:

1. Перейдите в **Actions** → **VS Code Extensions Compliance Check**
2. Нажмите **Run workflow**
3. Выберите ветку и опции

## Расширенные возможности

### Интеграция с CAA (Code Assistant Automation)

Система может быть интегрирована с Cognitive Automation Agent для полной автоматизации:

```python
# Пример интеграции с CAA
from scripts.vscode_extensions_manager import VSCodeExtensionManager

class VSCodeExtensionsCAAIntegration:
    def __init__(self):
        self.manager = VSCodeExtensionManager()

    def auto_sync(self):
        """Автоматическая синхронизация при запуске проекта"""
        compliance = self.manager.check_compliance()

        if compliance['compliance_score'] < 80:
            print("Обнаружены проблемы с расширениями. Запускаю синхронизацию...")
            self.manager.sync_extensions()
```

### Кастомные скрипты

Вы можете создавать собственные скрипты на основе системы:

```python
#!/usr/bin/env python3
# custom-vscode-sync.py

import sys
sys.path.append('scripts')

from vscode_extensions_manager import VSCodeExtensionManager

def custom_sync():
    manager = VSCodeExtensionManager()

    # Проверяем только обязательные расширения
    installed = set(manager.get_installed_extensions())
    required = set(manager.config.get("required", []))

    missing = required - installed

    if missing:
        print(f"Установка {len(missing)} отсутствующих расширений...")
        for ext in missing:
            manager.install_extension(ext)

    print("Синхронизация завершена")

if __name__ == "__main__":
    custom_sync()
```

## Устранение неполадок

### Ошибка "VS Code не найден"

**Проблема:** Скрипт не может найти команду `code`

**Решение:**
```bash
# Проверьте, что VS Code установлен и добавлен в PATH
code --version

# Если команда не найдена, добавьте VS Code в PATH
# Windows: Добавьте путь к VS Code в системные переменные
# Linux/macOS: Запустите VS Code и выполните "Install 'code' command in PATH"
```

### Ошибка "Permission denied"

**Проблема:** Недостаточно прав для установки расширений

**Решение:**
```bash
# Запустите скрипт с правами администратора
sudo make sync  # Linux/macOS

# Или запустите VS Code от имени администратора
```

### Ошибка "Network connection failed"

**Проблема:** Проблемы с сетью при установке расширений

**Решение:**
1. Проверьте подключение к интернету
2. Убедитесь, что Marketplace VS Code доступен
3. Попробуйте установить расширения вручную через VS Code

## Мониторинг и метрики

### Оценка соответствия

Система рассчитывает оценку соответствия по формуле:

```
Оценка = (Установленные обязательные / Все обязательные) × 70 - (Исключенные × 10)
```

### Отчеты

Система генерирует отчеты в нескольких форматах:

1. **Консольный отчет** - для быстрого просмотра
2. **Markdown отчет** - для документации
3. **CI/CD артефакты** - для анализа в GitHub Actions

### Логирование

Все действия системы логируются с разными уровнями:

- **INFO**: Информационные сообщения
- **WARNING**: Предупреждения
- **ERROR**: Критические ошибки

## Обновление системы

### Добавление новых расширений

1. Отредактируйте `config/vscode/vscode-extensions.json`
2. Добавьте расширения в соответствующие категории
3. Запустите проверку: `make check`
4. При необходимости выполните синхронизацию: `make sync`

### Обновление существующих расширений

Система автоматически обновляет расширения при синхронизации. Для принудительного обновления:

```bash
# Удалите и установите расширение заново
code --uninstall-extension publisher.extension
code --install-extension publisher.extension
```

## Интеграция с другими системами

### Docker

```dockerfile
# Dockerfile для разработки с предустановленными расширениями
FROM mcr.microsoft.com/vscode/devcontainers/python:3.10

# Копируем конфигурацию расширений
COPY config/vscode/vscode-extensions.json /tmp/vscode-extensions.json

# Устанавливаем расширения
RUN if command -v code > /dev/null 2>&1; then \
    python /workspace/scripts/vscode-extensions-manager.py --action sync --config /tmp/vscode-extensions.json; \
    fi
```

### VS Code Dev Containers

```json
// .devcontainer/devcontainer.json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter"
        // ... другие расширения из конфигурации
      ]
    }
  },
  "postCreateCommand": "python scripts/vscode-extensions-manager.py --action check"
}
```

## Часто задаваемые вопросы

### Вопрос: Зачем нужна эта система?

**Ответ:** Для обеспечения единообразия среды разработки между всеми участниками проекта, автоматического контроля качества и уменьшения времени на настройку окружения.

### Вопрос: Как часто нужно запускать синхронизацию?

**Ответ:** Рекомендуется запускать синхронизацию при:
- Первой настройке проекта
- Изменении конфигурации расширений
- Обнаружении расхождений в отчете проверки

### Вопрос: Что делать, если я хочу использовать расширение, которого нет в конфигурации?

**Ответ:** Добавьте его в категорию `optional` в конфигурационном файле и создайте pull request.

### Вопрос: Как отключить автоматическую проверку в CI/CD?

**Ответ:** Отредактируйте файл `.github/workflows/vscode-extensions-check.yml` или добавьте исключение в настройках репозитория.

## Контакты и поддержка

- **Документация:** [docs/vscode-extensions-automation.md](docs/vscode-extensions-automation.md)
- **Исходный код:** [scripts/vscode-extensions-manager.py](scripts/vscode-extensions-manager.py)
- **Проблемы:** Создайте issue в репозитории проекта

## Лицензия

Система распространяется под лицензией проекта. См. файл [LICENSE](../LICENSE) для подробностей.

---

*Последнее обновление: 2026-04-10*
*Версия системы: 1.0.0*
