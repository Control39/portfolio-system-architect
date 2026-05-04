#!/usr/bin/env python3
"""
Phase 1.3: Add src Directories
"""

from pathlib import Path

services = [
    'auth_service', 'cognitive-agent', 'decision-engine',
    'system-proof', 'thought-architecture'
]

print("📁 ADDING SRC DIRECTORIES")
print("=" * 70)

for service in services:
    src_path = Path(f"apps/{service}/src")
    src_path.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_file = src_path / "__init__.py"
    init_file.touch()
    
    print(f"✅ Created: {service}/src/")
    print(f"   ├── __init__.py")

print("=" * 70)
print("✅ Phase 1.3 COMPLETE: All src directories created")
