#!/usr/bin/env python3
"""
Генератор визуальной карты GitHub Workflows.

Анализирует workflow файлы в .github/workflows/ и генерирует:
1. Mermaid диаграмму (docs/GITHUB-WORKFLOWS-DIAGRAM.md)
2. Сводную таблицу статусов
3. Выявляет проблемы (если есть локальные логи)

Использование:
    python scripts/generate-workflow-diagram.py
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml


# Настройки
REPO_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
OUTPUT_FILE = REPO_ROOT / "docs" / "GITHUB-WORKFLOWS-DIAGRAM.md"

# Категории workflows (можно расширять)
CATEGORIES = {
    "CI / CD": [
        "ci.yml",
        "deploy.yml",
        "deploy-k8s.yml",
        "deploy-pages.yml",
        "deploy-dashboard.yml",
        "azure-deploy.yml",
        "release.yml",
        "code-quality.yml",
        "security-scan.yml",
        "codeql.yml",
        "cognitive-agent-ci.yml",
        "test-decision-engine.yml",
    ],
    "Monitoring & Alerts": [
        "monitoring-alerts.yml",
        "mirror-sync-enhanced.yml",
        "mirror-to-sourcecraft.yml",
        "monitor-mirror-discrepancies.yml",
        "badge-health-monitor.yml",
    ],
    "Metrics & Badges": ["update-metrics.yml", "auto-update-badges.yml"],
    "Documentation": ["docs.yml"],
    "Specialized Tests": ["cognitive-agent-ci.yml", "test-decision-engine.yml"],
    "Utilities": [
        "repo-audit.yml",
        "architecture-analysis.yml",
        "duplicate-check.yml",
        "vscode-extensions-check.yml",
    ],
    "GitOps": ["gitops-argocd.yml"],
    "Auto-Merge": ["dependabot-auto-merge.yml"],
    "AI Config": ["ai-configs.yaml"],
    "RAG": ["rag-update.yml"],
}

# Известные проблемы (можно обновлять вручную)
KNOWN_ISSUES = {
    "monitoring-alerts.yml": {
        "status": "fixed",
        "issue": "Health check отключён (localhost недоступен в CI)",
        "fix": "if: false для health-check job",
    },
    "mirror-to-sourcecraft.yml": {
        "status": "fixed",
        "issue": "Неверный URL SourceCraft",
        "fix": "Изменен на git.sourcecraft.dev/leadarchitect-ai",
    },
    "deploy-pages.yml": {
        "status": "broken",
        "issue": "publish_dir не совпадает с site_dir",
        "fix": "Изменить publish_dir: ./docs/site → ./site",
    },
    "update-metrics.yml": {
        "status": "broken",
        "issue": "Нет coverage.xml (тесты не проходят)",
        "fix": "Добавить запуск тестов перед сборкой метрик",
    },
    "mirror-sync-enhanced.yml": {
        "status": "broken",
        "issue": "Аналог SourceCraft mirror, может дублироваться",
        "fix": "Проверить необходимость, объединить с mirror-to-sourcecraft.yml",
    },
    "monitor-mirror-discrepancies.yml": {
        "status": "broken",
        "issue": "Проверяет расхождения зеркал",
        "fix": "Проверить работу после исправления URL",
    },
    "badge-health-monitor.yml": {
        "status": "broken",
        "issue": "Мониторинг бейджей",
        "fix": "Проверить после исправления update-metrics.yml",
    },
    "auto-update-badges.yml": {
        "status": "broken",
        "issue": "Автообновление бейджей",
        "fix": "Зависит от update-metrics.yml",
    },
}


def parse_workflow(file_path: Path) -> dict:
    """Парсинг workflow файла."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)

        name = content.get("name", file_path.stem)
        on_triggers = content.get("on", {})
        jobs = content.get("jobs", {})

        # Анализ триггеров
        triggers = []
        if isinstance(on_triggers, dict):
            if "push" in on_triggers:
                triggers.append("push")
            if "pull_request" in on_triggers:
                triggers.append("pr")
            if "schedule" in on_triggers:
                triggers.append("schedule")
            if "workflow_dispatch" in on_triggers:
                triggers.append("manual")
        elif on_triggers:
            triggers.append("unknown")

        # Анализ jobs
        job_names = list(jobs.keys())
        has_disabled = any(job.get("if") == "false" for job in jobs.values())

        return {
            "name": name,
            "file": file_path.stem,
            "triggers": triggers,
            "jobs": job_names,
            "has_disabled": has_disabled,
            "content": content,
        }
    except Exception as e:
        return {
            "name": file_path.stem,
            "file": file_path.stem,
            "error": str(e),
            "triggers": [],
            "jobs": [],
            "has_disabled": False,
        }


def categorize_workflow(filename: str) -> str:
    """Определение категории workflow."""
    for category, files in CATEGORIES.items():
        if filename in files:
            return category
    return "Uncategorized"


def get_status(filename: str) -> dict:
    """Получение статуса workflow."""
    if filename in KNOWN_ISSUES:
        issue = KNOWN_ISSUES[filename]
        return {"status": issue["status"], "issue": issue["issue"], "fix": issue["fix"]}
    return {"status": "unknown", "issue": None, "fix": None}


def generate_mermaid_diagram(workflows: list) -> str:
    """Генерация Mermaid диаграммы."""
    lines = ["```mermaid", "graph TD"]

    # Группировка по категориям
    grouped = defaultdict(list)
    for wf in workflows:
        category = categorize_workflow(wf["file"])
        grouped[category].append(wf)

    # Генерация узлов
    for category, wfs in grouped.items():
        category.replace(" & ", "_and_").replace(" ", "_")
        lines.append(f'    subgraph "{category}"')

        for wf in wfs:
            node_id = wf["file"].replace(".", "_")
            status = get_status(wf["file"])

            # Цвет в зависимости от статуса
            if status["status"] == "fixed":
                color = "#4CAF50"  # Зеленый
                icon = "✅"
            elif status["status"] == "broken":
                color = "#f44336"  # Красный
                icon = "❌"
            elif wf["has_disabled"]:
                color = "#FF9800"  # Оранжевый
                icon = "⚠️"
            else:
                color = "#2196F3"  # Синий
                icon = "ℹ️"

            # Формирование узла
            triggers = ", ".join(wf["triggers"][:2]) if wf["triggers"] else "manual"
            label = f"{icon} {wf['name']}<br/><small>{triggers}</small>"
            lines.append(f'        {node_id}["{label}"]')
            lines.append(f"        style {node_id} fill:{color},color:#fff")

        lines.append("    end")
        lines.append("")

    lines.append("```")
    return "\n".join(lines)


def generate_summary_table(workflows: list) -> str:
    """Генерация сводной таблицы."""
    table = [
        "| Файл | Категория | Триггеры | Статус | Проблема |",
        "|------|-----------|----------|--------|----------|",
    ]

    for wf in workflows:
        category = categorize_workflow(wf["file"])
        triggers = ", ".join(wf["triggers"][:2]) if wf["triggers"] else "manual"
        status_info = get_status(wf["file"])

        if status_info["status"] == "fixed":
            status = "✅ Исправлен"
            issue = status_info["issue"]
        elif status_info["status"] == "broken":
            status = "❌ Требует исправления"
            issue = status_info["issue"]
        elif wf["has_disabled"]:
            status = "⚠️ Отключен"
            issue = "Временно отключен"
        else:
            status = "ℹ️ Не проверено"
            issue = "-"

        table.append(f"| `{wf['file']}` | {category} | {triggers} | {status} | {issue} |")

    return "\n".join(table)


def generate_category_stats(workflows: list) -> str:
    """Генерация статистики по категориям."""
    stats = defaultdict(lambda: {"total": 0, "working": 0, "needs_attention": 0})

    for wf in workflows:
        category = categorize_workflow(wf["file"])
        stats[category]["total"] += 1

        status = get_status(wf["file"])
        if status["status"] == "fixed" or (not status["issue"] and not wf["has_disabled"]):
            stats[category]["working"] += 1
        else:
            stats[category]["needs_attention"] += 1

    lines = [
        "| Категория | Всего | Работают | Требуют внимания |",
        "|-----------|-------|----------|------------------|",
    ]

    total_total = total_working = total_attention = 0
    for category, data in sorted(stats.items()):
        lines.append(
            f"| {category} | {data['total']} | {data['working']} | {data['needs_attention']} |"
        )
        total_total += data["total"]
        total_working += data["working"]
        total_attention += data["needs_attention"]

    lines.append(f"| **Всего** | **{total_total}** | **{total_working}** | **{total_attention}** |")
    return "\n".join(lines)


def generate_fix_recommendations(workflows: list) -> str:
    """Генерация рекомендаций по исправлению."""
    recommendations = []

    for wf in workflows:
        status = get_status(wf["file"])
        if status["status"] == "broken":
            recommendations.append(
                {"file": wf["file"], "issue": status["issue"], "fix": status["fix"]}
            )

    if not recommendations:
        return "✅ Нет критических проблем для исправления."

    lines = ["### 🔧 Требуемые исправления:\n"]
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"**{i}. `{rec['file']}`**")
        lines.append(f"   - **Проблема:** {rec['issue']}")
        lines.append(f"   - **Решение:** {rec['fix']}")
        lines.append("")

    return "\n".join(lines)


def main():
    """Основная функция."""
    print("🔍 Анализ workflows в .github/workflows/...")

    # Сбор всех workflow файлов
    workflow_files = list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))
    workflows = [parse_workflow(wf) for wf in workflow_files]

    print(f"📊 Найдено {len(workflows)} workflow файлов")

    # Генерация контента
    timestamp = datetime.now().strftime("%d %B %Y, %H:%M")

    content = f"""# 📊 GitHub Workflows — Визуальная карта

> **Последнее обновление:** {timestamp}
> **Генерируется автоматически:** `scripts/generate-workflow-diagram.py`
> **Режим:** Исправление проблем (не отключение)

---

## 🔄 Общая схема

{generate_mermaid_diagram(workflows)}

---

## 📋 Детальный обзор

{generate_summary_table(workflows)}

---

## 📈 Статистика

{generate_category_stats(workflows)}

---

## 🔧 Рекомендации по исправлению

{generate_fix_recommendations(workflows)}

---

## 📝 История изменений

| Дата | Изменения | Автор |
|------|-----------|-------|
| {datetime.now().strftime("%d.%m.%Y")} | Автоматическая генерация | Koda AI |

---

*Этот документ генерируется автоматически.*
*Для обновления: `python scripts/generate-workflow-diagram.py`*
"""

    # Запись файла
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Документ сгенерирован: {OUTPUT_FILE.relative_to(REPO_ROOT)}")

    # Подсчёт статусов
    fixed_count = sum(1 for w in workflows if get_status(w["file"])["status"] == "fixed")
    broken_count = sum(1 for w in workflows if get_status(w["file"])["status"] == "broken")

    print("📊 Статистика:")
    print(f"   - Всего workflows: {len(workflows)}")
    print(f"   - Исправлено: {fixed_count}")
    print(f"   - Требует внимания: {broken_count}")


if __name__ == "__main__":
    main()
