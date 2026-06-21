# Директория tests для Cognitive Agent

Эта директория содержит тесты для различных компонентов Cognitive Agent.

## Структура

- [test_base_agent.py](./test_base_agent.py) - Тесты для базового класса агента
- [test_code_analyzer.py](./test_code_analyzer.py) - Тесты для анализатора кода
- [test_documentation_analyzer.py](./test_documentation_analyzer.py) - Тесты для анализатора документации
- [test_test_analyzer.py](./test_test_analyzer.py) - Тесты для анализатора тестов
- [test_project_scanner.py](./test_project_scanner.py) - Тесты для сканера проекта
- [test_guardrails.py](./test_guardrails.py) - Тесты для системы безопасности
- [test_task_planner.py](./test_task_planner.py) - Тесты для планировщика задач
- [integration/](./integration) - Интеграционные тесты
- [e2e/](./e2e) - Тесты сквозного выполнения
- [performance/](./performance) - Тесты производительности

## Основные категории тестов

### Модульные тесты

Тесты для отдельных компонентов агента:
- [test_code_analyzer.py](./test_code_analyzer.py) - Проверяет функциональность анализатора кода
- [test_documentation_analyzer.py](./test_documentation_analyzer.py) - Проверяет функциональность анализатора документации
- [test_test_analyzer.py](./test_test_analyzer.py) - Проверяет функциональность анализатора тестов

### Интеграционные тесты

Тесты взаимодействия между компонентами:
- [integration/](./integration) - Проверяет работу компонентов вместе

### Тесты безопасности

Тесты системы безопасности:
- [test_guardrails.py](./test_guardrails.py) - Проверяет работу системы enterprise-контроля доступа

## Запуск тестов

Для запуска всех тестов:
```bash
pytest tests/ -v
```

Для запуска конкретного теста:
```bash
pytest tests/test_code_analyzer.py -v
```

## Покрытие тестами

Цель - поддерживать покрытие не менее 80% для всех компонентов агента.