#!/usr/bin/env python3
"""
Phase 1.2: Add Config Directories
"""

from pathlib import Path

services = [
    "ai_config_manager",
    "auth_service",
    "career_development",
    "cognitive_agent",
    "decision_engine",
    "job_automation_agent",
    "knowledge_graph",
    "ml_model_registry",
    "portfolio_organizer",
    "system_proof",
    "template_service",
    "thought_architecture",
]

print("📁 ADDING CONFIG DIRECTORIES")
print("=" * 70)

for service in services:
    config_path = Path(f"apps/{service}/config")
    config_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {service}/config")

print("=" * 70)
print("✅ Phase 1.2 COMPLETE: All config directories created")
