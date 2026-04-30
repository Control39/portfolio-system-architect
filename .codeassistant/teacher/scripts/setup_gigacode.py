#!/usr/bin/env python3
"""
Скрипт для автоматической настройки GigaCode в VS Code
Автор: SourceCraft Code Assistant
Дата: 2026-04-10
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GigaCodeSetup:
    """Класс для настройки GigaCode в VS Code"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.vscode_dir = self.project_root / ".vscode"
        self.settings_file = self.vscode_dir / "settings.json"
        self.extensions_file = (
            self.project_root / "config" / "vscode" / "vscode-extensions.json"
        )

    def check_vscode_installed(self) -> bool:
        """Проверяет, установлен ли VS Code"""
        try:
            # Безопасный вызов без shell=True
            result = subprocess.run(
                ["code", "--version"], capture_output=True, text=True, shell=False
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    def check_gigacode_extension(self) -> Tuple[bool, str]:
        """Проверяет, установлено ли расширение GigaCode"""
        try:
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True,
                text=True,
                shell=False,
            )

            extensions = result.stdout.split("\n")
            gigacode_installed = "GigaCode.gigacode-vscode" in extensions

            if gigacode_installed:
                return True, "Расширение GigaCode установлено"
            else:
                return False, "Расширение GigaCode не установлено"

        except Exception as e:
            return False, f"Ошибка при проверке расширений: {str(e)}"

    def install_gigacode_extension(self) -> Tuple[bool, str]:
        """Устанавливает расширение GigaCode"""
        try:
            print("Установка расширения GigaCode...")

            result = subprocess.run(
                ["code", "--install-extension", "GigaCode.gigacode-vscode"],
                capture_output=True,
                text=True,
                shell=False,
            )

            if result.returncode == 0:
                return True, "Расширение GigaCode успешно установлено"
            else:
                return False, f"Ошибка при установке: {result.stderr}"

        except Exception as e:
            return False, f"Ошибка при установке расширения: {str(e)}"

    def load_current_settings(self) -> Dict:
        """Загружает текущие настройки VS Code"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def create_gigacode_config(self, api_key: Optional[str] = None) -> Dict:
        """Создает конфигурацию для GigaCode"""

        # Базовая конфигурация GigaCode
        gigacode_config = {
            "gigacode.enabled": True,
            "gigacode.model": "GigaChat",
            "gigacode.maxTokens": 4000,
            "gigacode.temperature": 0.7,
            "gigacode.enableCodeCompletion": True,
            "gigacode.enableChat": True,
            "gigacode.language": "ru",
            "gigacode.autoSuggest": True,
            "gigacode.suggestDelay": 300,
            "gigacode.contextWindow": 8000,
            # Настройки для конкретных языков
            "gigacode.python.enabled": True,
            "gigacode.typescript.enabled": True,
            "gigacode.javascript.enabled": True,
            "gigacode.yaml.enabled": True,
            "gigacode.markdown.enabled": True,
            # Интеграция с другими инструментами
            "gigacode.integrateWithCopilot": False,
            "gigacode.fallbackToSourceCraft": True,
            "gigacode.showTokenUsage": True,
            # Экономия токенов
            "gigacode.useForSimpleTasks": False,
            "gigacode.cacheResponses": True,
            "gigacode.dailyUsageLimit": 1000,
            # Уведомления
            "gigacode.notifyOnLowTokens": True,
            "gigacode.lowTokenThreshold": 50,
            "gigacode.notifyOnFallback": True,
        }

        # Добавляем API ключ, если он предоставлен
        if api_key:
            gigacode_config["gigacode.apiKey"] = api_key

        return gigacode_config

    def merge_settings(self, current_settings: Dict, gigacode_config: Dict) -> Dict:
        """Объединяет текущие настройки с конфигурацией GigaCode"""

        # Копируем текущие настройки
        merged = current_settings.copy()

        # Добавляем или обновляем настройки GigaCode
        for key, value in gigacode_config.items():
            merged[key] = value

        # Убедимся, что важные настройки проекта сохраняются
        important_settings = [
            "editor.defaultFormatter",
            "editor.formatOnSave",
            "files.autoSave",
            "python.analysis.typeCheckingMode",
            "cognitiveAgent.enabled",
        ]

        # Сохраняем важные настройки, если они уже есть
        for setting in important_settings:
            if setting in current_settings and setting not in merged:
                merged[setting] = current_settings[setting]

        return merged

    def save_settings(self, settings: Dict) -> bool:
        """Сохраняет настройки в файл"""
        try:
            # Создаем директорию .vscode, если её нет
            self.vscode_dir.mkdir(exist_ok=True)

            # Сохраняем настройки
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {str(e)}")
            return False

    def create_env_example(self) -> bool:
        """Создает пример файла .env с настройками GigaCode"""
        env_example = self.project_root / ".env.example"

        try:
            content = """# Настройки GigaCode
# Скопируйте этот файл в .env и заполните значения

# Токен GigaCode (получить на https://gigachat.cloud)
GIGACODE_API_KEY=ваш_токен_здесь

# Настройки модели
GIGACODE_MODEL=GigaChat
GIGACODE_MAX_TOKENS=4000
GIGACODE_TEMPERATURE=0.7

# Язык интерфейса
GIGACODE_LANGUAGE=ru

# Настройки для экономии токенов
GIGACODE_DAILY_LIMIT=1000
GIGACODE_USE_FOR_SIMPLE_TASKS=false

# Интеграция с SourceCraft
GIGACODE_FALLBACK_TO_SOURCECRAFT=true
"""

            with open(env_example, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Ошибка при создании .env.example: {str(e)}")
            return False

    def generate_setup_report(self, steps: List[Tuple[str, bool, str]]) -> str:
        """Генерирует отчет о настройке"""
        report_lines = [
            "=" * 60,
            "ОТЧЕТ О НАСТРОЙКЕ GIGACODE",
            "=" * 60,
            f"Дата: {platform.node()}",
            f"Проект: {self.project_root.name}",
            "",
        ]

        success_count = 0
        total_count = len(steps)

        for step_name, success, message in steps:
            status = "✅ УСПЕХ" if success else "❌ ОШИБКА"
            report_lines.append(f"{status}: {step_name}")
            report_lines.append(f"   {message}")
            report_lines.append("")

            if success:
                success_count += 1

        report_lines.append("=" * 60)
        report_lines.append(
            f"ИТОГ: {success_count}/{total_count} шагов выполнено успешно"
        )

        if success_count == total_count:
            report_lines.append("🎉 Настройка GigaCode завершена успешно!")
        elif success_count >= total_count * 0.7:
            report_lines.append("⚠️ Настройка завершена с предупреждениями")
        else:
            report_lines.append("❌ Настройка завершена с ошибками")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def run_setup(
        self, api_key: Optional[str] = None, auto_install: bool = True
    ) -> bool:
        """Запускает полную настройку GigaCode"""

        steps = []

        print("=" * 60)
        print("НАСТРОЙКА GIGACODE ДЛЯ VS CODE")
        print("=" * 60)

        # Шаг 1: Проверка VS Code
        print("\n1. Проверка установки VS Code...")
        vscode_installed = self.check_vscode_installed()
        steps.append(
            (
                "Проверка VS Code",
                vscode_installed,
                "VS Code установлен" if vscode_installed else "VS Code не найден",
            )
        )

        if not vscode_installed:
            print("❌ VS Code не установлен. Установите VS Code и повторите.")
            return False

        # Шаг 2: Проверка расширения GigaCode
        print("\n2. Проверка расширения GigaCode...")
        gigacode_installed, gigacode_msg = self.check_gigacode_extension()
        steps.append(("Проверка расширения GigaCode", gigacode_installed, gigacode_msg))

        # Шаг 3: Установка расширения (если нужно)
        if not gigacode_installed and auto_install:
            print("\n3. Установка расширения GigaCode...")
            install_success, install_msg = self.install_gigacode_extension()
            steps.append(
                ("Установка расширения GigaCode", install_success, install_msg)
            )

            if install_success:
                gigacode_installed = True
        elif not gigacode_installed:
            steps.append(
                (
                    "Установка расширения GigaCode",
                    False,
                    "Пропущено (auto_install=False)",
                )
            )

        if not gigacode_installed:
            print("❌ Расширение GigaCode не установлено.")
            print(
                "   Установите вручную: code --install-extension GigaCode.gigacode-vscode"
            )

        # Шаг 4: Загрузка текущих настроек
        print("\n4. Загрузка текущих настроек VS Code...")
        current_settings = self.load_current_settings()
        steps.append(
            (
                "Загрузка текущих настроек",
                True,
                f"Загружено {len(current_settings)} настроек",
            )
        )

        # Шаг 5: Создание конфигурации GigaCode
        print("\n5. Создание конфигурации GigaCode...")
        gigacode_config = self.create_gigacode_config(api_key)
        steps.append(
            (
                "Создание конфигурации GigaCode",
                True,
                f"Создано {len(gigacode_config)} настроек",
            )
        )

        # Шаг 6: Объединение настроек
        print("\n6. Объединение настроек...")
        merged_settings = self.merge_settings(current_settings, gigacode_config)
        steps.append(
            ("Объединение настроек", True, f"Итоговых настроек: {len(merged_settings)}")
        )

        # Шаг 7: Сохранение настроек
        print("\n7. Сохранение настроек...")
        save_success = self.save_settings(merged_settings)
        steps.append(
            (
                "Сохранение настроек",
                save_success,
                f"Сохранено в {self.settings_file}"
                if save_success
                else "Ошибка сохранения",
            )
        )

        # Шаг 8: Создание .env.example
        print("\n8. Создание .env.example...")
        env_success = self.create_env_example()
        steps.append(
            (
                "Создание .env.example",
                env_success,
                "Создан файл .env.example" if env_success else "Ошибка создания",
            )
        )

        # Генерация отчета
        print("\n" + "=" * 60)
        report = self.generate_setup_report(steps)
        print(report)

        # Сохранение отчета в файл
        report_file = (
            self.project_root
            / ".codeassistant"
            / "reports"
            / "gigacode_setup_report.md"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n📄 Отчет сохранен в: {report_file}")
        except Exception as e:
            print(f"\n⚠️ Не удалось сохранить отчет: {str(e)}")

        # Проверка успешности
        success_steps = sum(1 for _, success, _ in steps if success)
        return success_steps >= len(steps) * 0.8  # 80% успешных шагов


def main():
    """Основная функция"""

    # Парсинг аргументов командной строки
    import argparse

    parser = argparse.ArgumentParser(description="Настройка GigaCode для VS Code")

    parser.add_argument("--api-key", help="API ключ GigaCode (опционально)")

    parser.add_argument(
        "--no-auto-install",
        action="store_true",
        help="Не устанавливать расширение автоматически",
    )

    parser.add_argument(
        "--project-root", default=".", help="Корневая директория проекта"
    )

    args = parser.parse_args()

    # Создаем экземпляр настройщика
    setup = GigaCodeSetup(args.project_root)

    # Запускаем настройку
    success = setup.run_setup(
        api_key=args.api_key, auto_install=not args.no_auto_install
    )

    # Возвращаем код выхода
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
