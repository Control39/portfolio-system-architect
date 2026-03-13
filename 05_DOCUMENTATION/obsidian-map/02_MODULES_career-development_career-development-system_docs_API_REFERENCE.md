# Api Reference

- **Путь**: `02_MODULES\career-development\career-development-system\docs\API_REFERENCE.md`
- **Тип**: .MD
- **Размер**: 1,487 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# API Reference

## Базовый URL
```
http://localhost:5000/api
```

## Пользователи

### Получить список пользователей
```
GET /users
```

**Ответ:**
```json
[
  {
    "id": 1,
    "username": "ivan_petrov",
    "email": "ivan@example.com"
  }
]
```

### Создать пользователя
```
POST /users
```

**Тело запроса:**
```json
{
  "username": "ivan_petrov",
  "email": "ivan@example.com"
}
```

**Ответ:**
```json
{
  "id": 1,
  "username": "ivan_petrov",
  "email": "ivan@example.com"
}
```

### Получить
... (файл продолжается)
```
