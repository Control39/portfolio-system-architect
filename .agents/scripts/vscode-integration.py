#!/usr/bin/env python3
"""Интеграция Cognitive Automation Agent с VS Code.
Обеспечивает автоматический запуск агента при открытии проекта,
команды для палитры команд и уведомления.
"""

import json
import os
from pathlib import Path
from typing import Any


class VSCodeIntegration:
    """Интеграция с VS Code"""

    def __init__(self, agent_root: str = ".agents"):
        self.agent_root = Path(agent_root)
        self.vscode_dir = Path(".vscode")
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Загрузка конфигурации"""
        config_path = self.agent_root / "config" / "agent-config.yaml"
        if config_path.exists():
            try:
                import yaml
                with open(config_path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except:
                pass
        return {}

    def setup_vscode_integration(self) -> bool:
        """Настройка интеграции с VS Code"""
        print("🔧 Настройка интеграции с VS Code...")

        try:
            # Создаем задачи для VS Code
            self._create_vscode_tasks()

            # Создаем настройки для VS Code
            self._create_vscode_settings()

            # Создаем сниппеты
            self._create_vscode_snippets()

            # Создаем скрипт активации
            self._create_activation_script()

            print("✅ Интеграция с VS Code настроена")
            return True

        except Exception as e:
            print(f"❌ Ошибка настройки интеграции: {e}")
            return False

    def _create_vscode_tasks(self):
        """Создание задач для VS Code"""
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Cognitive Agent: Активировать",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/.agents/launch-script.py",
                        "--autonomy=medium",
                    ],
                    "group": {
                        "kind": "build",
                        "isDefault": False,
                    },
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated",
                    },
                    "problemMatcher": [],
                },
                {
                    "label": "Cognitive Agent: Сканировать проект",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/.agents/launch-script.py",
                        "--scan",
                    ],
                    "group": "build",
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated",
                    },
                },
                {
                    "label": "Cognitive Agent: Валидировать",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/.agents/tests/validation-test.py",
                    ],
                    "group": "test",
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated",
                    },
                },
                {
                    "label": "Cognitive Agent: Оптимизировать",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/.agents/launch-script.py",
                        "--optimize",
                    ],
                    "group": "build",
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated",
                    },
                },
                {
                    "label": "Cognitive Agent: Показать дашборд",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/.agents/launch-script.py",
                        "--dashboard",
                    ],
                    "group": "build",
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated",
                    },
                },
            ],
        }

        # Создаем директорию .vscode если её нет
        self.vscode_dir.mkdir(exist_ok=True)

        tasks_file = self.vscode_dir / "tasks.json"
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)

        print(f"📋 Созданы задачи VS Code: {tasks_file}")

    def _create_vscode_settings(self):
        """Создание настроек для VS Code"""
        settings = {
            "cognitiveAgent.enabled": True,
            "cognitiveAgent.autoActivate": True,
            "cognitiveAgent.autonomyLevel": "medium",
            "cognitiveAgent.notifications": True,
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 1000,
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll": "explicit",
                "source.organizeImports": "explicit",
            },
            "python.analysis.autoImportCompletions": True,
            "python.analysis.typeCheckingMode": "basic",
            "terminal.integrated.env.windows": {
                "COGNITIVE_AGENT_ENABLED": "true",
                "COGNITIVE_AGENT_PATH": "${workspaceFolder}/.agents",
            },
        }

        settings_file = self.vscode_dir / "settings.json"

        # Если файл уже существует, объединяем настройки
        if settings_file.exists():
            try:
                with open(settings_file, encoding="utf-8") as f:
                    existing_settings = json.load(f)
                # Объединяем настройки
                settings = {**existing_settings, **settings}
            except:
                pass

        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        print(f"⚙️  Созданы настройки VS Code: {settings_file}")

    def _create_vscode_snippets(self):
        """Создание сниппетов для VS Code"""
        snippets = {
            "Cognitive Agent Activation": {
                "prefix": "cog-activate",
                "body": [
                    "# Активация Cognitive Automation Agent",
                    "from agents.cognitive_agent import CognitiveAgent",
                    "",
                    "agent = CognitiveAgent(autonomy_level='${1|high,medium,low|}')",
                    "agent.activate()",
                    "agent.scan_project()",
                    "agent.generate_plan()",
                ],
                "description": "Активация Cognitive Automation Agent",
            },
            "Cognitive Agent Scan": {
                "prefix": "cog-scan",
                "body": [
                    "# Сканирование проекта Cognitive Agent",
                    "from agents.scanner import ProjectScanner",
                    "",
                    "scanner = ProjectScanner()",
                    "report = scanner.scan(deep=${1|True,False|})",
                    "scanner.save_report('scan_report.json')",
                ],
                "description": "Сканирование проекта",
            },
            "Cognitive Agent Task": {
                "prefix": "cog-task",
                "body": [
                    "# Создание задачи для Cognitive Agent",
                    "from agents.planner import TaskPlanner",
                    "",
                    "planner = TaskPlanner()",
                    "task = planner.create_task(",
                    "    name='${1:task_name}',",
                    "    description='${2:task_description}',",
                    "    priority='${3|critical,high,medium,low|}',",
                    "    estimated_time=${4:60}",
                    ")",
                    "planner.add_to_queue(task)",
                ],
                "description": "Создание задачи",
            },
        }

        snippets_file = self.vscode_dir / "cognitive-agent.code-snippets"
        with open(snippets_file, "w", encoding="utf-8") as f:
            json.dump(snippets, f, indent=2)

        print(f"📝 Созданы сниппеты VS Code: {snippets_file}")

    def _create_activation_script(self):
        """Создание скрипта активации для VS Code"""
        script_content = '''#!/usr/bin/env python3
"""
Скрипт активации Cognitive Automation Agent для VS Code.
Запускается автоматически при открытии проекта.
"""

import os
import sys
from pathlib import Path

def activate_cognitive_agent():
    """Активация Cognitive Automation Agent"""
    agent_path = Path(".agents")
    
    if not agent_path.exists():
        print("❌ Директория .agents не найдена")
        return False
    
    # Проверяем конфигурацию
    config_path = agent_path / "config" / "agent-config.yaml"
    if not config_path.exists():
        print("❌ Конфигурационный файл не найден")
        return False
    
    # Запускаем валидацию
    validation_script = agent_path / "tests" / "validation-test.py"
    if validation_script.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(validation_script)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Cognitive Agent прошел валидацию")
            
            # Запускаем сканирование если автоактивация включена
            launch_script = agent_path / "launch-script.py"
            if launch_script.exists():
                subprocess.Popen(
                    [sys.executable, str(launch_script), "--trigger=project_open"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("🚀 Cognitive Agent активирован")
                return True
        else:
            print("⚠️  Cognitive Agent требует настройки")
            print(result.stdout)
    
    return False

if __name__ == "__main__":
    # Проверяем, запущено ли в VS Code
    vs_code_env = os.environ.get("VSCODE_PID") or os.environ.get("TERM_PROGRAM") == "vscode"
    
    if vs_code_env:
        print("🔍 Обнаружена среда VS Code")
        activate_cognitive_agent()
    else:
        print("📁 Запуск вне VS Code, активация пропущена")
'''

        script_file = self.agent_root / "scripts" / "vscode-activate.py"
        script_file.parent.mkdir(exist_ok=True, parents=True)

        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Делаем скрипт исполняемым (для Unix-систем)
        if os.name != "nt":
            os.chmod(script_file, 0o755)

        print(f"🚀 Создан скрипт активации: {script_file}")

    def create_launch_configuration(self):
        """Создание конфигурации запуска для отладки"""
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Cognitive Agent: Debug",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/.agents/launch-script.py",
                    "args": ["--debug"],
                    "console": "integratedTerminal",
                    "justMyCode": False,
                },
                {
                    "name": "Cognitive Agent: Validate",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/.agents/tests/validation-test.py",
                    "console": "integratedTerminal",
                },
                {
                    "name": "Cognitive Agent: Scanner",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/.agents/launch-script.py",
                    "args": ["--scan", "--deep"],
                    "console": "integratedTerminal",
                },
            ],
        }

        launch_file = self.vscode_dir / "launch.json"

        # Если файл уже существует, добавляем конфигурации
        if launch_file.exists():
            try:
                with open(launch_file, encoding="utf-8") as f:
                    existing_config = json.load(f)

                # Добавляем наши конфигурации в начало
                if "configurations" in existing_config:
                    existing_config["configurations"] = launch_config["configurations"] + existing_config["configurations"]
                else:
                    existing_config["configurations"] = launch_config["configurations"]

                launch_config = existing_config
            except:
                pass

        with open(launch_file, "w", encoding="utf-8") as f:
            json.dump(launch_config, f, indent=2)

        print(f"🐛 Созданы конфигурации запуска: {launch_file}")

    def run(self):
        """Запуск интеграции"""
        print("=" * 60)
        print("🚀 ИНТЕГРАЦИЯ COGNITIVE AUTOMATION AGENT С VS CODE")
        print("=" * 60)

        success = self.setup_vscode_integration()

        if success:
            print("\n✅ Интеграция успешно настроена!")
            print("\nДоступные команды в VS Code:")
            print("1. Ctrl+Shift+P → 'Tasks: Run Task' → Выберите Cognitive Agent задачу")
            print("2. Используйте сниппеты: cog-activate, cog-scan, cog-task")
            print("3. Автоматическая активация при открытии проекта")
            print("\nФайлы конфигурации созданы в директории .vscode/")
        else:
            print("\n❌ Настройка интеграции завершилась с ошибками")

        return success

def main():
    """Основная функция"""
    integration = VSCodeIntegration()
    integration.run()

if __name__ == "__main__":
    main()
