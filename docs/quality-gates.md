# Quality Gates: Чек-лист проверки автоматизации

## 1. CI/CD (GitHub Actions)
```bash
gh run list --limit 5
```

## 2. Pre-commit хуки
```bash
pre-commit run --all-files
```

## 3. Тесты
```bash
pytest tests/ -v --tb=short
pytest --cov=. --cov-report=term
```

## 4. Линтеры
```bash
ruff check apps/ --statistics
black --check apps/
```

## 5. Type Checking
```bash
pyright apps/ --stats
```

## 6. Безопасность
```bash
trivy fs . --severity HIGH,CRITICAL --exit-code 0
bandit -r apps/ -ll
```

## 7. Импорты и синтаксис
```bash
find apps src -name "*.py" -exec python -m py_compile {} \; 2>&1 | head -20
grep -r "from src\.cloud_reason" --include="*.py" . 2>/dev/null || echo "✅ OK"
```

## 8. Docker сборка
```bash
docker build -f apps/cloud-reason/Dockerfile -t test-cloud-reason . --no-cache --dry-run
docker-compose config
```

## 9. Makefile команды
```bash
make test
make lint
```

## 10. Документация
```bash
mkdocs build --strict

