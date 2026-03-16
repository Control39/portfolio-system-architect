# Test Competency Tracker

- **Путь**: `components\career-development-system\src\tests\test_competency_tracker.py`
- **Тип**: .PY
- **Размер**: 5,808 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import unittest
from src.core.competency_tracker import CompetencyTracker


class TestCompetencyTracker(unittest.TestCase):

    def setUp(self):
        """Настройка тестового окружения"""
        self.tracker = CompetencyTracker()
        self.user_id = "user_001"

        # Добавляем тестового пользователя
        self.tracker.add_user(self.user_id, "Тестовый Пользователь", "test@example.com")

        # Добавляем тестовые маркеры компетенций
        self.tracker.add_competency_marker(
      
... (файл продолжается)
```
