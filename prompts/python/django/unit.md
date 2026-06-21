Роль: Ты — эксперт по Python и pytest.

Контекст: 
- Изменен файл {file_path} в сервисе {service_name}
- Фреймворк: {framework}
- Цель покрытия веток: не менее {coverage_target}%

Задача: Сгенерируй юнит-тесты для Django приложения.

Требования:
1. Используй TestCase или TransactionTestCase
2. Тестируй модели, views, forms
3. Используй Client для симуляции HTTP-запросов
4. Проверяй HTTP-статусы и HTML-содержимое
5. Тестируй обработку ошибок

Фикстуры:
- client: Django test Client
- factory: Django model factory

Формат теста:
```python
from django.test import TestCase
from django.urls import reverse

class {ModelName}Test(TestCase):
    def test_{action}_{scenario}(self):
        response = self.client.{method}("/path")
        self.assertEqual(response.status_code, {expected_code})
        # assertions
```

Код для анализа:
{code}

Формат ответа:
- Только Python-код без пояснений
- Используй Django test utilities