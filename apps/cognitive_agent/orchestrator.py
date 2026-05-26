#!/usr/bin/env python3
"""
Cognitive Agent Orchestrator
Восстанавливает связи между компонентами системы через MCP Server:
- AI Config Manager (через config_integration.py)
- IT-Compass маркеры (через MCP Server)
- Job Search (через job_search_adapter)
- Workflow execution (через YAML)
"""

import asyncio
import json
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MCPClient:
    """Клиент для связи с MCP Server через stdio"""

    def __init__(self, server_path: Path | None = None):
        self.server_path = server_path or REPO_ROOT / "tools" / "ai_integration" / "mcp_server.py"
        self.process: subprocess.Popen | None = None

    def start(self) -> bool:
        """Запуск MCP сервера как подпроцесса"""
        if not self.server_path.exists():
            logger.warning(f"⚠️  MCP сервер не найден: {self.server_path}")
            return False

        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            logger.info(f"✅ MCP сервер запущен (PID: {self.process.pid})")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка запуска MCP сервера: {e}")
            return False

    def call_tool(self, tool_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Вызов инструмента MCP сервера"""
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("MCP сервер не запущен")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": params or {}},
            "id": 1,
        }

        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()

            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                return response.get("result", {})
        except Exception as e:
            logger.error(f"Ошибка вызова MCP tool {tool_name}: {e}")

        return {}

    def stop(self):
        """Остановка MCP сервера"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("MCP сервер остановлен")


class CognitiveOrchestrator:
    """Оркестратор, восстанавливающий связи между компонентами"""

    def __init__(self):
        self.config = self._load_config()
        self.mcp_client = MCPClient()
        self.adapters: dict[str, Any] = {}
        self.running = False

    def _load_config(self) -> dict[str, Any]:
        """Загрузка конфигурации через существующий config_integration.py"""
        try:
            # Используем УЖЕ СУЩЕСТВУЮЩИЙ модуль интеграции
            from apps.cognitive_agent.src.config_integration import get_config

            config_wrapper = get_config()
            config = config_wrapper.get_config()
            logger.info(
                f"✅ Конфиг загружен (AI Config Manager: {config_wrapper.is_available()})"
            )
            return config
        except Exception as e:
            logger.warning(f"⚠️  Не удалось загрузить конфиг: {e}, использую дефолт")
            return {
                "scanner_interval": 60,
                "planner_interval": 120,
                "learning_interval": 300,
            }

    def init_mcp(self) -> bool:
        """Инициализация MCP клиента для связи с IT-Compass"""
        if self.mcp_client.start():
            # Проверяем, что MCP работает
            try:
                result = self.mcp_client.call_tool("get_project_context")
                if result:
                    logger.info("✅ MCP Server доступен для запросов")
                    return True
            except Exception as e:
                logger.warning(f"⚠️  MCP запущен, но не отвечает: {e}")
        return False

    def get_competency_markers(self) -> dict[str, Any]:
        """Получить маркеры компетенций из IT-Compass через MCP"""
        if not self.mcp_client.process:
            logger.warning("MCP не инициализирован")
            return {}

        try:
            result = self.mcp_client.call_tool("get_system_thinking_markers")
            logger.info("✅ Маркеры IT-Compass получены через MCP")
            return result
        except Exception as e:
            logger.error(f"Ошибка получения маркеров: {e}")
            return {}

    def run_workflow(self, workflow_name: str) -> bool:
        """Запуск существующего YAML workflow"""
        workflow_path = (
            REPO_ROOT / "apps" / "cognitive_agent" / "workflows" / f"{workflow_name}.yaml"
        )

        if not workflow_path.exists():
            logger.error(f"Workflow не найден: {workflow_path}")
            return False

        logger.info(f"🚀 Запуск workflow: {workflow_name}")

        # Парсим YAML и выполняем шаги
        try:
            import yaml

            with open(workflow_path, encoding="utf-8") as f:
                workflow = yaml.safe_load(f)

            logger.info(f"Описание: {workflow.get('description', 'N/A')}")
            logger.info(f"Количество шагов: {len(workflow.get('steps', []))}")

            for step in workflow.get("steps", []):
                logger.info(f"  → Шаг: {step.get('name')}")
                # Здесь можно добавить реальное выполнение через scripts/
                script = step.get("script")
                if script:
                    script_path = REPO_ROOT / "apps" / "cognitive_agent" / script
                    if script_path.exists():
                        logger.info(f"    Запуск: {script}")
                        # Асинхронный запуск, не блокируем
                        subprocess.Popen(
                            [sys.executable, str(script_path)],
                            cwd=str(REPO_ROOT / "apps" / "cognitive_agent"),
                        )

            logger.info(f"✅ Workflow {workflow_name} запущен")
            return True

        except Exception as e:
            logger.error(f"Ошибка запуска workflow: {e}")
            return False

    def run(self):
        """Главный цикл оркестратора"""
        logger.info("=" * 60)
        logger.info("Cognitive Agent Orchestrator — восстановление связей")
        logger.info("=" * 60)

        # 1. Инициализация MCP
        if self.init_mcp():
            # 2. Получение маркеров компетенций
            markers = self.get_competency_markers()
            logger.info(f"Загружено маркеров: {len(markers)}")

            # 3. Запуск базового workflow
            self.run_workflow("marker-extraction")

        # 4. Основной цикл — поддержка жизни
        self.running = True
        try:
            while self.running:
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Остановка оркестратора...")
            self.running = False
            self.mcp_client.stop()


def main():
    """Точка входа"""
    orchestrator = CognitiveOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()