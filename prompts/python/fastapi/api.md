Роль: Ты — эксперт по Python и pytest.

Контекст:
- Изменен API-файл {file_path} в сервисе {service_name}
- Фреймворк: {framework}
- Цель покрытия веток: не менее {coverage_target}%

Задача: Сгенерируй набор API-тестов для эндпоинтов FastAPI.

Требования:
1. Тестируй успешные запросы (200, 201 статусы)
2. Тестируй ошибки валидации (422 статус)
3. Тестируй ошибки авторизации (401, 403 статусы)
4. Используй TestClient для симуляции HTTP-запросов
5. Мокай зависимости через dependency_overrides
6. Проверяй JSON-структуру ответа

Фикстуры:
- client: TestClient(app)
- auth_headers: заголовки авторизации (если нужно)
- db_session: тестовая сессия БД (если нужно)

Формат теста:
```python
def test_{endpoint_name}_{scenario}(client):
    response = client.{method}("/path", json={...})
    assert response.status_code == {expected_code}
    assert response.json() == {expected_json}
```

Код для анализа:
{code}

Формат ответа:
- Только Python-код без пояснений
- Код должен быть готов к выполнению через pytest
