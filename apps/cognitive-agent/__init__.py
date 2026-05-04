"""
Cognitive Automation Agent Package

Автономный интеллектуальный агент для автоматизации разработки и управления проектами.
"""

__version__ = "1.0.0"
__author__ = "Cognitive Automation Agent Team"
__license__ = "MIT"

# Lazy imports to avoid circular dependencies
try:
    from .scripts.learning_main import LearningSystem
except (ImportError, ModuleNotFoundError):
    LearningSystem = None

try:
    from .scripts.planner_main import Planner
except (ImportError, ModuleNotFoundError):
    Planner = None

try:
    from .scripts.scanner_main import Scanner
except (ImportError, ModuleNotFoundError):
    Scanner = None

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
        try:
            from .launch_script import CognitiveAgentLauncher
            return CognitiveAgentLauncher
        except (ImportError, ModuleNotFoundError):
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
