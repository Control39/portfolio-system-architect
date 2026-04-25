import uvicorn

from .api.endpoints import app
from .config.loader import COMPONENT_CONFIG


def run_server():
    # Берём команду запуска из конфигурации
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

    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    run_server()

