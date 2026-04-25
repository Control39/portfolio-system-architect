"""Portfolio System Architect - основной пакет проекта.

Этот пакет содержит все компоненты системы архитектора портфолио,
включая AI-агентов, облачные интеграции, системы аудита и мониторинга.
"""

__version__ = "0.1.0"
__author__ = "Lead AI Systems Architect"
__email__ = ""

# Экспорт основных компонентов
__all__ = [
    "ai",
    "decision_engine",
    "main",
    "queues",
    "repo_audit",
    "security",
    "shared",
]

# Инициализация путей
import os
import sys

# Добавляем src в PYTHONPATH для относительных импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
