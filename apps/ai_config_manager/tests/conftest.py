"""
Конфигурация pytest для тестов ai-config-manager.
"""

import os
import sys

# Добавляем родительскую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
