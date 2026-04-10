#!/usr/bin/env python3
"""
Система автоматизации управления расширениями VS Code
Автоматическая установка, проверка и синхронизация расширений
"""

import json
import subprocess
import sys
import os
import platform
from pathlib import Path
from typing import List, Dict, Set, Optional
import argparse
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VSCodeExtensionManager:
    """Менеджер расширений VS Code"""
    
    def __init__(self, config_path: str = "config/vscode/vscode-extensions.json"):
        self.config_path = Path(config_path)
        self.system = platform.system()
        self.code_cmd = self._detect_code_command()
        
        # Загружаем конфигурацию
        self.config = self._load_config()
        
    def _detect_code_command(self) -> str:
        """Определяет команду для VS Code"""
        if self.system == "Windows":
            # Пробуем разные варианты для Windows
            code_paths = [
                "C:\\Users\\Z\\AppData\\Local\\Programs\\Microsoft VS Code\\bin\\code.cmd",
                "code",
                "code.cmd",
                "code.exe"
            ]
            for cmd in code_paths:
                try:
                    result = subprocess.run([cmd, "--version"], 
                                         capture_output=True, check=False, shell=True)
                    if result.returncode == 0:
                        return cmd
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
        else:
            # Linux/macOS
            try:
                subprocess.run(["code", "--version"], 
                             capture_output=True, check=False, shell=True)
                return "code"
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
        logger.warning("VS Code не найден в PATH. Используем 'code' как команду по умолчанию.")
        return "code"
    
    def _load_config(self) -> Dict:
        """Загружает конфигурацию расширений"""
        if not self.config_path.exists():
            logger.error(f"Конфигурационный файл не найден: {self.config_path}")
            return {
                "required": [],
                "recommended": [],
                "optional": [],
                "excluded": []
            }
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка чтения конфигурации: {e}")
            return {
                "required": [],
                "recommended": [],
                "optional": [],
                "excluded": []
            }
    
    def get_installed_extensions(self) -> List[str]:
        """Получает список установленных расширений"""
        try:
            result = subprocess.run(
                [self.code_cmd, "--list-extensions"],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            extensions = [ext.strip() for ext in result.stdout.split('\n') if ext.strip()]
            logger.info(f"Найдено {len(extensions)} установленных расширений")
            return extensions
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка получения списка расширений: {e}")
            return []
        except FileNotFoundError:
            logger.error(f"Команда '{self.code_cmd}' не найдена")
            return []
    
    def install_extension(self, extension_id: str) -> bool:
        """Устанавливает расширение"""
        logger.info(f"Установка расширения: {extension_id}")
        try:
            result = subprocess.run(
                [self.code_cmd, "--install-extension", extension_id],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            logger.info(f"Расширение {extension_id} успешно установлено")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка установки {extension_id}: {e.stderr}")
            return False
    
    def uninstall_extension(self, extension_id: str) -> bool:
        """Удаляет расширение"""
        logger.info(f"Удаление расширения: {extension_id}")
        try:
            result = subprocess.run(
                [self.code_cmd, "--uninstall-extension", extension_id],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            logger.info(f"Расширение {extension_id} успешно удалено")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка удаления {extension_id}: {e.stderr}")
            return False
    
    def check_compliance(self) -> Dict:
        """Проверяет соответствие установленных расширений конфигурации"""
        installed = set(self.get_installed_extensions())
        
        # Получаем все расширения из конфигурации
        required = set(self.config.get("required", []))
        recommended = set(self.config.get("recommended", []))
        optional = set(self.config.get("optional", []))
        excluded = set(self.config.get("excluded", []))
        
        all_configured = required.union(recommended).union(optional)
        
        # Анализ
        missing_required = required - installed
        missing_recommended = recommended - installed
        installed_excluded = installed.intersection(excluded)
        extra_extensions = installed - all_configured - excluded
        
        return {
            "installed_count": len(installed),
            "required_count": len(required),
            "recommended_count": len(recommended),
            "missing_required": list(missing_required),
            "missing_recommended": list(missing_recommended),
            "installed_excluded": list(installed_excluded),
            "extra_extensions": list(extra_extensions),
            "compliance_score": self._calculate_compliance_score(
                len(installed), 
                len(required), 
                len(missing_required),
                len(installed_excluded)
            )
        }
    
    def _calculate_compliance_score(self, installed: int, required: int, 
                                   missing_required: int, excluded: int) -> float:
        """Рассчитывает оценку соответствия"""
        if required == 0:
            return 100.0
        
        # Штраф за отсутствующие обязательные расширения
        required_score = ((required - missing_required) / required) * 70
        
        # Штраф за установленные исключенные расширения
        excluded_penalty = min(excluded * 10, 30)
        
        return max(0, required_score - excluded_penalty)
    
    def sync_extensions(self, dry_run: bool = False) -> Dict:
        """Синхронизирует расширения с конфигурацией"""
        compliance = self.check_compliance()
        actions = {
            "installed": [],
            "uninstalled": [],
            "failed": []
        }
        
        if not dry_run:
            # Устанавливаем отсутствующие обязательные расширения
            for ext in compliance["missing_required"]:
                if self.install_extension(ext):
                    actions["installed"].append(ext)
                else:
                    actions["failed"].append(f"install:{ext}")
            
            # Удаляем исключенные расширения
            for ext in compliance["installed_excluded"]:
                if self.uninstall_extension(ext):
                    actions["uninstalled"].append(ext)
                else:
                    actions["failed"].append(f"uninstall:{ext}")
        
        return {
            "compliance_before": compliance,
            "actions": actions,
            "dry_run": dry_run
        }
    
    def generate_report(self, compliance_data: Dict) -> str:
        """Генерирует отчет о соответствии"""
        report = []
        report.append("=" * 60)
        report.append("ОТЧЕТ О СООТВЕТСТВИИ РАСШИРЕНИЙ VS CODE")
        report.append("=" * 60)
        report.append(f"Установлено расширений: {compliance_data['installed_count']}")
        report.append(f"Обязательных расширений: {compliance_data['required_count']}")
        report.append(f"Рекомендуемых расширений: {compliance_data['recommended_count']}")
        report.append(f"Оценка соответствия: {compliance_data['compliance_score']:.1f}%")
        report.append("")
        
        if compliance_data['missing_required']:
            report.append("❌ ОТСУТСТВУЮТ ОБЯЗАТЕЛЬНЫЕ РАСШИРЕНИЯ:")
            for ext in compliance_data['missing_required']:
                report.append(f"  - {ext}")
            report.append("")
        
        if compliance_data['missing_recommended']:
            report.append("⚠️  ОТСУТСТВУЮТ РЕКОМЕНДУЕМЫЕ РАСШИРЕНИЯ:")
            for ext in compliance_data['missing_recommended']:
                report.append(f"  - {ext}")
            report.append("")
        
        if compliance_data['installed_excluded']:
            report.append("🚫 УСТАНОВЛЕНЫ ИСКЛЮЧЕННЫЕ РАСШИРЕНИЯ:")
            for ext in compliance_data['installed_excluded']:
                report.append(f"  - {ext}")
            report.append("")
        
        if compliance_data['extra_extensions']:
            report.append("ℹ️  ДОПОЛНИТЕЛЬНЫЕ РАСШИРЕНИЯ (не в конфигурации):")
            for ext in compliance_data['extra_extensions']:
                report.append(f"  - {ext}")
        
        report.append("=" * 60)
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Менеджер расширений VS Code")
    parser.add_argument("--action", choices=["check", "sync", "report"],
                       default="check", help="Действие (по умолчанию: check)")
    parser.add_argument("--dry-run", action="store_true", help="Показать изменения без применения")
    parser.add_argument("--config", default="config/vscode/vscode-extensions.json",
                       help="Путь к конфигурационному файлу")
    parser.add_argument("--output-score", action="store_true",
                       help="Вывести только оценку соответствия (для CI/CD)")
    parser.add_argument("--threshold", type=float, default=80.0,
                       help="Минимальный порог соответствия (по умолчанию: 80%%)")
    
    args = parser.parse_args()
    
    manager = VSCodeExtensionManager(args.config)
    
    if args.action == "check" or (args.action == "check" and not args.output_score):
        # Проверка соответствия
        compliance = manager.check_compliance()
        
        if args.output_score:
            # Режим CI/CD: выводим только оценку
            print(f"{compliance['compliance_score']:.1f}")
        else:
            # Обычный режим: полный отчет
            print(manager.generate_report(compliance))
            
            # Рекомендации
            if compliance['compliance_score'] < args.threshold:
                print(f"\n💡 РЕКОМЕНДАЦИИ (оценка ниже {args.threshold}%%):")
                print("Запустите 'python scripts/vscode-extensions-manager.py --action sync' для синхронизации")
    
    elif args.action == "sync":
        # Синхронизация расширений
        result = manager.sync_extensions(args.dry_run)
        print("=" * 60)
        print("РЕЗУЛЬТАТ СИНХРОНИЗАЦИИ")
        print("=" * 60)
        
        if args.dry_run:
            print("РЕЖИМ ПРОСМОТРА (изменения не применены)")
        
        if result['actions']['installed']:
            print("\n📦 БУДУТ УСТАНОВЛЕНЫ:")
            for ext in result['actions']['installed']:
                print(f"  + {ext}")
        
        if result['actions']['uninstalled']:
            print("\n🗑️  БУДУТ УДАЛЕНЫ:")
            for ext in result['actions']['uninstalled']:
                print(f"  - {ext}")
        
        if result['actions']['failed']:
            print("\n❌ ОШИБКИ:")
            for err in result['actions']['failed']:
                print(f"  ! {err}")
        
        if not args.dry_run:
            print("\n✅ Синхронизация завершена")
            # Показываем итоговый отчет
            new_compliance = manager.check_compliance()
            print(manager.generate_report(new_compliance))
    
    elif args.action == "report":
        # Генерация отчета в файл
        compliance = manager.check_compliance()
        report_file = "vscode-extensions-compliance-report.md"
        
        report_content = f"""# VS Code Extensions Compliance Report

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Конфигурация:** {args.config}

## Результаты проверки

{manager.generate_report(compliance).replace('=', '#')}

## Детали

- **Всего установлено:** {compliance['installed_count']}
- **Обязательных расширений:** {compliance['required_count']}
- **Рекомендуемых расширений:** {compliance['recommended_count']}
- **Оценка соответствия:** {compliance['compliance_score']:.1f}%

## Рекомендации

1. Установите отсутствующие обязательные расширения
2. Удалите исключенные расширения
3. Рассмотрите установку рекомендуемых расширений

## Команды для исправления

\`\`\`bash
# Проверить соответствие
python scripts/vscode-extensions-manager.py --action check

# Синхронизировать расширения
python scripts/vscode-extensions-manager.py --action sync

# Предварительный просмотр изменений
python scripts/vscode-extensions-manager.py --action sync --dry-run
\`\`\`

---

*Этот отчет сгенерирован автоматически системой управления расширениями VS Code.*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Отчет сохранен в {report_file}")


if __name__ == "__main__":
    main()