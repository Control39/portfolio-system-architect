"""
Repository Audit - модуль аудита репозиториев.

Содержит инструменты для автоматического аудита кода,
проверки качества, безопасности и соответствия стандартам.
"""

__version__ = "0.1.0"
__all__ = ["checks", "cli"]

from .cli import main as audit_main

__all__ += ['audit_main']