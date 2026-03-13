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

### Получить навыки пользователя
```
GET /users/{user_id}/skills
```

**Ответ:**
```json
[
  {
    "id": 1,
    "name": "Python",
    "level": 3
  }
]
```

### Добавить навык пользователю
```
POST /users/{user_id}/skills
```

**Тело запроса:**
```json
{
  "name": "Python",
  "level": 3
}
```

**Ответ:**
```json
{
  "id": 1,
  "name": "Python",
  "level": 3
}
```

## Маркеры компетенций

### Получить все маркеры компетенций
```
GET /markers
```

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Основы программирования",
    "description": "Понимание базовых концепций программирования",
    "required_level": 2
  }
]
