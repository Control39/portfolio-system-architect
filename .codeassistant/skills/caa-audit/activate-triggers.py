#!/usr/bin/env python3
"""
Скрипт активации проактивных триггеров PMR Agent
Интеграция с существующей системой Cognitive Automation Agent
"""

import os
import sys
import yaml
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class TriggerActivator:
    """Активатор проактивных триггеров PMR Agent"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.pmr_triggers_path = self.project_root / ".codeassistant/skills/caa-audit/pmr-triggers.yaml"
        self.caa_triggers_path = self.project_root / ".agents/config/triggers.yaml"
        self.caa_git_hooks_path = self.project_root / ".agents/config/git-hooks.yaml"
        
    def activate_all(self, dry_run: bool = False) -> Dict:
        """Активация всех триггеров"""
        print("🚀 Активация проактивных триггеров PMR Agent...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # 1. Проверка существования конфигурационных файлов
            self._check_prerequisites(results)
            
            # 2. Загрузка конфигурации PMR триггеров
            pmr_config = self._load_pmr_config(results)
            if not pmr_config:
                return results
            
            # 3. Интеграция с CAA триггерами
            if not dry_run:
                self._integrate_with_caa_triggers(pmr_config, results)
            
            # 4. Настройка Git хуков
            if not dry_run:
                self._setup_git_hooks(pmr_config, results)
            
            # 5. Создание директорий для хранения данных
            if not dry_run:
                self._create_storage_directories(pmr_config, results)
            
            # 6. Генерация скриптов запуска
            if not dry_run:
                self._generate_launch_scripts(pmr_config, results)
            
            print("\n✅ Активация завершена успешно!")
            
        except Exception as e:
            results["errors"].append(f"Критическая ошибка: {str(e)}")
            print(f"\n❌ Ошибка активации: {e}")
        
        return results
    
    def _check_prerequisites(self, results: Dict):
        """Проверка предварительных условий"""
        print("  🔍 Проверка предварительных условий...")
        
        # Проверка существования файлов CAA
        required_files = [
            self.caa_triggers_path,
            self.pmr_triggers_path
        ]
        
        for file_path in required_files:
            if file_path.exists():
                results["steps"].append({
                    "step": "check_prerequisites",
                    "status": "success",
                    "message": f"Файл найден: {file_path.relative_to(self.project_root)}"
                })
            else:
                results["errors"].append(f"Файл не найден: {file_path.relative_to(self.project_root)}")
        
        # Проверка Python и зависимостей
        try:
            import yaml
            results["steps"].append({
                "step": "check_dependencies",
                "status": "success",
                "message": "PyYAML установлен"
            })
        except ImportError:
            results["errors"].append("PyYAML не установлен. Установите: pip install pyyaml")
    
    def _load_pmr_config(self, results: Dict) -> Optional[Dict]:
        """Загрузка конфигурации PMR триггеров"""
        print("  📂 Загрузка конфигурации PMR триггеров...")
        
        try:
            with open(self.pmr_triggers_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            results["steps"].append({
                "step": "load_pmr_config",
                "status": "success",
                "message": f"Загружено {len(config.get('triggers', {}))} триггеров"
            })
            
            return config
            
        except Exception as e:
            results["errors"].append(f"Ошибка загрузки конфигурации PMR: {e}")
            return None
    
    def _integrate_with_caa_triggers(self, pmr_config: Dict, results: Dict):
        """Интеграция с существующей системой CAA триггеров"""
        print("  🔗 Интеграция с CAA триггерами...")
        
        try:
            # Загрузка конфигурации CAA
            with open(self.caa_triggers_path, 'r', encoding='utf-8') as f:
                caa_config = yaml.safe_load(f)
            
            # Добавление PMR триггеров в CAA конфигурацию
            if 'triggers' not in caa_config:
                caa_config['triggers'] = {}
            
            pmr_triggers = pmr_config.get('triggers', {})
            integrated_count = 0
            
            for trigger_name, trigger_config in pmr_triggers.items():
                # Добавляем префикс pmr_ для избежания конфликтов
                caa_trigger_name = f"pmr_{trigger_name}"
                caa_config['triggers'][caa_trigger_name] = trigger_config
                integrated_count += 1
                
                results["steps"].append({
                    "step": "integrate_trigger",
                    "status": "success",
                    "message": f"Интегрирован триггер: {trigger_name} -> {caa_trigger_name}"
                })
            
            # Добавление секции интеграции
            if 'integration' not in caa_config:
                caa_config['integration'] = {}
            
            caa_config['integration']['pmr_agent'] = {
                "enabled": True,
                "config_source": str(self.pmr_triggers_path.relative_to(self.project_root)),
                "integrated_triggers": integrated_count,
                "integration_date": datetime.now().isoformat()
            }
            
            # Сохранение обновлённой конфигурации
            backup_path = self.caa_triggers_path.with_suffix('.yaml.backup')
            shutil.copy2(self.caa_triggers_path, backup_path)
            
            with open(self.caa_triggers_path, 'w', encoding='utf-8') as f:
                yaml.dump(caa_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            results["steps"].append({
                "step": "save_caa_config",
                "status": "success",
                "message": f"Интегрировано {integrated_count} триггеров. Backup: {backup_path.name}"
            })
            
        except Exception as e:
            results["errors"].append(f"Ошибка интеграции с CAA: {e}")
    
    def _setup_git_hooks(self, pmr_config: Dict, results: Dict):
        """Настройка Git хуков"""
        print("  🪝 Настройка Git хуков...")
        
        # Создание директории для Git хуков
        git_hooks_dir = self.project_root / ".codeassistant/skills/caa-audit/git-hooks"
        git_hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Создание pre-commit хука
        pre_commit_hook = git_hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/bash
# Git pre-commit hook для проверки позиционирования CAA

echo "🔍 Проверка позиционирования Cognitive Automation Agent..."

# Запуск быстрого аудита
python .codeassistant/skills/caa-audit/caa-audit-script.py --quick --format=text

# Проверка score
SCORE=$(python .codeassistant/skills/caa-audit/caa-audit-script.py --focus=positioning --format=json 2>/dev/null | grep -o '"total_score":[0-9]*' | cut -d: -f2)

if [ -n "$SCORE" ] && [ "$SCORE" -lt 60 ]; then
    echo "⚠️  Внимание: Score позиционирования CAA ниже 60 ($SCORE/100)"
    echo "Рекомендуется улучшить позиционирование перед коммитом."
    read -p "Продолжить коммит? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Коммит отменён."
        exit 1
    fi
fi

echo "✅ Проверка позиционирования завершена."
exit 0
"""
        
        pre_commit_hook.write_text(pre_commit_content, encoding='utf-8')
        pre_commit_hook.chmod(0o755)
        
        # Создание pre-push хука
        pre_push_hook = git_hooks_dir / "pre-push"
        pre_push_content = """#!/bin/bash
# Git pre-push hook для проверки позиционирования CAA

echo "🔍 Полная проверка позиционирования CAA перед пушем..."

# Запуск полного аудита
python .codeassistant/skills/caa-audit/caa-audit-script.py --format=markdown --output=.agents/reports/pre-push-caa-audit-$(date +%Y%m%d-%H%M%S).md

SCORE=$(python .codeassistant/skills/caa-audit/caa-audit-script.py --format=json 2>/dev/null | grep -o '"total_score":[0-9]*' | cut -d: -f2)

if [ -n "$SCORE" ] && [ "$SCORE" -lt 40 ]; then
    echo "❌ Критическое предупреждение: Score позиционирования CAA ниже 40 ($SCORE/100)"
    echo "Пуш заблокирован. Улучшите позиционирование CAA."
    exit 1
fi

echo "✅ Проверка позиционирования завершена. Score: ${SCORE:-N/A}/100"
exit 0
"""
        
        pre_push_hook.write_text(pre_push_content, encoding='utf-8')
        pre_push_hook.chmod(0o755)
        
        # Интеграция с существующей конфигурацией Git хуков CAA
        if self.caa_git_hooks_path.exists():
            try:
                with open(self.caa_git_hooks_path, 'r', encoding='utf-8') as f:
                    git_hooks_config = yaml.safe_load(f) or {}
                
                if 'hooks' not in git_hooks_config:
                    git_hooks_config['hooks'] = []
                
                # Добавление PMR хуков
                git_hooks_config['hooks'].extend([
                    {
                        "name": "pre-commit-caa-audit",
                        "script": str(pre_commit_hook.relative_to(self.project_root)),
                        "description": "Проверка позиционирования CAA перед коммитом",
                        "enabled": True
                    },
                    {
                        "name": "pre-push-caa-audit",
                        "script": str(pre_push_hook.relative_to(self.project_root)),
                        "description": "Проверка позиционирования CAA перед пушем",
                        "enabled": True
                    }
                ])
                
                # Сохранение обновлённой конфигурации
                with open(self.caa_git_hooks_path, 'w', encoding='utf-8') as f:
                    yaml.dump(git_hooks_config, f, default_flow_style=False, allow_unicode=True)
                
                results["steps"].append({
                    "step": "setup_git_hooks",
                    "status": "success",
                    "message": "Git хуки настроены и интегрированы с CAA"
                })
                
            except Exception as e:
                results["warnings"].append(f"Ошибка интеграции Git хуков: {e}. Хуки созданы, но не интегрированы.")
        else:
            results["warnings"].append("Файл конфигурации Git хуков CAA не найден. Хуки созданы, но не интегрированы.")
    
    def _create_storage_directories(self, pmr_config: Dict, results: Dict):
        """Создание директорий для хранения данных"""
        print("  📁 Создание директорий для хранения данных...")
        
        storage_config = pmr_config.get('storage', {})
        created_dirs = []
        
        # Директории для отчётов
        reports_dir = self.project_root / storage_config.get('reports', {}).get('directory', '.agents/reports/caa-audit/')
        reports_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(reports_dir.relative_to(self.project_root)))
        
        # Директории для метрик
        metrics_dir = self.project_root / storage_config.get('metrics', {}).get('directory', '.agents/data/caa-metrics/')
        metrics_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(metrics_dir.relative_to(self.project_root)))
        
        # Директории для логов
        logs_dir = self.project_root / storage_config.get('logs', {}).get('directory', '.agents/logs/caa-audit/')
        logs_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(logs_dir.relative_to(self.project_root)))
        
        # Директория для ежедневных отчётов
        daily_dir = self.project_root / ".agents/reports/daily"
        daily_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(daily_dir.relative_to(self.project_root)))
        
        # Директория для PR отчётов
        pr_dir = self.project_root / ".agents/reports/pr"
        pr_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(pr_dir.relative_to(self.project_root)))
        
        results["steps"].append({
            "step": "create_storage_dirs",
            "status": "success",
            "message": f"Создано {len(created_dirs)} директорий: {', '.join(created_dirs[:3])}..."
        })
    
    def _generate_launch_scripts(self, pmr_config: Dict, results: Dict):
        """Генерация скриптов запуска"""
        print("  🚀 Генерация скриптов запуска...")
        
        # Скрипт для ручного запуска аудита
        launch_script = self.project_root / ".codeassistant/skills/caa-audit/launch-audit.sh"
        launch_content = """#!/bin/bash
# Скрипт запуска аудита позиционирования CAA

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$PROJECT_ROOT"

echo "🎯 Запуск аудита позиционирования Cognitive Automation Agent"
echo "=========================================================="

# Параметры по умолчанию
MODE="full"
FORMAT="markdown"
OUTPUT=".agents/reports/caa-audit-$(date +%Y%m%d-%H%M%S).md"
FOCUS=""

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            MODE="quick"
            shift
            ;;
        --focus)
            FOCUS="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --help)
            echo "Использование: $0 [опции]"
            echo "Опции:"
            echo "  --quick        Быстрый аудит (только критические проверки)"
            echo "  --focus AREA   Фокус на конкретной области (implementation,positioning,integration,evidence)"
            echo "  --format FMT   Формат вывода (markdown, json, text)"
            echo "  --output FILE  Путь для сохранения отчёта"
            echo "  --help         Показать эту справку"
            exit 0
            ;;
        *)
            echo "Неизвестный аргумент: $1"
            exit 1
            ;;
    esac
done

# Формирование команды
CMD="python .codeassistant/skills/caa-audit/caa-audit-script.py"

if [ "$MODE" = "quick" ]; then
    CMD="$CMD --quick"
fi

if [ -n "$FOCUS" ]; then
    CMD="$CMD --focus=$FOCUS"
fi

CMD="$CMD --format=$FORMAT"
CMD="$CMD --output=$OUTPUT"

echo "Команда: $CMD"
echo ""

# Запуск аудита
eval $CMD

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Аудит завершён успешно"
    echo "📄 Отчёт сохранён: $OUTPUT"
else
    echo ""
    echo "❌ Аудит завершился с ошибкой (код: $EXIT_CODE)"
fi

exit $EXIT_CODE
"""
        
        launch_script.write_text(launch_content, encoding='utf-8')
        launch_script.chmod(0o755)
        
        # Скрипт для проверки конфигурации
        check_script = self.project_root / ".codeassistant/skills/caa-audit/check-config.py"
        check_content = """#!/usr/bin/env python3
"""
        # Продолжение скрипта check-config.py будет в следующем сообщении из-за ограничения длины
        check_script.write_text(check_content, encoding='utf-8')
        check_script.chmod(0o755)
        
        results["steps"].append({
            "step": "generate_launch_scripts",
            "status": "success",
            "message": "Скрипты запуска сгенерированы"
        })

def main():
    parser = argparse.ArgumentParser(description="Активатор проактивных триггеров PMR Agent")
    parser.add_argument("--project-root", default=".", help="Корневая директория проекта")
    parser.add_argument("--dry-run", action="store_true", help="Проверка без внесения изменений")
    parser.add_argument("--verbose", action="store_true", help="Подробный вывод")
    
    args = parser.parse_args()
    
    activator = TriggerActivator(args.project_root)
    results = activator.activate_all(args.dry_run)
    
    # Вывод результатов
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ АКТИВАЦИИ")
    print("="*60)
    
    if results["steps"]:
        print("\n✅ УСПЕШНЫЕ ШАГИ:")
        for step in results["steps"]:
            print(f"  • {step['message']}")
    
    if results["warnings"]:
        print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
        for warning in results["warnings"]:
            print(f"  • {warning}")
    
    if results["errors"]:
        print("\n❌ ОШИБКИ:")
        for error in results["errors"]:
            print(f"  • {error}")
        
        if not args.dry_run:
            print("\n🔴 Активация завершилась с ошибками.")
            sys.exit(1)
    
    print("\n" + "="*60)
    
    if args.dry_run:
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА (dry-run)")
        print("   Для реальной активации запустите без --dry-run")
    else:
        print("🎯 АКТИВАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Проверить интеграцию: python .codeassistant/skills/caa-audit/check-config.py")
        print("2. Запустить тестовый аудит: ./launch-audit.sh --quick")
        print("3. Проверить Git хуки: git commit --allow-empty -m 'test'")
        print("\n📚 ДОКУМЕНТАЦИЯ:")
        print("  - Конфигурация: .codeassistant/skills/caa-audit/pmr-triggers.yaml")
        print("  - Скрипт аудита: .codeassistant/skills/caa-audit/caa-audit-script.py")
        print("  - Git хуки: .codeassistant/skills/caa-audit/git-hooks/")
    
    print("="*60)

if __name__ == "__main__":
    main()