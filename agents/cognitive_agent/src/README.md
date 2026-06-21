# Директория src для Cognitive Agent

Эта директория содержит исходный код основных компонентов Cognitive Agent.

## Структура

- [base_agent.py](./base_agent.py) - Базовый класс агента с общей функциональностью
- [code_analyzer.py](./code_analyzer.py) - Модуль анализа качества кода (интеграция с MyPy, Ruff, Bandit, Pyright, Coverage)
- [documentation_analyzer.py](./documentation_analyzer.py) - Модуль анализа документации (проверка docstring'ов, структуры Markdown)
- [test_analyzer.py](./test_analyzer.py) - Модуль анализа тестов (поиск файлов тестов, оценка качества и покрытия)
- [project_scanner.py](./project_scanner.py) - Сканер проекта для обнаружения файлов и структуры
- [logging_config.py](./logging_config.py) - Конфигурация логирования
- [task_planner.py](./task_planner.py) - Планировщик задач
- [task_planner_enhanced.py](./task_planner_enhanced.py) - Улучшенный планировщик задач
- [api/](./api) - API endpoints для агента

## Основные компоненты

### Анализаторы

Агент включает три ключевых анализатора для оценки качества проекта:

1. **Анализатор кода** ([code_analyzer.py](./code_analyzer.py)) - Проверяет типизацию, стиль кода, безопасность и покрытие тестами
2. **Анализатор документации** ([documentation_analyzer.py](./documentation_analyzer.py)) - Проверяет наличие и качество docstring'ов и структуру документации
3. **Анализатор тестов** ([test_analyzer.py](./test_analyzer.py)) - Оценивает структуру, качество и покрытие тестов

### Базовый класс

[base_agent.py](./base_agent.py) содержит базовую функциональность, общую для всех версий агента, включая интеграцию с анализаторами качества.

## Использование

Компоненты в этой директории используются внутри агента и не предназначены для прямого использования вне его.
