#!/usr/bin/env python3
"""
CAA Audit Script - Реализация режима caa-audit для PMR Agent

Аудит и валидация позиционирования Cognitive Automation Agent (CAA)
Проверка соответствия между технической реализацией и бизнес-позиционированием
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class CaaAudit:
    """Аудитор Cognitive Automation Agent"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {
            "audit_date": datetime.now().isoformat(),
            "scores": {},
            "findings": [],
            "recommendations": [],
            "artifacts": []
        }
        
    def run_audit(self, focus_areas: List[str] = None) -> Dict:
        """Запуск полного аудита CAA"""
        
        print("🔍 Запуск аудита Cognitive Automation Agent...")
        
        # 1. Проверка реализации CAA
        if not focus_areas or "implementation" in focus_areas:
            self._audit_implementation()
        
        # 2. Проверка позиционирования
        if not focus_areas or "positioning" in focus_areas:
            self._audit_positioning()
        
        # 3. Проверка интеграций
        if not focus_areas or "integration" in focus_areas:
            self._audit_integrations()
        
        # 4. Проверка доказательной базы
        if not focus_areas or "evidence" in focus_areas:
            self._audit_evidence()
        
        # 5. Расчет итогового score
        self._calculate_scores()
        
        return self.results
    
    def _audit_implementation(self):
        """Аудит технической реализации CAA"""
        print("  📋 Проверка технической реализации...")
        
        # Проверка структуры .agents/
        agents_dir = self.project_root / ".agents"
        if agents_dir.exists():
            self.results["findings"].append({
                "category": "implementation",
                "type": "success",
                "message": "Директория .agents/ существует",
                "details": f"Найдено: {len(list(agents_dir.iterdir()))} элементов"
            })
            
            # Проверка ключевых поддиректорий
            required_dirs = ["config", "skills", "data", "logs", "reports"]
            for dir_name in required_dirs:
                dir_path = agents_dir / dir_name
                if dir_path.exists():
                    self.results["findings"].append({
                        "category": "implementation",
                        "type": "success",
                        "message": f"Директория .agents/{dir_name}/ существует",
                        "details": "Обязательная структура присутствует"
                    })
                else:
                    self.results["findings"].append({
                        "category": "implementation",
                        "type": "warning",
                        "message": f"Директория .agents/{dir_name}/ отсутствует",
                        "recommendation": f"Создать директорию для {dir_name}"
                    })
        else:
            self.results["findings"].append({
                "category": "implementation",
                "type": "critical",
                "message": "Директория .agents/ не найдена",
                "recommendation": "Создать структуру CAA в .agents/"
            })
    
    def _audit_positioning(self):
        """Аудит позиционирования CAA"""
        print("  📝 Проверка позиционирования...")
        
        # Ключевые файлы для проверки
        key_files = [
            "README.md",
            "docs/employer/ONE-PAGER.md",
            "docs/employer/PRESENTATION-2MIN.md",
            ".agents/USAGE.md"
        ]
        
        positioning_terms = {
            "autonomy": ["автономн", "предугадывает", "сам создаёт", "проактивн", "контекстное понимание"],
            "architect_narrative": ["архитектор", "строитель", "проектирует систему", "управляет ии"],
            "value_proposition": ["экономит время", "сокращает затраты", "увеличивает качество", "предотвращает проблемы"]
        }
        
        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8', errors='ignore').lower()
                    
                    # Проверка терминов
                    for category, terms in positioning_terms.items():
                        found_terms = [term for term in terms if term in content]
                        if found_terms:
                            self.results["findings"].append({
                                "category": "positioning",
                                "type": "success",
                                "message": f"В {file_path} найдены термины {category}",
                                "details": f"Найдено: {', '.join(found_terms[:3])}"
                            })
                        else:
                            self.results["findings"].append({
                                "category": "positioning",
                                "type": "warning",
                                "message": f"В {file_path} отсутствуют термины {category}",
                                "recommendation": f"Добавить термины: {', '.join(terms[:3])}"
                            })
                except Exception as e:
                    self.results["findings"].append({
                        "category": "positioning",
                        "type": "error",
                        "message": f"Ошибка чтения {file_path}",
                        "details": str(e)
                    })
    
    def _audit_integrations(self):
        """Аудит интеграций CAA"""
        print("  🔗 Проверка интеграций...")
        
        # Проверка Git хуков
        git_hooks_path = self.project_root / ".agents/config/git-hooks.yaml"
        if git_hooks_path.exists():
            self.results["findings"].append({
                "category": "integration",
                "type": "success",
                "message": "Конфигурация Git хуков найдена",
                "artifact": str(git_hooks_path.relative_to(self.project_root))
            })
            
            try:
                with open(git_hooks_path, 'r', encoding='utf-8') as f:
                    git_hooks = yaml.safe_load(f)
                    if git_hooks and 'hooks' in git_hooks:
                        self.results["findings"].append({
                            "category": "integration",
                            "type": "success",
                            "message": f"Настроено {len(git_hooks['hooks'])} Git хуков",
                            "details": "Интеграция с Git работает"
                        })
            except Exception as e:
                self.results["findings"].append({
                    "category": "integration",
                    "type": "warning",
                    "message": "Ошибка чтения git-hooks.yaml",
                    "details": str(e)
                })
        
        # Проверка триггеров
        triggers_path = self.project_root / ".agents/config/triggers.yaml"
        if triggers_path.exists():
            self.results["findings"].append({
                "category": "integration",
                "type": "success",
                "message": "Конфигурация триггеров найдена",
                "artifact": str(triggers_path.relative_to(self.project_root))
            })
        
        # Проверка мониторинга
        monitoring_dirs = ["monitoring", ".agents/dashboards", ".agents/data"]
        for dir_name in monitoring_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.results["findings"].append({
                    "category": "integration",
                    "type": "success",
                    "message": f"Система мониторинга найдена: {dir_name}",
                    "details": "Наблюдаемость настроена"
                })
    
    def _audit_evidence(self):
        """Аудит доказательной базы"""
        print("  📊 Проверка доказательной базы...")
        
        # Поиск артефактов
        artifact_patterns = [
            ("reports", ".agents/reports/", "Отчёты CAA"),
            ("logs", ".agents/logs/", "Логи выполнения"),
            ("dashboards", ".agents/dashboards/", "Дашборды мониторинга"),
            ("test_reports", "test_reports/", "Отчёты тестирования"),
            ("metrics", "badges/metrics.json", "Метрики проекта")
        ]
        
        for artifact_type, path_pattern, description in artifact_patterns:
            artifact_path = self.project_root / path_pattern
            if artifact_path.exists():
                if artifact_path.is_dir():
                    artifacts = list(artifact_path.glob("*"))
                    if artifacts:
                        self.results["artifacts"].append({
                            "type": artifact_type,
                            "path": path_pattern,
                            "count": len(artifacts),
                            "description": description
                        })
                        self.results["findings"].append({
                            "category": "evidence",
                            "type": "success",
                            "message": f"Найдены {description}",
                            "details": f"{len(artifacts)} файлов в {path_pattern}"
                        })
                else:
                    # Это файл
                    self.results["artifacts"].append({
                        "type": artifact_type,
                        "path": path_pattern,
                        "count": 1,
                        "description": description
                    })
                    self.results["findings"].append({
                        "category": "evidence",
                        "type": "success",
                        "message": f"Найден файл {description}",
                        "details": path_pattern
                    })
    
    def _calculate_scores(self):
        """Расчёт итоговых оценок"""
        print("  📈 Расчёт оценок...")
        
        # Категории и их веса
        categories = {
            "implementation": 0.3,
            "positioning": 0.3,
            "integration": 0.2,
            "evidence": 0.2
        }
        
        scores = {}
        total_score = 0
        
        for category, weight in categories.items():
            # Подсчёт успешных проверок в категории
            category_findings = [f for f in self.results["findings"] if f["category"] == category]
            if not category_findings:
                scores[category] = 0
                continue
                
            success_count = len([f for f in category_findings if f["type"] == "success"])
            total_count = len(category_findings)
            
            category_score = (success_count / total_count) * 100 if total_count > 0 else 0
            scores[category] = round(category_score, 1)
            total_score += category_score * weight
        
        self.results["scores"] = scores
        self.results["total_score"] = round(total_score, 1)
        
        # Генерация рекомендаций на основе findings
        critical_issues = [f for f in self.results["findings"] if f["type"] == "critical"]
        warnings = [f for f in self.results["findings"] if f["type"] == "warning"]
        
        if critical_issues:
            self.results["recommendations"].append({
                "priority": "critical",
                "message": f"Найдено {len(critical_issues)} критических проблем",
                "actions": [f["recommendation"] for f in critical_issues if "recommendation" in f]
            })
        
        if warnings:
            self.results["recommendations"].append({
                "priority": "high",
                "message": f"Найдено {len(warnings)} предупреждений",
                "actions": [f["recommendation"] for f in warnings if "recommendation" in f]
            })
    
    def generate_report(self, output_format: str = "markdown", output_path: Optional[str] = None) -> str:
        """Генерация отчёта"""
        
        if output_format == "markdown":
            report = self._generate_markdown_report()
        elif output_format == "json":
            report = json.dumps(self.results, indent=2, ensure_ascii=False)
        else:
            report = str(self.results)
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report, encoding='utf-8')
            print(f"📄 Отчёт сохранён: {output_path}")
        
        return report
    
    def _generate_markdown_report(self) -> str:
        """Генерация Markdown отчёта"""
        
        report = f"""# Отчёт аудита Cognitive Automation Agent

**Дата аудита**: {self.results['audit_date']}
**Общий score**: {self.results.get('total_score', 0)}/100

## 📊 Оценки по категориям

| Категория | Оценка | Статус |
|-----------|--------|--------|
"""
        
        for category, score in self.results.get("scores", {}).items():
            status = "🟢 Отлично" if score >= 80 else "🟡 Средне" if score >= 60 else "🔴 Требует улучшений"
            report += f"| {category.capitalize()} | {score}/100 | {status} |\n"
        
        report += """

## 🔍 Ключевые находки

### Успехи ✅
"""
        
        successes = [f for f in self.results["findings"] if f["type"] == "success"]
        for finding in successes[:10]:  # Показываем первые 10 успехов
            report += f"- **{finding['message']}**\n"
            if finding.get('details'):
                report += f"  *{finding['details']}*\n"
        
        report += "\n### Проблемы ⚠️\n"
        
        issues = [f for f in self.results["findings"] if f["type"] in ["warning", "critical", "error"]]
        for finding in issues[:10]:  # Показываем первые 10 проблем
            icon = "🔴" if finding["type"] == "critical" else "🟡" if finding["type"] == "warning" else "⚫"
            report += f"- {icon} **{finding['message']}**\n"
            if finding.get('details'):
                report += f"  *{finding['details']}*\n"
            if finding.get('recommendation'):
                report += f"  💡 **Рекомендация**: {finding['recommendation']}\n"
        
        report += "\n## 📁 Артефакты\n"
        
        if self.results["artifacts"]:
            report += "| Тип | Путь | Количество | Описание |\n"
            report += "|-----|------|------------|----------|\n"
            for artifact in self.results["artifacts"]:
                report += f"| {artifact['type']} | `{artifact['path']}` | {artifact['count']} | {artifact['description']} |\n"
        else:
            report += "Артефакты не найдены\n"
        
        report += "\n## 🎯 Рекомендации\n"
        
        if self.results["recommendations"]:
            for rec in self.results["recommendations"]:
                priority_icon = "🔴" if rec["priority"] == "critical" else "🟡" if rec["priority"] == "high" else "🟢"
                report += f"### {priority_icon} {rec['priority'].upper()}: {rec['message']}\n"
                if rec.get("actions"):
                    for action in rec["actions"]:
                        report += f"- {action}\n"
        else:
            report += "Критических рекомендаций нет\n"
        
        report += f"""

## 📈 Итоговая оценка позиционирования CAA

**{self.results.get('total_score', 0)}/100** - {
    "Отличное позиционирование" if self.results.get('total_score', 0) >= 80 else 
    "Хорошее позиционирование" if self.results.get('total_score', 0) >= 60 else 
    "Требует значительных улучшений"
}

### Ключевые сильные стороны:
1. **Автономность**: {'✅ Высокая' if self.results.get('scores', {}).get('implementation', 0) >= 70 else '⚠️ Средняя' if self.results.get('scores', {}).get('implementation', 0) >= 50 else '❌ Низкая'}
2. **Интеграция**: {'✅ Полная' if self.results.get('scores', {}).get('integration', 0) >= 70 else '⚠️ Частичная' if self.results.get('scores', {}).get('integration', 0) >= 50 else '❌ Слабая'}
3. **Доказательная база**: {'✅ Богатая' if self.results.get('scores', {}).get('evidence', 0) >= 70 else '⚠️ Умеренная' if self.results.get('scores', {}).get('evidence', 0) >= 50 else '❌ Скудная'}

---

*Отчёт сгенерирован автоматически CAA Audit Script*
"""
        
        return report

def main():
    parser = argparse.ArgumentParser(description="CAA Audit Script - Аудит позиционирования Cognitive Automation Agent")
    parser.add_argument("--project-root", default=".", help="Корневая директория проекта")
    parser.add_argument("--focus", help="Фокусные области (implementation,positioning,integration,evidence)")
    parser.add_argument("--output", help="Путь для сохранения отчёта")
    parser.add_argument("--format", choices=["markdown", "json", "text"], default="markdown", help="Формат вывода")
    parser.add_argument("--quick", action="store_true", help="Быстрый режим (только критические проверки)")
    
    args = parser.parse_args()
    
    # Определение фокусных областей
    focus_areas = None
    if args.focus:
        focus_areas = [area.strip() for area in args.focus.split(",")]
    elif args.quick:
        focus_areas = ["implementation", "positioning"]  # Только критические проверки
    
    # Запуск аудита
    auditor = CaaAudit(args.project_root)
    results = auditor.run_audit(focus_areas)
    
    # Генерация отчёта
    report = auditor.generate_report(args.format, args.output)
    
    if not args.output:
        print("\n" + "="*60)
        print(report)
    
    # Вывод итогового score
    total_score = results.get("total_score", 0)
    print(f"\n🎯 Итоговый score позиционирования CAA: {total_score}/100")
    
    if total_score >= 80:
        print("✅ Отличное позиционирование! CAA описан как автономная система.")
    elif total_score >= 60:
        print("⚠️ Хорошее позиционирование, но есть возможности для улучшения.")
    else:
        print("🔴 Требует значительных улучшений в позиционировании.")
    
    # Возвращаем код выхода в зависимости от score
    sys.exit(0 if total_score >= 60 else 1)

if __name__ == "__main__":
    main()