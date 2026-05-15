"""
Конфигурация для тестов auth_service
"""

import os


# Устанавливаем переменные окружения ДО импорта модулей
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
