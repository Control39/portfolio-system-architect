"""Общие константы и утилиты для Cognitive Agent."""

import logging
import signal
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Настройка логирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


# Универсальная функция для обработки сигналов завершения
def handle_shutdown(signum, frame):
    """Универсальная функция для обработки сигналов завершения."""
    logger.info("🛑 Получен сигнал остановки...")
    # Тут можно добавить любую логику завершения
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# Константы
APP_NAME = "Cognitive Agent"
VERSION = "0.1.0"
APP_DIR = REPO_ROOT / "apps" / "cognitive_agent"
LOG_DIR = APP_DIR / "logs"
DATA_DIR = APP_DIR / "data"
CONFIG_DIR = APP_DIR / "config"
REPORTS_DIR = APP_DIR / "reports"
SKILLS_DIR = APP_DIR / "skills"
SCRIPTS_DIR = APP_DIR / "scripts"

# Создание directories
for directory in [LOG_DIR, DATA_DIR, CONFIG_DIR, REPORTS_DIR, SKILLS_DIR, SCRIPTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
