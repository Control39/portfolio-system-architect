# Test Helpers

- **Путь**: `components\career-development-system\src\tests\test_helpers.py`
- **Тип**: .PY
- **Размер**: 5,628 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
import os
import tempfile
from src.utils.helpers import *


class TestHelpers(unittest.TestCase):

    def test_validate_email(self):
        """Тест валидации email"""
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("test@"))
        self.assertFalse(validate_email("@example.com"))

    def test_sanitize_f
... (файл продолжается)
```
