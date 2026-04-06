#!/usr/bin/env python3
"""
Универсальный скрипт для установки расширений VS Code
Поддерживает конфигурацию для разных стеков технологий
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Any

class VSCodeExtensionInstaller:
    """Установщик расширений VS Code с поддержкой конфигураций стеков"""
    
    # Базовые расширения для всех проектов
    BASE_EXTENSIONS = [
        "eamodio.gitlens",           # Git enhancements
        "esbenp.prettier-vscode",    # Code formatter
        "yzhang.markdown-all-in-one", # Markdown support
        "usernamehw.errorlens",      # Error highlighting
    ]
    
    # Конфигурации стеков технологий
    TECH_STACKS = {
        "python": {
            "name": "Python Development",
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-python.isort",
                "njpwerner.autodocstring",
                "LittleFoxTeam.vscode-python-test-adapter",
                "charliermarsh.ruff",
            ]
        },
        "fastapi": {
            "name": "FastAPI Framework",
            "extensions": [
                "tomasz-smykowski.fastapi-snippets",
                "tushortz.python-pydantic",
            ],
            "requires": ["python"]
        },
        "docker": {
            "name": "Docker & Containers",
            "extensions": [
                "ms-azuretools.vscode-docker",
            ]
        },
        "kubernetes": {
            "name": "Kubernetes",
            "extensions": [
                "ms-kubernetes-tools.vscode-kubernetes-tools",
            ]
        },
        "devops": {
            "name": "DevOps Tools",
            "extensions": [
                "redhat.vscode-yaml",
                "ms-vscode.makefile-tools",
                "emilast.LogFileHighlighter",
            ]
        },
        "web": {
            "name": "Web Development",
            "extensions": [
                "humao.rest-client",
                "rangav.vscode-thunder-client",
                "bierner.markdown-mermaid",
            ]
        },
        "powershell": {
            "name": "PowerShell",
            "extensions": [
                "ms-vscode.powershell",
            ]
        },
        "monitoring": {
            "name": "Monitoring",
            "extensions": [
                "prometheus.promql",
            ]
        },
        "ai-ml": {
            "name": "AI/ML Development",
            "extensions": [
                "ms-toolsai.jupyter",
                "ms-toolsai.vscode-jupyter-cell-tags",
            ]
        },
        "java": {
            "name": "Java Development",
            "extensions": [
                "redhat.java",
                "vscjava.vscode-java-debug",
                "vscjava.vscode-java-test",
            ]
        },
        "javascript": {
            "name": "JavaScript/TypeScript",
            "extensions": [
                "dbaeumer.vscode-eslint",
                "christian-kohler.npm-intellisense",
                "ms-vscode.vscode-typescript-next",
            ]
        },
        "go": {
            "name": "Go Development",
            "extensions": [
                "golang.go",
            ]
        },
        "rust": {
            "name": "Rust Development",
            "extensions": [
                "rust-lang.rust-analyzer",
            ]
        }
    }
    
    # Предустановленные конфигурации для популярных стеков
    PRESET_CONFIGS = {
        "portfolio-system-architect": ["python", "fastapi", "docker", "kubernetes", "devops", "web", "powershell", "monitoring"],
        "python-backend": ["python", "fastapi", "docker", "devops"],
        "web-fullstack": ["python", "javascript", "docker", "devops", "web"],
        "ai-ml-pipeline": ["python", "ai-ml", "docker", "devops"],
        "microservices": ["python", "docker", "kubernetes", "devops", "web"],
        "devops-tools": ["docker", "kubernetes", "devops", "powershell"],
    }
    
    def __init__(self):
        self.installed_extensions = self._get_installed_extensions()
        
    def _get_installed_extensions(self) -> List[str]:
        """Получить список уже установленных расширений"""
        try:
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True,
                text=True,
                check=True
            )
            return [ext.strip() for ext in result.stdout.splitlines() if ext.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  VS Code CLI (code) не найден. Убедитесь, что VS Code добавлен в PATH.")
            print("   Инструкция: https://code.visualstudio.com/docs/setup/mac#_launching-from-the-command-line")
            return []
    
    def install_extension(self, extension_id: str) -> bool:
        """Установить одно расширение"""
        if extension_id in self.installed_extensions:
            print(f"  ✓ {extension_id} (уже установлено)")
            return True
            
        print(f"  → Устанавливаю {extension_id}...")
        try:
            subprocess.run(
                ["code", "--install-extension", extension_id],
                check=True,
                capture_output=True,
                text=True
            )
            self.installed_extensions.append(extension_id)
            print(f"  ✓ {extension_id} (установлено)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Ошибка установки {extension_id}: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"  ✗ VS Code CLI не найден. Не могу установить {extension_id}")
            return False
    
    def install_stack(self, stack_name: str) -> bool:
        """Установить стек технологий"""
        if stack_name not in self.TECH_STACKS:
            print(f"✗ Неизвестный стек: {stack_name}")
            print(f"  Доступные стеки: {', '.join(self.TECH_STACKS.keys())}")
            return False
            
        stack = self.TECH_STACKS[stack_name]
        print(f"\n📦 Установка стека: {stack['name']} ({stack_name})")
        
        # Установить зависимости
        if "requires" in stack:
            for req in stack["requires"]:
                if not self.install_stack(req):
                    return False
        
        # Установить расширения стека
        success = True
        for ext in stack["extensions"]:
            if not self.install_extension(ext):
                success = False
                
        return success
    
    def install_preset(self, preset_name: str) -> bool:
        """Установить предустановленную конфигурацию"""
        if preset_name not in self.PRESET_CONFIGS:
            print(f"✗ Неизвестная предустановка: {preset_name}")
            print(f"  Доступные предустановки: {', '.join(self.PRESET_CONFIGS.keys())}")
            return False
            
        print(f"\n🎯 Установка предустановки: {preset_name}")
        print(f"  Стеки: {', '.join(self.PRESET_CONFIGS[preset_name])}")
        
        success = True
        for stack in self.PRESET_CONFIGS[preset_name]:
            if not self.install_stack(stack):
                success = False
                
        return success
    
    def install_custom(self, extensions: List[str]) -> bool:
        """Установить пользовательский список расширений"""
        print(f"\n🔧 Установка пользовательских расширений ({len(extensions)} шт.)")
        
        success = True
        for ext in extensions:
            if not self.install_extension(ext):
                success = False
                
        return success
    
    def generate_config_file(self, stacks: List[str], output_path: str = "vscode-extensions-config.json"):
        """Сгенерировать файл конфигурации для быстрой установки"""
        all_extensions = set(self.BASE_EXTENSIONS)
        
        for stack_name in stacks:
            if stack_name in self.TECH_STACKS:
                stack = self.TECH_STACKS[stack_name]
                all_extensions.update(stack["extensions"])
                
                # Добавить зависимости
                if "requires" in stack:
                    for req in stack["requires"]:
                        if req in self.TECH_STACKS:
                            all_extensions.update(self.TECH_STACKS[req]["extensions"])
        
        config = {
            "stacks": stacks,
            "extensions": sorted(list(all_extensions)),
            "install_command": "code --install-extension " + " --install-extension ".join(sorted(list(all_extensions)))
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Файл конфигурации создан: {output_path}")
        print(f"  Расширений: {len(all_extensions)}")
        print(f"  Стеки: {', '.join(stacks)}")
        
        return list(all_extensions)
    
    def detect_project_stack(self, project_path: str = ".") -> List[str]:
        """Автоматически определить стек технологий проекта"""
        detected_stacks = []
        path = Path(project_path)
        
        # Проверка файлов проекта
        if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
            detected_stacks.append("python")
            
            # Проверка на FastAPI
            if (path / "main.py").exists():
                with open(path / "main.py", 'r') as f:
                    content = f.read()
                    if "fastapi" in content.lower() or "FastAPI" in content:
                        detected_stacks.append("fastapi")
            
            # Проверка на AI/ML
            if (path / "requirements.txt").exists():
                with open(path / "requirements.txt", 'r') as f:
                    content = f.read()
                    if any(x in content.lower() for x in ["tensorflow", "pytorch", "scikit-learn", "jupyter"]):
                        detected_stacks.append("ai-ml")
        
        if (path / "Dockerfile").exists() or (path / "docker-compose.yml").exists():
            detected_stacks.append("docker")
            
        if (path / "deployment").exists() and any((path / "deployment").glob("*.yaml")):
            detected_stacks.append("kubernetes")
            
        if (path / "package.json").exists():
            detected_stacks.append("javascript")
            
        if any(path.glob("*.ps1")) or any(path.glob("*.psm1")):
            detected_stacks.append("powershell")
            
        if (path / "prometheus.yml").exists() or (path / "grafana").exists():
            detected_stacks.append("monitoring")
            
        return list(set(detected_stacks))

def main():
    """Основная функция"""
    installer = VSCodeExtensionInstaller()
    
    print("=" * 60)
    print("🚀 Универсальный установщик расширений VS Code")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Режим командной строки
        command = sys.argv[1]
        
        if command == "preset":
            if len(sys.argv) > 2:
                preset = sys.argv[2]
                installer.install_preset(preset)
            else:
                print("Доступные предустановки:")
                for preset in installer.PRESET_CONFIGS:
                    print(f"  {preset}: {', '.join(installer.PRESET_CONFIGS[preset])}")
                    
        elif command == "stack":
            if len(sys.argv) > 2:
                for stack in sys.argv[2:]:
                    installer.install_stack(stack)
            else:
                print("Доступные стеки:")
                for stack_name, stack_info in installer.TECH_STACKS.items():
                    print(f"  {stack_name}: {stack_info['name']}")
                    
        elif command == "detect":
            stacks = installer.detect_project_stack()
            print(f"\n🔍 Обнаруженные стеки: {', '.join(stacks) if stacks else 'не обнаружено'}")
            if stacks:
                response = input("Установить обнаруженные стеки? (y/n): ")
                if response.lower() == 'y':
                    for stack in stacks:
                        installer.install_stack(stack)
                        
        elif command == "generate":
            if len(sys.argv) > 2:
                stacks = sys.argv[2:]
                installer.generate_config_file(stacks)
            else:
                print("Укажите стеки для генерации конфигурации")
                print("Пример: python setup-vscode-extensions.py generate python docker devops")
                
        elif command == "custom":
            if len(sys.argv) > 2:
                extensions = sys.argv[2:]
                installer.install_custom(extensions)
            else:
                print("Укажите расширения для установки")
                print("Пример: python setup-vscode-extensions.py custom ms-python.python ms-azuretools.vscode-docker")
                
        else:
            print(f"Неизвестная команда: {command}")
            
    else:
        # Интерактивный режим
        print("\nВыберите режим работы:")
        print("1. Установить предустановленную конфигурацию")
        print("2. Установить отдельные стеки технологий")
        print("3. Автоматически определить стек проекта")
        print("4. Сгенерировать файл конфигурации")
        print("5. Установить базовые расширения")
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == "1":
            print("\nДоступные предустановки:")
            for i, (preset, stacks) in enumerate(installer.PRESET_CONFIGS.items(), 1):
                print(f"  {i}. {preset} ({', '.join(stacks)})")
                
            preset_choice = input("\nВыберите предустановку (номер или название): ").strip()
            
            if preset_choice.isdigit():
                preset_idx = int(preset_choice) - 1
                if 0 <= preset_idx < len(installer.PRESET_CONFIGS):
                    preset_name = list(installer.PRESET_CONFIGS.keys())[preset_idx]
                    installer.install_preset(preset_name)
                else:
                    print("Неверный номер")
            else:
                installer.install_preset(preset_choice)
                
        elif choice == "2":
            print("\nДоступные стеки технологий:")
            for stack_name, stack_info in installer.TECH_STACKS.items():
                print(f"  {stack_name}: {stack_info['name']}")
                
            stacks_input = input("\nВведите стеки через пробел: ").strip()
            stacks = stacks_input.split()
            
            for stack in stacks:
                installer.install_stack(stack)
                
        elif choice == "3":
            stacks = installer.detect_project_stack()
            print(f"\n🔍 Обнаруженные стеки: {', '.join(stacks) if stacks else 'не обнаружено'}")
            
            if stacks:
                response = input("\nУстановить обнаруженные стеки? (y/n): ")
                if response.lower() == 'y':
                    for stack in stacks:
                        installer.install_stack(stack)
                        
        elif choice == "4":
            print("\nДоступные стеки технологий:")
            for stack_name, stack_info in installer.TECH_STACKS.items():
                print(f"  {stack_name}: {stack_info['name']}")
                
            stacks_input = input("\nВведите стеки для конфигурации через пробел: ").strip()
            stacks = stacks_input.split()
            
            output_file = input("Имя выходного файла (по умолчанию: vscode-extensions-config.json): ").strip()
            if not output_file:
                output_file = "vscode-extensions-config.json"
                
            installer.generate_config_file(stacks, output_file)
            
        elif choice == "5":
            print("\n📦 Установка базовых расширений...")
            installer.install_custom(installer.BASE_EXTENSIONS)
            
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()
