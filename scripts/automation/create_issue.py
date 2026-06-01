#!/usr/bin/env python
"""Скрипт для создания GitHub Issue через API."""

import os

import requests


GITHUB_TOKEN = os.getenv("GH_TOKEN", os.getenv("GITHUB_TOKEN"))
REPO_OWNER = "Control39"
REPO_NAME = "portfolio-system-architect"

TITLE = "📝 Documentation: Audit & Refactoring Case for mcp-server"

BODY = """## 1️⃣ ЗАПРОС (REQUEST)

Провести глубокий аудит микросервиса `apps/mcp-server` после глобальной реорганизации репозитория. Выполнить статический анализ импортов без выполнения кода.

Цель: выявить нарушения импортов, отсутствующие модули и архитектурные проблемы перед интеграцией в CI/CD.

---

## 2️⃣ ОТЧЕТ (REPORT)

**Найдено 5 критических проблем:**

| № | Тип проблемы | Описание |
|---|--------------|----------|
| 1 | ModuleNotFoundError | `No module named 'navigation'` |
| 2 | ModuleNotFoundError | `No module named 'command_tools'` |
| 3 | ModuleNotFoundError | `No module named 'src.shared.llm'` |
| 4 | Архитектурная ошибка | Дублирование инициализации `FastMCP()` в main.py |
| 5 | Зависимости | Отсутствуют явные зависимости в requirements.txt |

**Отсутствующие файлы:**
- `apps/mcp-server/navigation.py` — модуль навигации
- `apps/mcp-server/command_tools.py` — модуль команд
- `src/shared/llm/__init__.py` — требуется проверка

**Критическая проблема:** Дублирование экземпляров FastMCP (строки 20 и 35 в main.py) — может привести к конфликтам регистрации инструментов.

---

## 3️⃣ ИТОГИ И СЛЕДУЮЩИЕ ШАГИ (ACTION ITEMS)

**Создан документ кейса:**
📄 [cases/refactoring_experience/01_mcp_server_audit.md](cases/refactoring_experience/01_mcp_server_audit.md)

**План действий:**
- [ ] Исправить импорты в main.py
- [ ] Унифицировать инициализацию tools (init_tools(), init_llm())
- [ ] Устранить дублирование FastMCP — оставить один экземпляр
- [ ] Создать отсутствующие модули или переписать импорты
- [ ] Обновить requirements.txt с явными зависимостями
- [ ] Добавить sys.path управление для кроссплатформенности
- [ ] Написать тесты инициализации
- [ ] Добавить pre-commit hook для проверки импортов

**Метрики:** 5 критических проблем → 0 после рефакторинга

---

*Кейс создан в рамках процесса обеспечения качества Portfolio System Architect.*
"""

LABELS = ["documentation", "architecture", "audit"]


def create_issue():
    if not GITHUB_TOKEN:
        print("Ошибка: установите переменную GH_TOKEN или GITHUB_TOKEN")
        return

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": TITLE,
        "body": BODY,
        "labels": LABELS,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        issue_url = response.json()["html_url"]
        print(f"✅ Issue создан: {issue_url}")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")


if __name__ == "__main__":
    create_issue()
