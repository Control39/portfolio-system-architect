"""
Запуск сервера Portfolio Organizer API.

Поддерживает режимы разработки (dev) и продакшена (prod),
автозагрузку конфигурации и безопасную инициализацию приложения.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту для корректного импорта
project_root = Path(__file__).parent.parent

# Конфигурация по умолчанию (fallback)
DEFAULT_CONFIG: dict[str, Any] = {
    "automation": {
        "scripts": [
            {
                "name": "run_api",
                "command": [
                    "uvicorn",
                    "apps.portfolio_organizer.endpoints.routes:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                    "--reload",
                ],
            }
        ]
    }
}

COMPONENT_CONFIG = DEFAULT_CONFIG.copy()

try:
    from decision_engine.configs.loader import COMPONENT_CONFIG as LOADED_CONFIG

    if LOADED_CONFIG and isinstance(LOADED_CONFIG, dict):
        COMPONENT_CONFIG = LOADED_CONFIG
        logger.info("Конфигурация успешно загружена из decision_engine")
    else:
        logger.warning("Загруженная конфигурация пуста или неверного типа, используем fallback")
except ImportError as e:
    logger.warning(f"Не удалось загрузить конфигурацию из decision_engine: {e}")
except Exception as e:
    logger.error(f"Неожиданная ошибка при загрузке конфигурации: {e}")


def create_stub_app() -> FastAPI:
    app = FastAPI(
        title="Portfolio Organizer (Stub)",
        description="Заглушечное приложение для Portfolio Organizer API",
        version="1.0.0",
    )

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "Заглушечное приложение", "status": "running", "version": "1.0.0"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy", "service": "portfolio-organizer"}

    return app


web_app: FastAPI | None = None
APP_IMPORT_STRING = "apps.portfolio_organizer.endpoints.routes:app"

try:
    from apps.portfolio_organizer.endpoints.routes import app as imported_app

    if imported_app is None:
        raise ImportError("App is None после импорта")
    web_app = imported_app
    logger.info("FastAPI приложение успешно импортировано")
except ImportError as e:
    logger.warning(f"Не удалось импортировать приложение ({e}). Используем заглушку.")
    web_app = create_stub_app()
    APP_IMPORT_STRING = "__main__:web_app"
except Exception as e:
    logger.error(f"Критическая ошибка при инициализации: {e}")
    web_app = create_stub_app()
    APP_IMPORT_STRING = "__main__:web_app"


def validate_port(port: int) -> bool:
    return 1 <= port <= 65535


def extract_port_from_config() -> int:
    default_port = 8000
    try:
        scripts = COMPONENT_CONFIG.get("automation", {}).get("scripts", [])
        for script in scripts:
            if isinstance(script, dict) and script.get("name") == "run_api":
                command = script.get("command", [])
                if isinstance(command, list) and "--port" in command:
                    idx = command.index("--port")
                    if idx + 1 < len(command) and command[idx + 1].isdigit():
                        port = int(command[idx + 1])
                        if validate_port(port):
                            return port
    except Exception as e:
        logger.warning(f"Ошибка чтения порта из конфига: {e}")
    return default_port


def run_server(host: str, port: int, reload: bool, workers: int | None) -> None:
    if not validate_port(port):
        logger.error(f"Некорректный порт {port}, использую 8000")
        port = 8000

    if reload and workers and workers > 1:
        logger.warning("Режим reload несовместим с multiple workers. Устанавливаю workers=1.")
        workers = 1

    logger.info(f"Запуск сервера: {host}:{port} | Reload: {reload} | Workers: {workers}")

    uvicorn_kwargs: dict[str, Any] = {
        "host": host,
        "port": port,
        "reload": reload,
        "log_level": "info",
        "access_log": True,
        "timeout_keep_alive": 5,
    }

    if reload:
        uvicorn_kwargs["app"] = APP_IMPORT_STRING
        logger.info(f"Dev режим: используем импорт '{APP_IMPORT_STRING}'")
    else:
        if web_app is None:
            raise RuntimeError("FastAPI приложение не инициализировано")
        uvicorn_kwargs["app"] = web_app
        if workers:
            uvicorn_kwargs["workers"] = workers
            logger.info(f"Production режим: {workers} воркеров")

    try:
        uvicorn.run(**uvicorn_kwargs)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        sys.exit(1)


def main(host: str, port: int | None, reload: bool, workers: int | None) -> None:
    final_port = port if port else extract_port_from_config()
    run_server(host, final_port, reload, workers)


def main_dev(host: str, port: int | None) -> None:
    logger.info(">>> Запуск в DEVELOPMENT режиме <<<")
    main(host=host, port=port, reload=True, workers=1)


def main_prod(host: str, port: int | None, workers: int) -> None:
    logger.info(f">>> Запуск в PRODUCTION режиме ({workers} workers) <<<")
    main(host=host, port=port, reload=False, workers=workers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Portfolio Organizer API Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python run_api.py --mode dev
  python run_api.py --mode prod --port 8080 --workers 8
        """,
    )

    parser.add_argument("--mode", choices=["dev", "prod"], default="dev", help="Режим запуска")
    parser.add_argument("--host", default="0.0.0.0", help="Хост сервера")
    parser.add_argument("--port", type=int, default=None, help="Порт (из конфига, если не указан)")
    parser.add_argument("--workers", type=int, default=4, help="Воркеры (только prod)")

    args = parser.parse_args()

    logger.info(
        f"Параметры запуска: режим={args.mode}, host={args.host}, port={args.port or 'auto'}, workers={args.workers}"
    )

    if args.mode == "dev":
        main_dev(host=args.host, port=args.port)
    else:
        main_prod(host=args.host, port=args.port, workers=args.workers)
