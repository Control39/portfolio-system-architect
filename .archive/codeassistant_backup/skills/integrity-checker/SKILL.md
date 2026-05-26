# Skill: Repository Integrity Checker

## Задачи:
1. **Ссылки**: Проверка всех `[text](url)` в .md на 404/редиректы
2. **Код**: Запуск `python -m assistant_orchestrator --dry-run` для проверки импортов
3. **Бейджи**: Парсинг `README.md`, запрос к каждому URL, фикс сломанных
4. **Дубли**: Поиск идентичных файлов по хешу (кроме examples/)

## Детальная реализация

### 1. Проверка ссылок
```bash
# Установка lychee (если нет)
cargo install lychee

# Запуск проверки
lychee --no-progress --output json --include-mail --include-http --include-https .

# Анализ результатов
python scripts/analyze_links.py --fix-broken
```

**Что проверять:**
- Все `.md`, `.rst`, `.txt` файлы
- Относительные ссылки на существование файлов
- Внешние ссылки на доступность (HTTP 200, 3xx)
- Якорные ссылки (`#section`) на наличие заголовков

### 2. Проверка кода
```bash
# Проверка импортов Python
python -m py_compile src/**/*.py
python -m pylint --errors-only apps/

# Проверка запускаемости
python -m assistant_orchestrator --dry-run
python -m pytest --collect-only > /dev/null
```

**Что проверять:**
- Отсутствие синтаксических ошибок
- Корректность импортов
- Доступность зависимостей
- Соответствие типов (mypy)

### 3. Проверка бейджей
```python
# Псевдокод проверки
import re
import requests

def check_badges(readme_path):
    with open(readme_path) as f:
        content = f.read()
    
    badges = re.findall(r'!\[.*?\]\((.*?)\)', content)
    for badge_url in badges:
        try:
            resp = requests.head(badge_url, timeout=5)
            if resp.status_code != 200:
                print(f"Сломан бейдж: {badge_url}")
        except:
            print(f"Ошибка доступа: {badge_url}")
```

**21 обязательных бейджа:**
1. CI Status
2. Test Coverage
3. License
4. Python Version
5. Docker
6. Code Quality
7. Documentation
8. Dependencies
9. Security
10. Code Style
11. Linting
12. Type Checking
13. Performance
14. Compatibility
15. Last Commit
16. Stars
17. Forks
18. Issues
19. PRs
20. Releases
21. Downloads

### 4. Поиск дубликатов
```bash
# Поиск по хешу SHA256
find . -type f -not -path "./.git/*" -not -path "./examples/*" -exec sha256sum {} \; | sort | uniq -w64 -d
```

**Исключения:**
- Файлы в `.git/`
- Примеры в `examples/`, `samples/`
- Логи, кэши, временные файлы
- Лицензионные копии (если нужно)

## Авто-фикс:
- **Битые ссылки** → предложить актуальный путь или удалить
- **Сломанные бейджи** → обновить URL или заменить на статичный
- **Дубли** → предложить удалить с сохранением истории в git
- **Ошибки импорта** → предложить исправление через `scripts/fix_imports.py`

## Интеграция в CI:
```yaml
- name: Integrity Check
  run: |
    python scripts/check_integrity.py --fix --report
    if [ -f "integrity_report.json" ]; then
      python scripts/create_issues.py integrity_report.json
    fi

- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: integrity-report
    path: integrity_report.json
```

## Формат отчёта:
```json
{
  "timestamp": "2024-04-10T02:26:00Z",
  "links": {
    "total": 450,
    "broken": [
      {"url": "https://old-example.com", "file": "README.md", "line": 42}
    ],
    "redirects": 3
  },
  "code": {
    "import_errors": [],
    "syntax_errors": [],
    "test_errors": ["test_edge_case.py::test_failure"]
  },
  "badges": {
    "total": 21,
    "broken": ["https://img.shields.io/badge/coverage-85%25-green"],
    "working": 20
  },
  "duplicates": {
    "found": 2,
    "files": [
      ["docs/old/README.md", "docs/new/README.md"]
    ]
  }
}
```

## Планировщик:
- Ежедневный запуск в 02:00 UTC
- Уведомление в Slack при обнаружении критических проблем
- Автоматическое создание Issues для broken links
- Еженедельный отчёт в `docs/integrity-reports/`