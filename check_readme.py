import os
from pathlib import Path

apps_dir = Path(r"C:\repo\apps")
services = [
    "ai_config_manager",
    "auth_service",
    "career_development",
    "cognitive_agent",
    "decision_engine",
    "infra_orchestrator",
    "it_compass",
    "job_automation_agent",
    "knowledge_graph",
    "mcp_server",
    "ml_model_registry",
    "portfolio_organizer",
    "system_proof",
    "template_service",
    "thought_architecture",
]

print("=== Проверка README в сервисах ===\n")
for service in services:
    service_dir = apps_dir / service
    readme = service_dir / "README.md"
    if readme.exists():
        size = readme.stat().st_size
        print(f"✅ {service}: exists ({size} bytes)")
    else:
        print(f"❌ {service}: MISSING")
