"""
Cognitive Automation Agent Package

Автономный интеллектуальный агент для автоматизации разработки и управления проектами.
"""

__version__ = "1.0.0"
__author__ = "Cognitive Automation Agent Team"
__license__ = "MIT"

# Экспорт основных классов
__all__ = [
    "CognitiveAgentLauncher",
    "LearningSystem",
    "Planner",
    "Scanner",
    "TriggerProcessor",
]


# Ленивая загрузка для избежания циклических импортов и проблем с зависимостями
def __getattr__(name):
    if name == "CognitiveAgentLauncher":
        try:
            from .launch_script import CognitiveAgentLauncher

            return CognitiveAgentLauncher
        except (ImportError, ModuleNotFoundError):
            return None
    if name == "LearningSystem":
        try:
            from .scripts.learning_main import LearningSystem

            return LearningSystem
        except (ImportError, ModuleNotFoundError):
            return None
    if name == "Planner":
        try:
            from .scripts.planner_main import Planner

            return Planner
        except (ImportError, ModuleNotFoundError):
            return None
    if name == "Scanner":
        try:
            from .scripts.scanner_main import Scanner

            return Scanner
        except (ImportError, ModuleNotFoundError):
            return None
    if name == "TriggerProcessor":
        try:
            from .scripts.trigger_processor import TriggerProcessor

            return TriggerProcessor
        except (ImportError, ModuleNotFoundError):
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
