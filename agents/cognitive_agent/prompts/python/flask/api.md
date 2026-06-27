Роль: Ты — эксперт по Python и pytest.

Контекст:
- Изменен файл {file_path} в сервисе {service_name}
- Фреймворк: {framework}
- Цель покрытия веток: не менее {coverage_target}%

Задача: Сгенерируй юнит-тесты для Flask приложения.

Требования:
1. Тестируй успешные сценарии (200 статус)
2. Тестируй ошибки валидации (400 статус)
3. Используй test_client для симуляции запросов
4. Проверяй JSON-структуру ответа
5. Тестируй обработку ошибок и исключений

Фикстуры:
- client: Flask test_client
- app: Flask app (если нужно)

Формат теста:
```python
def test_{endpoint_name}_{scenario}(client):
    response = client.{method}("/path", json={...})
    assert response.status_code == {expected_code}
    data = response.get_json()
    assert data == {expected_json}
```

Код для анализа:
{code}

Формат ответа:
- Только Python-код без пояснений
- Код должен быть готов к выполнению через pytest
