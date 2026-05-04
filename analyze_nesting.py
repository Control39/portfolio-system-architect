#!/usr/bin/env python3
"""
Анализатор вложенности структуры проекта.
Выявляет дублирование, глубокие вложенности и проблемы архитектуры.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class ProjectAnalyzer:
    def __init__(self, root: str = "."):
        self.root = Path(root).resolve()
        self.structure = {}
        self.stats = {
            "total_dirs": 0,
            "total_files": 0,
            "max_depth": 0,
            "avg_depth": 0,
            "deep_paths": [],  # глубже чем 6 уровней
            "duplicate_dirs": defaultdict(list),  # одинаковые имена в разных местах
            "suspicious_patterns": defaultdict(list),  # config, data, logs и т.д.
        }

    def analyze(self):
        """Запуск полного анализа"""
        print("🔍 Анализ структуры проекта...")
        
        # Обход директорий
        for path in self.root.rglob("*"):
            if path.is_dir() and not self._is_ignored(path):
                self._analyze_directory(path)
        
        self._calculate_stats()
        return self.stats

    def _is_ignored(self, path: Path) -> bool:
        """Пропустить стандартные папки"""
        ignored = {
            ".git", ".venv", "node_modules", "__pycache__", 
            ".pytest_cache", ".mypy_cache", "dist", "build",
            ".egg-info", "venv", "env", ".cache"
        }
        return any(part in ignored for part in path.parts)

    def _analyze_directory(self, path: Path):
        """Анализ одной директории"""
        try:
            relative_path = path.relative_to(self.root)
        except ValueError:
            return
        depth = len(relative_path.parts)
        
        self.stats["total_dirs"] += 1
        self.stats["max_depth"] = max(self.stats["max_depth"], depth)
        
        # Проверка на глубокую вложенность
        if depth > 6:
            self.stats["deep_paths"].append({
                "path": str(relative_path),
                "depth": depth
            })
        
        # Проверка на дублирование имён
        dir_name = path.name
        self.stats["duplicate_dirs"][dir_name].append(str(relative_path))
        
        # Проверка на подозрительные паттерны
        suspicious = ["config", "data", "logs", "cache", "models", "skills", 
                     "rules", "agents", "tools", "utils", "helpers"]
        if any(pattern in dir_name for pattern in suspicious):
            self.stats["suspicious_patterns"][dir_name].append(str(relative_path))
        
        # Подсчет файлов
        try:
            file_count = len(list(path.glob("*")))
            if file_count > 0:
                self.stats["total_files"] += file_count
        except:
            pass

    def _calculate_stats(self):
        """Расчет статистики"""
        if self.stats["total_dirs"] > 0:
            self.stats["avg_depth"] = round(self.stats["max_depth"] / 1.5, 1)
        
        # Фильтруем реальные дублирования (не одиночные)
        self.stats["duplicate_dirs"] = {
            k: v for k, v in self.stats["duplicate_dirs"].items() 
            if len(v) > 1
        }

    def print_report(self):
        """Вывод отчета"""
        print("\n" + "="*70)
        print("📊 АНАЛИЗ ВЛОЖЕННОСТИ ПРОЕКТА")
        print("="*70)
        
        print(f"\n📈 Общая статистика:")
        print(f"  • Всего директорий: {self.stats['total_dirs']}")
        print(f"  • Всего файлов: {self.stats['total_files']}")
        print(f"  • Максимальная глубина: {self.stats['max_depth']} уровней")
        print(f"  • Средняя глубина: {self.stats['avg_depth']} уровней")
        
        if self.stats["deep_paths"]:
            print(f"\n⚠️  ГЛУБОКИЕ ВЛОЖЕННОСТИ (>6 уровней): {len(self.stats['deep_paths'])}")
            for item in sorted(self.stats["deep_paths"], key=lambda x: x["depth"], reverse=True)[:10]:
                print(f"  • {item['path']} (глубина: {item['depth']})")
        
        if self.stats["duplicate_dirs"]:
            print(f"\n🔄 ДУБЛИРОВАНИЕ ИМЁН: {len(self.stats['duplicate_dirs'])}")
            for name, paths in sorted(self.stats["duplicate_dirs"].items()):
                print(f"  • '{name}' встречается в {len(paths)} местах:")
                for path in paths:
                    print(f"    - {path}")
        
        if self.stats["suspicious_patterns"]:
            print(f"\n🎯 ПОДОЗРИТЕЛЬНЫЕ ПАТТЕРНЫ: {len(self.stats['suspicious_patterns'])}")
            for pattern, paths in sorted(self.stats["suspicious_patterns"].items()):
                print(f"  • '{pattern}': {len(paths)} вхождений")
                for path in paths[:3]:
                    print(f"    - {path}")
                if len(paths) > 3:
                    print(f"    ... и ещё {len(paths)-3}")
        
        print("\n" + "="*70)

    def generate_recommendations(self):
        """Генерация рекомендаций"""
        print("\n💡 РЕКОМЕНДАЦИИ:")
        
        if self.stats["max_depth"] > 6:
            print("  1. ⚠️  Уменьшить глубину вложенности")
            print("     → Объединить папки на уровне 7+")
            print("     → Переместить дублирующиеся компоненты")
        
        if len(self.stats["duplicate_dirs"]) > 3:
            print(f"\n  2. 🔄 Консолидировать дублирующиеся директории")
            print(f"     → Создать единые 'skills', 'config', 'tools'")
            print(f"     → Использовать symlinks для обратной совместимости")
        
        if len(self.stats["suspicious_patterns"]) > 10:
            print(f"\n  3. 📦 Стандартизировать структуру")
            print(f"     → Перенести все конфиги в 'config/'")
            print(f"     → Перенести все логи в 'logs/'")
            print(f"     → Создать 'tools/' для инструментов анализа")
        
        print("\n  4. 📋 Составить карту инструментов:")
        print("     → Какие инструменты используются?")
        print("     → Какие дублируют функциональность?")
        print("     → Какие можно объединить?")


if __name__ == "__main__":
    analyzer = ProjectAnalyzer()
    stats = analyzer.analyze()
    analyzer.print_report()
    analyzer.generate_recommendations()
    
    # Экспорт статистики
    report_path = Path("analysis_report.json")
    with open(report_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"\n✅ Отчет сохранён: {report_path.absolute()}")
