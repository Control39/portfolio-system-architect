# Makefile для управления расширениями VS Code
# Упрощает запуск скриптов на разных платформах

.PHONY: help check install sync report dry-run clean test

# Конфигурация
CONFIG ?= ../config/vscode/vscode-extensions.json
PYTHON ?= python3
POWERSHELL ?= powershell
BASH ?= bash

# Определение ОС
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Помощь
help:
	@echo "$(BLUE)=== Система автоматизации расширений VS Code ===$(NC)"
	@echo ""
	@echo "Доступные команды:"
	@echo "  $(GREEN)make check$(NC)     - Проверить соответствие расширений"
	@echo "  $(GREEN)make install$(NC)   - Установить отсутствующие обязательные расширения"
	@echo "  $(GREEN)make sync$(NC)      - Полная синхронизация (установить недостающие, удалить исключенные)"
	@echo "  $(GREEN)make report$(NC)    - Сгенерировать подробный отчет"
	@echo "  $(GREEN)make dry-run$(NC)   - Предварительный просмотр изменений"
	@echo "  $(GREEN)make test$(NC)      - Запустить тесты"
	@echo "  $(GREEN)make clean$(NC)     - Очистить временные файлы"
	@echo ""
	@echo "Переменные:"
	@echo "  CONFIG=путь/к/конфигу   Указать альтернативный конфигурационный файл"
	@echo ""
	@echo "Примеры:"
	@echo "  make check CONFIG=../config/vscode/my-config.json"
	@echo "  make sync"
	@echo "  make dry-run"
	@echo ""
	@echo "Обнаруженная ОС: $(YELLOW)$(DETECTED_OS)$(NC)"

# Проверка соответствия
check:
	@echo "$(BLUE)Проверка соответствия расширений...$(NC)"
ifeq ($(DETECTED_OS),Windows)
	@$(POWERSHELL) -ExecutionPolicy Bypass -File vscode-extensions-windows.ps1 -Check -ConfigPath "$(CONFIG)"
else
	@$(BASH) vscode-extensions-unix.sh --check --config "$(CONFIG)"
endif

# Установка обязательных расширений
install:
	@echo "$(BLUE)Установка отсутствующих обязательных расширений...$(NC)"
ifeq ($(DETECTED_OS),Windows)
	@$(POWERSHELL) -ExecutionPolicy Bypass -File vscode-extensions-windows.ps1 -Install -ConfigPath "$(CONFIG)"
else
	@$(BASH) vscode-extensions-unix.sh --install --config "$(CONFIG)"
endif

# Полная синхронизация
sync:
	@echo "$(BLUE)Полная синхронизация расширений...$(NC)"
ifeq ($(DETECTED_OS),Windows)
	@$(POWERSHELL) -ExecutionPolicy Bypass -File vscode-extensions-windows.ps1 -Sync -ConfigPath "$(CONFIG)"
else
	@$(BASH) vscode-extensions-unix.sh --sync --config "$(CONFIG)"
endif

# Генерация отчета
report:
	@echo "$(BLUE)Генерация отчета о соответствии...$(NC)"
ifeq ($(DETECTED_OS),Windows)
	@$(POWERSHELL) -ExecutionPolicy Bypass -File vscode-extensions-windows.ps1 -Report -ConfigPath "$(CONFIG)"
else
	@$(BASH) vscode-extensions-unix.sh --report --config "$(CONFIG)"
endif

# Предварительный просмотр
dry-run:
	@echo "$(YELLOW)Предварительный просмотр изменений...$(NC)"
ifeq ($(DETECTED_OS),Windows)
	@$(POWERSHELL) -ExecutionPolicy Bypass -File vscode-extensions-windows.ps1 -Sync -ConfigPath "$(CONFIG)" -DryRun
else
	@$(BASH) vscode-extensions-unix.sh --sync --config "$(CONFIG)" --dry-run
endif

# Запуск Python скрипта напрямую
python-check:
	@echo "$(BLUE)Запуск Python скрипта...$(NC)"
	@$(PYTHON) vscode-extensions-manager.py --action check --config "$(CONFIG)"

python-sync:
	@echo "$(BLUE)Запуск Python скрипта для синхронизации...$(NC)"
	@$(PYTHON) vscode-extensions-manager.py --action sync --config "$(CONFIG)"

# Тестирование
test:
	@echo "$(BLUE)Запуск тестов...$(NC)"
	@echo "$(YELLOW)Тестирование конфигурационного файла...$(NC)"
	@$(PYTHON) -c "import json; json.load(open('$(CONFIG)', 'r')); print('✓ Конфигурация валидна')"
	@echo "$(YELLOW)Тестирование Python скрипта...$(NC)"
	@$(PYTHON) vscode-extensions-manager.py --action check --config "$(CONFIG)" --dry-run
	@echo "$(GREEN)✓ Все тесты пройдены$(NC)"

# Очистка временных файлов
clean:
	@echo "$(BLUE)Очистка временных файлов...$(NC)"
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Очистка завершена$(NC)"

# Проверка зависимостей
deps:
	@echo "$(BLUE)Проверка зависимостей...$(NC)"
ifeq ($(DETECTED_OS),Windows)
	@code --version > nul 2>&1 && echo "$(GREEN)✓ VS Code найден$(NC)" || echo "$(RED)✗ VS Code не найден$(NC)"
	@python --version > nul 2>&1 && echo "$(GREEN)✓ Python найден$(NC)" || echo "$(RED)✗ Python не найден$(NC)"
	@powershell -Command "Get-Command code" > nul 2>&1 && echo "$(GREEN)✓ PowerShell доступен$(NC)" || echo "$(RED)✗ PowerShell недоступен$(NC)"
else
	@which code > /dev/null 2>&1 && echo "$(GREEN)✓ VS Code найден$(NC)" || echo "$(RED)✗ VS Code не найден$(NC)"
	@which python3 > /dev/null 2>&1 && echo "$(GREEN)✓ Python3 найден$(NC)" || echo "$(RED)✗ Python3 не найден$(NC)"
	@which bash > /dev/null 2>&1 && echo "$(GREEN)✓ Bash найден$(NC)" || echo "$(RED)✗ Bash не найден$(NC)"
endif

# Статус системы
status:
	@echo "$(BLUE)=== Статус системы автоматизации ===$(NC)"
	@echo "ОС: $(YELLOW)$(DETECTED_OS)$(NC)"
	@echo "Конфигурация: $(YELLOW)$(CONFIG)$(NC)"
	@echo ""
	@echo "Доступные скрипты:"
	@ls -la *.py *.ps1 *.sh *.bat 2>/dev/null || dir *.py *.ps1 *.sh *.bat 2>/dev/null
	@echo ""
	@echo "Используйте $(GREEN)make check$(NC) для проверки соответствия"

# Справка по конфигурации
config-help:
	@echo "$(BLUE)=== Справка по конфигурации расширений ===$(NC)"
	@echo ""
	@echo "Конфигурационный файл: $(YELLOW)$(CONFIG)$(NC)"
	@echo ""
	@echo "Структура конфигурации:"
	@echo "  {"
	@echo "    \"required\": [\"расширение1\", \"расширение2\", ...],"
	@echo "    \"recommended\": [\"расширение3\", \"расширение4\", ...],"
	@echo "    \"optional\": [\"расширение5\", \"расширение6\", ...],"
	@echo "    \"excluded\": [\"расширение7\", \"расширение8\", ...]"
	@echo "  }"
	@echo ""
	@echo "Пример расширения: \"ms-python.python\""
	@echo "ID расширения можно найти в Marketplace VS Code"
	@echo ""
	@echo "Для обновления конфигурации:"
	@echo "  1. Отредактируйте файл $(CONFIG)"
	@echo "  2. Запустите $(GREEN)make sync$(NC) для применения изменений"
	@echo "  3. Используйте $(GREEN)make dry-run$(NC) для предварительного просмотра"
