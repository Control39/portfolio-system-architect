# Components It Compass Tests Test Tracker

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\components_it-compass_tests_test_tracker.md`
- **Тип**: .MD
- **Размер**: 894 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
# Test Tracker

- **Путь**: `components\it-compass\tests\test_tracker.py`
- **Тип**: .PY
- **Размер**: 12,010 байт
- **Последнее изменение**: 2026-03-06 14:43:00

## Превью

```
"""
Тесты для трекера компетенций IT Compass
"""

import unittest
import json
import os
import tempfile
import sys
from datetime import datetime
from unittest.mock import patch, mock_open

# Добавляем путь к модулям IT Compass
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.tracker
... (файл продолжается)
```
