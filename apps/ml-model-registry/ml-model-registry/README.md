# ML Model Registry

Реестр моделей машинного обучения с отказоустойчивостью и расширенным тестированием.

## Статус

![CI](https://github.com/leadarchitect-ai/portfolio-system-architect/workflows/CI/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## Описание

Этот компонент предоставляет реализацию реестра моделей машинного обучения с расширенными возможностями тестирования:

- Отказоустойчивость при сбоях компонентов
- Fuzz-тестирование для выявления неожиданных поведений
- Контрактные тесты для обеспечения совместимости интерфейсов
- Визуализация покрытия кода
- Анализ мутаций для подтверждения качества тестов

## Установка

```bash
pip install -r requirements.txt
```

## Использование

```python
from src.core.model_registry import ModelRegistry

registry = ModelRegistry()
registry.register_model("my_model", {"name": "My Model", "version": "1.0"})
```

## Тестирование

Для запуска всех тестов выполните:

```bash
python -m unittest discover tests
```

### Типы тестов

- **Модульные тесты**: `test_model_registry.py`
- **Тесты отказоустойчивости**: `test_resilience.py`
- **Fuzz-тесты**: `test_fuzz.py`
- **Контрактные тесты**: `test_contract.py`

## Лицензия

MIT