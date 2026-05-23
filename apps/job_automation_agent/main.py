"""
Job Automation Agent — автоматизация поиска работы и подачи заявок.

API:
    GET /health — проверка здоровья
    POST /jobs/search — поиск вакансий
    POST /jobs/apply — подача заявки
"""

from fastapi import FastAPI

app = FastAPI(title="Job Automation Agent", description="Автоматизация поиска работы и подачи заявок", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "job-automation-agent"}


@app.get("/")
async def root():
    return {"name": "Job Automation Agent", "version": "1.0.0", "docs": "/docs", "entry": "src/main.py"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
