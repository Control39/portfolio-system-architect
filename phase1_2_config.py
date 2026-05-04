#!/usr/bin/env python3
"""
Phase 1.2: Add Config Directories
"""

from pathlib import Path

services = [
    'ai-config-manager', 'auth_service', 'career_development',
    'cognitive-agent', 'decision-engine', 'job-automation-agent',
    'knowledge-graph', 'ml-model-registry', 'portfolio_organizer',
    'system-proof', 'template-service', 'thought-architecture'
]

print("📁 ADDING CONFIG DIRECTORIES")
print("=" * 70)

for service in services:
    config_path = Path(f"apps/{service}/config")
    config_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {service}/config")

print("=" * 70)
print("✅ Phase 1.2 COMPLETE: All config directories created")
