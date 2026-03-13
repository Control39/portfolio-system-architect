## IT-Compass: Пример для разработчика

### Задача
Расширить IT-Compass новым типом маркера для оценки навыков в области ИИ.

### Действие
1. Создать файл `components/it-compass/src/data/markers/ai_skills.json` с определением маркера:
   ```json
   {
     "id": "ai_skills",
     "name": "Навыки ИИ",
     "category": "emerging",
     "levels": ["beginner", "intermediate", "advanced", "expert"]
   }
   ```
2. Добавить логику валидации в `components/it-compass/src/core/tracker.py`:
   ```python
   def validate_ai_marker(self, marker_data):
       # Логика валидации
       pass
   ```
3. Написать тесты в `components/it-compass/tests/test_ai_skills.py`.

### Результат
IT-Compass теперь может оценивать навыки в области ИИ и интегрирован в общую систему маркеров.

