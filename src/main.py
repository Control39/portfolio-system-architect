import os
import sys

import uvicorn

# Добавляем путь к проекту для корректного импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Пробуем импортировать из decision_engine.decision_engine.configs.loader
    from decision_engine.decision_engine.configs.loader import COMPONENT_CONFIG
except ImportError:
    # Fallback: создаем простую конфигурацию
    COMPONENT_CONFIG = {
        "automation": {
            "scripts": [
                {
                    "name": "run_api",
                    "command": "uvicorn api.endpoints:app --host 0.0.0.0 --port 8000 --reload",
                },
            ],
        },
    }
    print("Внимание: Используется fallback конфигурация. Убедитесь, что component-config.yaml существует.")

try:
    from apps.portfolio_organizer.src.endpoints import app
except ImportError:
    print("Ошибка: Не удалось импортировать app из api.endpoints")
    print("Создаем заглушечное FastAPI приложение")
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    def root():
        return {"message": "Заглушечное приложение"}

def main():
    """Основная функция для запуска сервера в production-режиме."""
    try:
        api_script = next(
            script for script in COMPONENT_CONFIG["automation"]["scripts"]
            if script["name"] == "run_api"
        )
        print(f"Запуск API: {api_script['command']}")

        # Извлекаем порт из команды (если указан)
        port = 8000  # дефолтный порт
        if "--port" in api_script["command"]:
            port_str = api_script["command"].split("--port")[1].strip().split()[0]
            port = int(port_str)
    except (KeyError, StopIteration):
        print("Внимание: Конфигурация run_api не найдена, используем порт по умолчанию 8000")
        port = 8000

    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)  # nosec: bound in container, not exposed externally


def main_dev():
    """Функция для запуска сервера в development-режиме с возможностью перезагрузки."""
    try:
        api_script = next(
            script for script in COMPONENT_CONFIG["automation"]["scripts"]
            if script["name"] == "run_api"
        )
        print(f"Запуск API: {api_script['command']}")

        # Извлекаем порт из команды (если указан)
        port = 8000  # дефолтный порт
        if "--port" in api_script["command"]:
            port_str = api_script["command"].split("--port")[1].strip().split()[0]
            port = int(port_str)
    except (KeyError, StopIteration):
        print("Внимание: Конфигурация run_api не найдена, используем порт по умолчанию 8000")
        port = 8000

    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)  # nosec: dev mode, bound in container


if __name__ == "__main__":
    main_dev()  # Запускаем в режиме разработки по умолчанию

