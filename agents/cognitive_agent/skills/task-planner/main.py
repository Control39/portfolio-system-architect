"""
Проактивный планировщик задач на основе контекста проекта.
Запускается после сканирования и извлечения маркеров.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class TaskPlanner:
    def __init__(self):
        self.report_path = "reports/planning/"
        self.context_file = "reports/project-analysis.json"
        Path(self.report_path).mkdir(parents=True, exist_ok=True)

    def load_context(self):
        """Загружает результаты project-scanner"""
        if not os.path.exists(self.context_file):
            return {}
        with open(self.context_file, encoding="utf-8") as f:
            return json.load(f)

    def predict_tasks(self):
        context = self.load_context()
        tasks = []

        # Правило 1: Низкое покрытие тестами
        coverage = context.get("quick", {}).get("test_coverage", 100)
        if coverage < 85:
            tasks.append(
                {
                    "task": "increase_test_coverage",
                    "priority": "high",
                    "title": "📌 Дописать тесты",
                    "description": f"Покрытие кода {coverage}% < 85%. Нужно добавить unit-тесты.",
                    "suggestion": "Запустить: pytest --cov=src --cov-report=html",
                    "impact": "quality",
                    "estimate_minutes": 60,
                }
            )

        # Правило 2: Найдены уязвимости
        vulns = context.get("deep", {}).get("security", {}).get("vulnerabilities", [])
        if len(vulns) > 0:
            tasks.append(
                {
                    "task": "fix_security_issues",
                    "priority": "critical",
                    "title": f"🚨 Исправить {len(vulns)} уязвимостей",
                    "description": "Обнаружены уязвимости в зависимостях (trivy/safety).",
                    "suggestion": "Выполнить: trivy fs . --security-checks vuln",
                    "impact": "security",
                    "estimate_minutes": 90,
                }
            )

        # Правило 3: Изменён ADR → нужно обновить маркеры
        adr_updated = context.get("context", {}).get("adr_updated", False)
        if adr_updated:
            tasks.append(
                {
                    "task": "re_extract_markers",
                    "priority": "medium",
                    "title": "🔄 Перезапустить извлечение маркеров",
                    "description": "Обнаружены изменения в ADR — нужно обновить доказательства компетенций.",
                    "suggestion": "python -m agents.cognitive_agent --skill=marker-extraction",
                    "impact": "portfolio",
                    "estimate_minutes": 10,
                }
            )

        return sorted(tasks, key=lambda x: self._priority_score(x["priority"]), reverse=True)

    def _priority_score(self, priority):
        return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(priority, 0)

    def save_plan(self, tasks):
        plan = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_tasks": len(tasks),
            "tasks": tasks,
        }
        path = f"{self.report_path}task_plan.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        print(f"✅ План задач сохранён: {path}")
        return path


if __name__ == "__main__":
    planner = TaskPlanner()
    tasks = planner.predict_tasks()
    planner.save_plan(tasks)
    print(f"\n📋 Предложено задач: {len(tasks)}")
    for t in tasks:
        print(f"  [{t['priority'].upper()}] {t['title']} — {t['suggestion']}")
