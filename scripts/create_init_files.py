#!/usr/bin/env python3
"""Создание __init__.py для всех сервисов"""

from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

SERVICES = [
    "auth_service",
    "career_development",
    "decision_engine",
    "infra-orchestrator",
    "it_compass",
    "job-automation-agent",
    "knowledge_graph",
    "mcp_server",
    "ml_model_registry",
    "portfolio_organizer",
    "system_proof",
    "thought-architecture",
]

for service in SERVICES:
    src_dir = REPO_ROOT / "apps" / service / "src"
    init_file = src_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"✅ {init_file.relative_to(REPO_ROOT)}")
    else:
        print(f"⏭️  {init_file.relative_to(REPO_ROOT)} (существует)")

print("Готово!")
