# Run Tests

- **Путь**: `scripts\python scripts\run_tests.sh`
- **Тип**: .SH
- **Размер**: 334 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
#!/bin/bash
# Получаем директорию тестов из конфигурации
TEST_DIR=$(python -c "import yaml; c=yaml.safe_load(open('component-config.yaml')); print(c['tests']['directory'])")

echo "Запуск тестов в: $TEST_DIR"
pytest $TEST_DIR -v --cov=components/cloud-reason --cov-report=html

```
