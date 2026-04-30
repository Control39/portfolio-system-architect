import json
import logging
from datetime import datetime


class PortfolioLogger:
    def __init__(self):
        self.logger = logging.getLogger("portfolio")
        self.logger.setLevel(logging.INFO)

        # Настройка форматирования
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_upload(self, filename, size, user_id):
        """Логирование загрузки файла"""
        self.logger.info(
            json.dumps(
                {
                    "event": "file_upload",
                    "filename": filename,
                    "size": size,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

    def log_analysis(self, project_id, analysis_time, result):
        """Логирование анализа"""
        self.logger.info(
            json.dumps(
                {
                    "event": "project_analysis",
                    "project_id": project_id,
                    "analysis_time": analysis_time,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

    def log_error(self, error_type, error_message, context=None):
        """Логирование ошибок"""
        self.logger.error(
            json.dumps(
                {
                    "event": "error",
                    "error_type": error_type,
                    "error_message": error_message,
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )
