# Настройка VS Code для проекта portfolio-system-architect

## 📦 Рекомендуемые расширения

### Установка через командную строку (пакетно):
```bash
# Основные расширения Python и DevOps
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension LittleFoxTeam.vscode-python-test-adapter
code --install-extension njpwerner.autodocstring

# FastAPI специфика
code --install-extension tomasz-smykowski.fastapi-snippets
code --install-extension tushortz.python-pydantic

# Контейнеризация и DevOps
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools
code --install-extension redhat.vscode-yaml
code --install-extension ms-vscode.makefile-tools

# Веб и API
code --install-extension humao.rest-client
code --install-extension rangav.vscode-thunder-client

# Документация
code --install-extension yzhang.markdown-all-in-one
code --install-extension bierner.markdown-mermaid

# Git
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph

# Качество кода
code --install-extension charliermarsh.ruff
code --install-extension esbenp.prettier-vscode

# Мониторинг
code --install-extension prometheus.promql
code --install-extension emilast.LogFileHighlighter

# PowerShell
code --install-extension ms-vscode.powershell

# Дополнительные утилиты
code --install-extension usernamehw.errorlens
code --install-extension wix.vscode-import-cost
code --install-extension formulahendry.code-runner
```

### Установка через VS Code UI:
1. Откройте VS Code
2. Нажмите `Ctrl+Shift+X` (Extensions)
3. Введите название расширения в поиск
4. Нажмите "Install"

## ⚙️ Настройки проекта

### Если папка `.vscode` не заблокирована:
1. Создайте папку `.vscode` в корне проекта
2. Скопируйте содержимое `vscode-recommended-settings.json` в `.vscode/settings.json`
3. Скопируйте содержимое `vscode-recommended-extensions.json` в `.vscode/extensions.json`

### Если папка `.vscode` заблокирована (как в этом проекте):
1. Используйте глобальные настройки VS Code
2. Или временно разрешите папку `.vscode` в `.codeassistantignore`

## 🐛 Конфигурация отладки

Создайте файл `.vscode/launch.json` (если папка не заблокирована):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI (auth-service)",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "apps.auth-service.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: FastAPI (cloud-reason)",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "apps.cloud-reason.cloud_reason.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8001"
      ],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests",
        "-v",
        "--no-header"
      ],
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Docker: Compose Up",
      "type": "docker",
      "request": "launch",
      "preLaunchTask": "docker-compose-up"
    }
  ]
}
```

## 🛠️ Полезные задачи (Tasks)

Создайте `.vscode/tasks.json` для автоматизации:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "docker-compose-up",
      "type": "shell",
      "command": "docker-compose up -d",
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "docker-compose-down",
      "type": "shell",
      "command": "docker-compose down",
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "run-tests",
      "type": "shell",
      "command": "pytest tests -v",
      "group": "test",
      "problemMatcher": []
    },
    {
      "label": "format-code",
      "type": "shell",
      "command": "black . && isort .",
      "group": "build",
      "problemMatcher": []
    }
  ]
}
```

## 🔧 Рекомендуемые настройки VS Code (глобальные)

Если не можете использовать `.vscode/settings.json`, настройте глобально:

1. `File` → `Preferences` → `Settings` (или `Ctrl+,`)
2. В поиске найдите нужные настройки:
   - `python.defaultInterpreterPath`: укажите путь к виртуальному окружению
   - `editor.formatOnSave`: включите
   - `python.formatting.provider`: выберите "black"
   - `python.linting.ruffEnabled`: включите

## 📝 Проверка установки

После установки расширений проверьте:

1. **Python**: Должна быть доступна отладка и автодополнение
2. **Docker**: В левой панели должна появиться иконка Docker
3. **GitLens**: В редакторе должны показываться аннотации коммитов
4. **REST Client**: Должна быть возможность создавать `.http` файлы для тестирования API

## 🚀 Быстрый старт

Для быстрой настройки выполните:

```bash
# Создайте скрипт установки
cat > install-vscode-extensions.sh << 'EOF'
#!/bin/bash
echo "Установка расширений VS Code..."
extensions=(
  "ms-python.python"
  "ms-python.vscode-pylance"
  "ms-azuretools.vscode-docker"
  "redhat.vscode-yaml"
  "eamodio.gitlens"
  "charliermarsh.ruff"
)

for ext in "${extensions[@]}"; do
  code --install-extension "$ext"
done
echo "Готово!"
EOF

chmod +x install-vscode-extensions.sh
./install-vscode-extensions.sh
```

## ❓ Поддержка

Если возникли проблемы:
1. Перезапустите VS Code после установки расширений
2. Проверьте, что Python интерпретатор выбран правильно
3. Убедитесь, что Docker запущен (для расширения Docker)
4. Проверьте логи расширений через `View` → `Output`
