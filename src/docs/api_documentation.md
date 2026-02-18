# Документация API системы управления карьерным развитием

## Общая информация

Этот документ описывает API системы управления карьерным развитием на основе объективных маркеров компетенций.

Базовый URL: `http://localhost:5000/api`

## Пользователи

### Получить список всех пользователей

**Запрос:**
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
  },
  {
    "id": 2,
    "username": "maria_sidorova",
    "email": "maria@example.com"
  }
]
```

### Создать нового пользователя

**Запрос:**
```
POST /users
Content-Type: application/json

{
  "username": "new_user",
  "email": "newuser@example.com"
}
```

**Ответ:**
```json
{
  "id": 3,
  "username": "new_user",
  "email": "newuser@example.com"
}
```

## Навыки пользователей

### Получить навыки пользователя

**Запрос:**
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
  },
  {
    "id": 2,
    "name": "JavaScript",
    "level": 2
  }
]
```

### Добавить навык пользователю

**Запрос:**
```
POST /users/{user_id}/skills
Content-Type: application/json

{
  "name": "Java",
  "level": 4
}
```

**Ответ:**
```json
{
  "id": 3,
  "name": "Java",
  "level": 4
}
```

## Маркеры компетенций

### Получить все маркеры компетенций

**Запрос:**
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
  },
  {
    "id": 2,
    "title": "Продвинутые алгоритмы",
    "description": "Знание сложных алгоритмов и структур данных",
    "required_level": 4
  }
]
```

## Модели данных

### Пользователь (User)

| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | Уникальный идентификатор |
| username | string | Имя пользователя |
| email | string | Email пользователя |

### Навык (Skill)

| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | Уникальный идентификатор |
| name | string | Название навыка |
| level | integer | Уровень навыка (1-10) |

### Маркер компетенции (CompetencyMarker)

| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | Уникальный идентификатор |
| title | string | Название маркера |
| description | text | Описание маркера |
| required_level | integer | Требуемый уровень навыка |