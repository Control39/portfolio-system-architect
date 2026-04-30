"""
Cognitive Automation Agent Package

Автономный интеллектуальный агент для автоматизации разработки и управления проектами.
"""

__version__ = "1.0.0"
__author__ = "Cognitive Automation Agent Team"
__license__ = "MIT"

from .scripts.learning_main import LearningSystem
from .scripts.planner_main import Planner

# Импорт основных компонентов для удобного доступа
from .scripts.scanner_main import Scanner
from .scripts.trigger_processor import TriggerProcessor

# Экспорт основных классов
__all__ = [
    "Scanner",
    "Planner",
    "LearningSystem",
    "TriggerProcessor",
    "CognitiveAgentLauncher",
]


# Ленивая загрузка для избежания циклических импортов
def __getattr__(name):
    if name == "CognitiveAgentLauncher":
        from .launch_script import CognitiveAgentLauncher

        return CognitiveAgentLauncher
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
