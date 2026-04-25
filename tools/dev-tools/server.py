# server.py
import json
import os

import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# === Загрузка конфигурации ===
CONFIG_PATH = ".gigacode/config.json"

if not os.path.exists(CONFIG_PATH):
    print(f"❌ Файл конфигурации не найден: {CONFIG_PATH}")
    print("Создайте его или скопируйте из config.example.json")
    exit(1)

with open(CONFIG_PATH, encoding="utf-8") as f:
    config = json.load(f)

# Загружаем переменные окружения
from dotenv import load_dotenv

load_dotenv()

# Подменяем ключ GigaChat из .env
if config.get("gigachat", {}).get("api_key") == "YOUR_GIGACHAT_TOKEN_HERE":
    key = os.getenv("GIGACHAT_API_KEY")
    if key:
        config["gigachat"]["api_key"] = key
    else:
        print("❌ Не задан GIGACHAT_API_KEY в .env")
        exit(1)

print(f"✅ Активный провайдер: {config['active_provider']}")

# === Модели запросов ===
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    model: str | None = None

# === Роут для чата ===
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    provider = config["active_provider"]

    if provider == "codette":
        # Запрос к Ollama (Codette)
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": config["codette"]["model"],
                    "prompt": request.messages[-1].content,
                    "stream": False,
                },
            )
            data = response.json()
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": data.get("response", "Нет ответа от Codette"),
                        },
                    },
                ],
                "model": config["codette"]["model"],
            }
        except Exception as e:
            return {"error": f"Codette error: {e!s}"}

    elif provider == "gigachat":
        # Запрос к GigaChat API
        try:
            auth_response = requests.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": "unique-request-id",
                    "Authorization": f"Basic {config['gigachat']['api_key']}",
                },
                data={"scope": "GIGACHAT_API_PERS"},
            )
            token = auth_response.json().get("access_token")

            chat_response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "model": config["gigachat"]["model"],
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": 0.7,
                },
            )
            data = chat_response.json()
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": data["choices"][0]["message"]["content"],
                        },
                    },
                ],
                "model": "GigaChat",
            }
        except Exception as e:
            return {"error": f"GigaChat error: {e!s}"}

    else:
        return {"error": f"Unknown provider: {provider}"}

# === Запуск ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081)
