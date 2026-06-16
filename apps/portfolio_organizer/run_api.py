#!/usr/bin/env python
"""
Запуск сервера Portfolio Organizer API.
Точка входа сервиса.
"""

import argparse
import logging
import os
import signal
import sys

# 🔴 КРИТИЧНОЕ ИЗМЕНЕНИЕ ДЛЯ ADR-022: Проверка PYTHONPATH
PYTHONPATH = os.environ.get("PYTHONPATH")


# Используем sys.stderr для вывода до инициализации логгера
def log_error(msg):
    print(f"ERROR: {msg}", file=sys.stderr)


if not PYTHONPATH:
    log_error(
        "⚠️ PYTHONPATH не установлен. Установите: PYTHONPATH=/app:/app/src (Docker) или PYTHONPATH=.:src:apps:agents (локально)"
    )
    sys.exit(1)

# Допускаем Docker-путь (/app) ИЛИ локальный путь (корень проекта + поддиректории)
_is_docker = "/app" in PYTHONPATH
_has_src = "/src" in PYTHONPATH or "src" in PYTHONPATH
_has_apps = "/apps" in PYTHONPATH or "apps" in PYTHONPATH

if not _is_docker and (not _has_src or not _has_apps):
    log_error(f"❌ PYTHONPATH должен содержать пути к 'src' и 'apps'. Получено: {PYTHONPATH}")
    sys.exit(1)

# 1. Настройка логирования (без force=True, чтобы не ломать библиотечный лог)
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("portfolio_organizer")

# 2. Конфигурация сервиса
SERVICE_NAME = "portfolio_organizer"
DEFAULT_HOST = os.environ.get("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces is intentional for container
DEFAULT_PORT = 8004  # Наш выделенный порт

# 3. Инициализация приложения
# ВАЖНО: Импорт указывает на новую структуру endpoints/routes.py
try:
    from apps.portfolio_organizer.endpoints.routes import app as imported_app

    logger.info(f"✅ Приложение {SERVICE_NAME} успешно инициализировано")
    web_app = imported_app
except ImportError as e:
    # Fallback для разработки, если эндпоинты еще не готовы
    logger.warning(f"⚠️ Не удалось импортировать эндпоинты ({e}). Создаем stub.")
    from fastapi import FastAPI  # Добавлен импорт FastAPI

    app = FastAPI(title=f"{SERVICE_NAME} (Stub)", version="1.0.0")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": SERVICE_NAME}

    web_app = app


# --- Graceful Shutdown ---
def handle_sigterm(signum, frame):
    logger.info(f"🛑 Получен сигнал {signal.Signals(signum).name}. Завершение работы...")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


# --- Запуск ---
def run_server(host: str, port: int, mode: str, workers: int) -> None:
    """Запуск Uvicorn с настройками окружения."""

    # Интеграция с общей телеметрией (если доступна)
    try:
        from src.common.telemetry import setup_telemetry

        setup_telemetry(SERVICE_NAME)
        logger.info("🔭 OpenTelemetry инициализирован")
    except ImportError:
        logger.warning("🔭 src.common.telemetry не найден. Трейсинг отключен.")

    is_dev = mode == "dev"

    # Проверка несовместимости
    if is_dev and workers > 1:
        logger.warning("⚠️ Режим reload несовместим с воркерами. Устанавливаем workers=1.")
        workers = 1

    import uvicorn  # Добавлен импорт uvicorn

    uvicorn.run(
        app="apps.portfolio_organizer.endpoints.routes:app" if is_dev else web_app,
        host=host,
        port=port,
        reload=is_dev,
        workers=workers if not is_dev else 1,
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
        timeout_keep_alive=5,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{SERVICE_NAME} API Runner")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("SERVICE_PORT", DEFAULT_PORT))
    )  # Исправлено: os.getenv → os.environ.get
    parser.add_argument("--workers", type=int, default=4)

    args = parser.parse_args()
    logger.info(f"🚀 Запуск: mode={args.mode}, port={args.port}, workers={args.workers}")
    run_server(args.host, args.port, args.mode, args.workers)


if __name__ == "__main__":
    main()
