"""
Модуль скриптов Cognitive Automation Agent.

Содержит основные компоненты агента: сканер, планировщик, систему обучения и обработчик триггеров.
"""

# Ленивый импорт для избежания проблем с зависимостями в CI
# Импорты выполняются только при явном обращении к классам


def __getattr__(name):
    """Ленивая загрузка модулей."""
    if name == "LearningSystem":
        from .learning_main import LearningSystem
        return LearningSystem
    if name == "TaskPlanner":
        from .planner_main import TaskPlanner
        return TaskPlanner
    if name == "Scanner":
        from .scanner_main import Scanner
        return Scanner
    if name == "TriggerProcessor":
        from .trigger_processor import TriggerProcessor
        return TriggerProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Scanner",
    "TaskPlanner",
    "LearningSystem",
    "TriggerProcessor",
]
