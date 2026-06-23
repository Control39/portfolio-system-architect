#!/usr/bin/env python3
"""
Генерация отчёта по TODO-комментариям в проекте

Использование:
    python scripts/generate_todo_report.py
    python scripts/generate_todo_report.py --output .reports/todos/todos_2026-05-27.md
"""

import argparse
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def find_todos(project_path: Path, extensions: list[str] = None) -> list[dict]:
    """Найти все TODO-комментарии в проекте"""
    if extensions is None:
        extensions = [".py", ".ps1", ".js", ".ts"]
    todos = []

    pattern = re.compile(r"#\s*TODO[:\s]+(.+)", re.IGNORECASE)

    for ext in extensions:
        for file_path in project_path.rglob(f"*{ext}"):
            # Пропускаем игнорируемые директории
            if any(part in str(file_path) for part in [".venv", "__pycache__", "node_modules", ".git"]):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        match = pattern.search(line)
                        if match:
                            todos.append(
                                {
                                    "file": str(file_path.relative_to(project_path)),
                                    "line": line_num,
                                    "message": match.group(1).strip(),
                                    "content": line.strip(),
                                }
                            )
            except Exception as e:
                print(f"⚠️  Ошибка чтения {file_path}: {e}")

    return todos


def group_todos(todos: list[dict]) -> dict[str, list[dict]]:
    """Группировать TODO по файлам/сервисам"""
    grouped = defaultdict(list)

    for todo in todos:
        # Извлекаем сервис из пути (например, agents/cognitive_agent/... -> cognitive_agent)
        parts = todo["file"].split(os.sep)
        service = parts[1] if len(parts) > 1 and parts[0] == "apps" else "root"

        grouped[service].append(todo)

    return dict(grouped)


def generate_report(todos: list[dict], output_path: Path = None):
    """Генерация Markdown-отчёта"""
    grouped = group_todos(todos)

    lines = [
        "# Отчёт по TODO-комментариям",
        "",
        f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Всего TODO:** {len(todos)}",
        f"**Сервисов:** {len(grouped)}",
        "",
        "## Сводка по сервисам",
        "",
        "| Сервис | Количество TODO |",
        "|--------|-----------------|",
    ]

    for service, service_todos in sorted(grouped.items(), key=lambda x: -len(x[1])):
        lines.append(f"| {service} | {len(service_todos)} |")

    lines.extend(
        [
            "",
            "## Детальный отчёт",
            "",
        ]
    )

    for service, service_todos in sorted(grouped.items(), key=lambda x: -len(x[1])):
        lines.extend(
            [
                f"### {service} ({len(service_todos)} TODO)",
                "",
            ]
        )

        for todo in service_todos:
            lines.append(f"- **{todo['file']}:{todo['line']}** — {todo['message']}")

        lines.append("")

    report = "\n".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Отчёт сохранён: {output_path}")
    else:
        print(report)

    return report


def main():
    parser = argparse.ArgumentParser(description="Генерация отчёта по TODO-комментариям")
    parser.add_argument("--output", "-o", help="Путь к файлу отчёта")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")

    args = parser.parse_args()

    print(f"🔍 Поиск TODO в: {REPO_ROOT}")

    todos = find_todos(REPO_ROOT)
    print(f"✅ Найдено TODO: {len(todos)}")

    if args.json:
        import json

        print(json.dumps(todos, indent=2, ensure_ascii=False))
    else:
        output_path = Path(args.output) if args.output else None
        generate_report(todos, output_path)


if __name__ == "__main__":
    main()
