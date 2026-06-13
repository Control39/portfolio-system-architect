#!/usr/bin/env python3
"""
IT Compass Scanner - Сканирование артефактов проекта

Интеграция:
1. Загружает маркеры из apps/it_compass/src/data/markers/ (CareerTracker)
2. Сканирует проект на наличие артефактов
3. Передаёт прогресс в Job Automation Agent (не генерирует вакансии!)

Автор методологии: Ekaterina Kudelya (CC BY-ND 4.0)
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).parent.parent.parent.parent

from apps.it_compass.src.core.tracker import CareerTracker

logs_dir = REPO_ROOT / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "it_compass_scanner.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ITCompassScanner:
    """Сканирует проект и передаёт данные в Job Automation Agent"""

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else REPO_ROOT
        self.it_compass_core = self.project_path / "apps" / "it_compass"
        self.markers_dir = self.it_compass_core / "src" / "data" / "markers"
        self.compass_dir = self.project_path / "it_compass"
        self.progress_file = self.compass_dir / "progress.json"

        # CareerTracker (авторская реализация)
        self.tracker = CareerTracker()

        # Job Automation Agent API
        self.job_agent_url = os.getenv("JOB_AGENT_URL", "http://localhost:8005")

        logger.info("🧭 IT Compass Scanner initialized")
        logger.info(f"📁 Project: {self.project_path}")
        logger.info(f"📚 Markers: {self.markers_dir}")
        logger.info("👤 Author: Ekaterina Kudelya (CC BY-ND 4.0)")
        logger.info("⚠️  NOTE: Passes data to Job Agent, does NOT generate jobs")

    def scan_project(self) -> Dict[str, Any]:
        """Сканировать проект и передать данные в Job Agent"""
        logger.info("🔍 Starting IT Compass scan...")

        scan_start = datetime.now()

        # 1. Получаем прогресс из CareerTracker
        tracker_progress = self.tracker.calculate_progress()

        # 2. Сканируем артефакты
        artifacts = self._scan_for_artifacts()

        # 3. Подготавливаем данные для Job Agent
        job_agent_payload = {
            "timestamp": scan_start.isoformat(),
            "methodology_author": "Ekaterina Kudelya",
            "methodology_license": "CC BY-ND 4.0",
            "tracker_progress": tracker_progress,
            "artifacts": artifacts,
            "completed_markers": self.tracker.progress.get("completed_markers", []),
        }

        # 4. Передаём в Job Automation Agent
        self._send_to_job_agent(job_agent_payload)

        # 5. Сохраняем результаты
        self.compass_dir.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(job_agent_payload, f, indent=2, ensure_ascii=False)

        scan_duration = (datetime.now() - scan_start).total_seconds()

        logger.info(f"✅ Scan completed in {scan_duration:.2f}s")
        logger.info(f"   Progress: {tracker_progress['overall_progress']:.1f}%")
        logger.info(f"   Completed markers: {tracker_progress['total_completed']}")
        logger.info(f"   Sent to Job Agent: {self.job_agent_url}")

        return job_agent_payload

    def _scan_for_artifacts(self) -> Dict[str, Any]:
        """Сканировать проект на наличие артефактов"""
        artifacts = {}

        # Python
        py_files = list(self.project_path.rglob("**/*.py"))
        if len(py_files) >= 10:
            artifacts["python_files"] = len(py_files)

        # Tests
        test_files = list(self.project_path.rglob("**/test_*.py"))
        if len(test_files) >= 5:
            artifacts["test_files"] = len(test_files)

        # E2E tests
        e2e_dir = self.project_path / "tests" / "e2e"
        if e2e_dir.exists():
            e2e_files = list(e2e_dir.glob("test_*.py"))
            if e2e_files:
                artifacts["e2e_tests"] = len(e2e_files)

        # Docker
        if (self.project_path / "docker-compose.yml").exists():
            artifacts["docker_compose"] = True

        # Documentation
        docs_dir = self.project_path / "docs"
        if docs_dir.exists():
            md_files = list(docs_dir.glob("**/*.md"))
            if md_files:
                artifacts["docs"] = len(md_files)

        # Microservices
        apps_dir = self.project_path / "apps"
        if apps_dir.exists():
            services = [d.name for d in apps_dir.iterdir() if d.is_dir()]
            if len(services) >= 3:
                artifacts["microservices"] = services

        # IT Compass
        if self.it_compass_core.exists():
            artifacts["it_compass_methodology"] = True

        return artifacts

    def _send_to_job_agent(self, payload: Dict[str, Any]):
        """Передать данные в Job Automation Agent"""
        try:
            # Сохраняем для последующей ручной отправки (если Job Agent не запущен)
            job_agent_file = self.compass_dir / "job_agent_payload.json"
            with open(job_agent_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Data saved to {job_agent_file}")
            logger.info("   (Will be sent to Job Agent when available)")

            # Пытаемся отправить (если Job Agent запущен)
            # TODO: Реализовать отправку после запуска Job Agent

        except Exception as e:
            logger.warning(f"Could not send to Job Agent: {e}")
            logger.info("   Data saved for later submission")


def scan_it_compass(project_path: str = None) -> Dict[str, Any]:
    """Удобная функция для сканирования"""
    scanner = ITCompassScanner(project_path)
    return scanner.scan_project()


def get_scanner():
    """Получить экземпляр сканера"""
    return ITCompassScanner()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IT Compass Scanner")
    parser.add_argument("--scan", action="store_true", help="Запустить сканирование")
    parser.add_argument("--project", type=str, help="Путь к проекту")

    args = parser.parse_args()

    if args.scan:
        results = scan_it_compass(args.project)
        print("\n✅ Scan completed!")
        print(f"   Progress: {results['tracker_progress']['overall_progress']:.1f}%")
        print("   Data saved for Job Agent")
    else:
        parser.print_help()
