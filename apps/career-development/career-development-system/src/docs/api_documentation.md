# API Documentation

## Overview
All endpoints are served by a **FastAPI** application (`src/api/app.py`).  
The OpenAPI schema is automatically available at `/openapi.json` and the Swagger UI at `/docs`.

## Endpoints Detail

### GET `/`
```json
{
  "message": "Career Development System API is running"
}
```

### GET `/profile`
- **Response** – полная структура `UserProfile` в JSON.

### POST `/goals`
```json
{
  "title": "Become senior architect",
  "description": "Lead 3 large‑scale projects",
  "target_date": "2027-12-31"
}
```
- **Response** – статус создания.

### PATCH `/markers/{marker_id}`
```json
{
  "status": "in_progress"
}
```
- **Response** – подтверждение обновления.

### GET `/evidence/export`
- **Response** – путь к готовому ZIP‑архиву с доказательствами (PDF/MD).

### GET `/progress`
- **Response**
```json
{
  "progress": 73.5
}
```

*Все запросы требуют **Bearer Token** (встроена в `AuthMiddleware` вашего проекта).*

