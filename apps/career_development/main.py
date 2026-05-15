"""
Career Development API entry point for uvicorn.
"""

import os
import sys


# Добавляем путь к корню проекта (src уже в /app/src благодаря Dockerfile)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.app import app


__all__ = ["app"]
