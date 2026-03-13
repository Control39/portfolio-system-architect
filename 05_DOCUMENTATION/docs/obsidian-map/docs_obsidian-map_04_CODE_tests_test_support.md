# 04 Code Tests Test Support

- **Путь**: `docs\obsidian-map\04_CODE_tests_test_support.md`
- **Тип**: .MD
- **Размер**: 858 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# Test Support

- **Путь**: `04_CODE\tests\test_support.py`
- **Тип**: .PY
- **Размер**: 4,150 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
"""
Тесты для модуля психологической поддержки.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.mental.support import PsychologicalSupport
import pytest
from unittest.mock import patch, MagicMock

def test_psychological_support_initialization():
    """Проверяем
... (файл продолжается)
```
