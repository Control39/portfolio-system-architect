import json
import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GIGA IDE MCP Server", version="1.0.0")


class PromptRequest(BaseModel):
    prompt: str
    variables: Dict[str, Any] = {}
    rules: List[str] = []


class PromptResponse(BaseModel):
    result: str
    processed_rules: List[str] = []
    metadata: Dict[str, Any] = {}


def load_rules():
    """Загрузка правил из файла"""
    try:
        with open("rules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("rules.json not found, using default rules")
        return {
            "default_rules": [
                "Follow project conventions",
                "Prioritize security best practices",
                "Use clear and concise code",
                "Add comments only when necessary",
            ]
        }
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
        return {"default_rules": []}


@app.get("/")
async def root():
    """Проверка состояния сервера"""
    return {"status": "running", "message": "GIGA IDE MCP Server is operational"}


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "healthy"}


@app.post("/process-prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    """Обработка промпта с применением правил"""
    try:
        logger.info(f"Processing prompt: {request.prompt[:100]}...")

        # Загружаем правила
        rules = load_rules()
        applied_rules = []

        # Применяем правила к промпту
        processed_prompt = request.prompt

        # Если в запросе указаны правила, используем их
        if request.rules:
            applied_rules = request.rules
        else:
            # Используем правила по умолчанию
            applied_rules = rules.get("default_rules", [])

        # Простая обработка промпта (в реальности здесь будет более сложная логика)
        result = f"Processed: {processed_prompt}"

        # Добавляем информацию о примененных правилах
        metadata = {
            "prompt_length": len(request.prompt),
            "rule_count": len(applied_rules),
            "variables_count": len(request.variables),
        }

        logger.info(f"Prompt processed successfully with {len(applied_rules)} rules")

        return PromptResponse(result=result, processed_rules=applied_rules, metadata=metadata)

    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/rules")
async def get_rules():
    """Получение списка доступных правил"""
    try:
        rules = load_rules()
        return rules
    except Exception as e:
        logger.error(f"Error retrieving rules: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve rules") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
