"""
MCP Server — Entry Point

Сервер Model Context Protocol (MCP) для взаимодействия с AI-агентами.
Обеспечивает регистрацию инструментов, управление ресурсами и шаблоны промптов.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:

# Интеграция с AI Config Manager
try:
    from apps.mcp_server.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    mcp_config = config_manager.get_config()
    print("✅ MCP Server: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  MCP Server: AI Config Manager недоступен ({e}), используется локальный конфиг")
    mcp_config = {}


def run_mcp_server():
    """Запуск MCP сервера"""
    from apps.mcp_server.src.server import main as mcp_main

    port = 8002
    if mcp_config:
        port = mcp_config.get("mcp_server", {}).get("port", 8002)

    print(f"🚀 Запуск MCP Server на port {port}...")
    mcp_main(port=port)


if __name__ == "__main__":
    run_mcp_server()
