"""
Portfolio System Architect - основной пакет проекта.

Этот пакет содержит все компоненты системы архитектора портфолио,
включая AI-агентов, облачные интеграции, системы аудита и мониторинга.
"""

__version__ = "0.1.0"
__author__ = "Lead AI Systems Architect"
__email__ = ""

# Экспорт основных компонентов
# Removed legacy modules (decision_engine_v1, repo_audit_v1), moved to /legacy.
__all__ = [
    "main",
    "shared",
    "ai",
    "security",
    "queues",
]

import os

# Инициализация путей
import sys

# Добавляем src в PYTHONPATH для относительных импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
