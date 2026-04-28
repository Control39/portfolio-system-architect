import os

import uvicorn
from dotenv import load_dotenv

from .api.endpoints import app
from .config.loader import COMPONENT_CONFIG

load_dotenv()


def run_server():
    # Берём команду запуска из конфигурации
    api_script = next(
        script
        for script in COMPONENT_CONFIG["automation"]["scripts"]
        if script["name"] == "run_api"
    )

    print(f"Запуск API: {api_script['command']}")

    # Извлекаем порт из команды (если указан)
    port = 8000  # дефолтный порт
    if "--port" in api_script["command"]:
        port_str = api_script["command"].split("--port")[1].strip().split()[0]
        port = int(port_str)

    # Безопасный хост: только localhost для production
    # DEBUG=true разрешает доступ со всех интерфейсов (для разработки)
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    # Для продакшена всегда используем localhost
    # В режиме отладки можно разрешить доступ с других интерфейсов через DEBUG_BIND_ALL=true
    bind_all = os.getenv("DEBUG_BIND_ALL", "false").lower() == "true"
    host = "0.0.0.0" if debug_mode and bind_all else "127.0.0.1"
    reload = debug_mode  # reload только для разработки

    print(f"🔒 Host: {host} ({'development' if debug_mode else 'production'} mode)")
    print(f"📡 Port: {port}")
    print(f"🔄 Reload: {reload}")

    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server()
