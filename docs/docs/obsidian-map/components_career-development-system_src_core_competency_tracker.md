# Competency Tracker

- **Путь**: `components\career-development-system\src\core\competency_tracker.py`
- **Тип**: .PY
- **Размер**: 5,824 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
class CompetencyTracker:
    """Класс для отслеживания компетенций и карьерного развития"""

    def __init__(self):
        self.users = {}
        self.competency_markers = {}

    def add_user(self, user_id, username, email):
        """Добавить пользователя в систему"""
        self.users[user_id] = {
            "username": username,
            "email": email,
            "skills": {},
            "progress_history": [],
        }

    def add_skill(self, user_id, skill_name, level=1):
   
... (файл продолжается)
```

