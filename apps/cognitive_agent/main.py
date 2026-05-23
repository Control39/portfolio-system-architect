"""
Cognitive Automation Agent — автономный ИИ-агент для управления проектами.

API:
    GET /health — проверка здоровья
    POST /tasks — создание задачи
    GET /tasks/{id} — получение задачи
"""

from fastapi import FastAPI

app = FastAPI(
    title="Cognitive Automation Agent", description="Автономный ИИ-агент для управления проектами", version="1.0.0"
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cognitive-agent"}


@app.get("/")
async def root():
    return {
        "name": "Cognitive Automation Agent",
        "version": "1.0.0",
        "docs": "/docs",
        "entry": "scripts/scanner_main.py",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
