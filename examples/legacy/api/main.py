"""FastAPI сервер для AI-консультанта по архитектуре.
Предоставляет RAG-based API для ответов на вопросы о проекте.
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.assistant_orchestrator.plugins.rag_advisor import RAGAdvisor

app = FastAPI(
    title="Architect Assistant API",
    description="AI-консультант по архитектуре проекта с RAG-поиском",
    version="1.0.0",
)

logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    query: str
    top_k: int = 3
    min_confidence: float = 0.3


class SourceItem(BaseModel):
    file: str
    text: str
    score: float
    line_start: int | None = None
    line_end: int | None = None


class AnswerResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: list[SourceItem]
    processing_time_ms: float


# Инициализируем RAGAdvisor
project_root = Path(__file__).parent.parent
rag_advisor = RAGAdvisor(project_root)


@app.post("/ask", response_model=AnswerResponse)
async def ask_architecture_question(request: QuestionRequest):
    """Задать вопрос о проекте и получить ответ на основе RAG-поиска."""
    import time

    start_time = time.time()

    try:
        # Используем RAGAdvisor для получения ответа
        result = rag_advisor.ask(
            question=request.query,
            top_k=request.top_k,
            min_confidence=request.min_confidence,
        )

        processing_time_ms = (time.time() - start_time) * 1000

        # Форматируем источники
        sources = []
        if result.get("sources"):
            for src in result["sources"]:
                sources.append(
                    SourceItem(
                        file=src.get("file", "unknown"),
                        text=src.get("text", ""),
                        score=src.get("score", 0.0),
                        line_start=src.get("line_start"),
                        line_end=src.get("line_end"),
                    )
                )

        return AnswerResponse(
            question=request.query,
            answer=result.get("answer", "Не удалось получить ответ."),
            confidence=result.get("confidence", 0.0),
            sources=sources,
            processing_time_ms=processing_time_ms,
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        processing_time_ms = (time.time() - start_time) * 1000
        return AnswerResponse(
            question=request.query,
            answer=f"Ошибка при обработке вопроса: {e!s}",
            confidence=0.0,
            sources=[],
            processing_time_ms=processing_time_ms,
        )


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    try:
        index_ready = rag_advisor.is_index_ready()
        return {
            "status": "healthy",
            "index_ready": index_ready,
            "service": "architect-assistant-api",
            "version": "1.0.0",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "architect-assistant-api",
        }


@app.get("/stats")
async def get_stats():
    """Получить статистику по индексу."""
    try:
        stats = rag_advisor.get_index_stats()
        return {
            "status": "success",
            "stats": stats,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
