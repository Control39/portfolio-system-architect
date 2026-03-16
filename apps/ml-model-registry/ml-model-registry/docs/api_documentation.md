# Документация API ML Model Registry

## Описание

API ML Model Registry предоставляет интерфейс для управления моделями машинного обучения, включая регистрацию, версионирование и развертывание моделей.

## Базовый URL

```
http://localhost:8000/api/v1
```

## Эндпоинты

### Регистрация модели

```
POST /models
```

Регистрирует новую модель в реестре.

**Параметры запроса:**
- `name` (string, обязательный) - имя модели
- `version` (string, обязательный) - версия модели
- `framework` (string) - фреймворк модели (TensorFlow, PyTorch, etc.)
- `metadata` (object) - дополнительные метаданные

**Пример запроса:**
```json
{
  "name": "recommendation_model",
  "version": "1.0.0",
  "framework": "TensorFlow",
  "metadata": {
    "description": "Модель рекомендаций для e-commerce",
    "metrics": {
      "accuracy": 0.92,
      "precision": 0.88
    }
  }
}
```

**Пример ответа:**
```json
{
  "status": "success",
  "model_id": "rec_model_v1_0_0"
}
```

### Получение информации о модели

```
GET /models/{model_id}
```

Получает информацию о зарегистрированной модели.

**Параметры пути:**
- `model_id` (string, обязательный) - идентификатор модели

**Пример ответа:**
```json
{
  "id": "rec_model_v1_0_0",
  "name": "recommendation_model",
  "version": "1.0.0",
  "framework": "TensorFlow",
  "created_at": "2023-01-15T10:30:00Z",
  "metadata": {
    "description": "Модель рекомендаций для e-commerce",
    "metrics": {
      "accuracy": 0.92,
      "precision": 0.88
    }
  }
}
```

### Список моделей

```
GET /models
```

Возвращает список всех зарегистрированных моделей.

**Пример ответа:**
```json
{
  "models": [
    {
      "id": "rec_model_v1_0_0",
      "name": "recommendation_model",
      "version": "1.0.0",
      "framework": "TensorFlow"
    },
    {
      "id": "fraud_model_v2_1_0",
      "name": "fraud_detection_model",
      "version": "2.1.0",
      "framework": "PyTorch"
    }
  ]
}
```

### Удаление модели

```
DELETE /models/{model_id}
```

Удаляет модель из реестра.

**Параметры пути:**
- `model_id` (string, обязательный) - идентификатор модели

**Пример ответа:**
```json
{
  "status": "success",
  "message": "Model rec_model_v1_0_0 deleted"
}