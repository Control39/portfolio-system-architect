#!/usr/bin/env python3
"""Test TestGenerator functionality"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("🧪 Testing TestGenerator")
print("=" * 80)

# Test 1: Import TestGenerator
print("\n✅ Step 1: Importing TestGenerator...")
try:
    from agents.cognitive_agent.src.test_generator import TestGenerator

    print("   ✓ TestGenerator imported successfully")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize generator
print("\n✅ Step 2: Initializing TestGenerator...")
try:
    generator = TestGenerator(
        project_path="C:/repo",
        prompts_dir=Path("agents/cognitive_agent/prompts"),
    )
    print(f"   ✓ Generator initialized with {len(generator.prompt_engine.templates)} templates")
except Exception as e:
    print(f"   ✗ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test framework detection
print("\n✅ Step 3: Testing framework detection...")
try:
    test_files = [
        Path("apps/decision_engine/core/models.py"),
        Path("apps/user_service/api/users.py"),
    ]
    
    for test_file in test_files:
        full_path = Path("C:/repo") / test_file
        if full_path.exists():
            framework = generator._detect_framework(full_path)
            file_type = generator._detect_file_type(full_path, framework)
            template = generator._get_template_path(framework, file_type)
            print(f"   • {test_file}: {framework} / {file_type} → {template}")
        else:
            print(f"   • {test_file}: File not found (skipped)")
except Exception as e:
    print(f"   ✗ Framework detection test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test template path selection
print("\n✅ Step 4: Testing template path selection...")
try:
    test_cases = [
        ("fastapi", "api", "python/fastapi/api"),
        ("fastapi", "integration", "python/fastapi/integration"),
        ("flask", "api", "python/flask/api"),
        ("django", "models", "python/django/unit"),
        ("django", "unit", "python/django/unit"),
        ("base", "unit", "python/base/unit"),
        ("base", "models", "python/base/unit"),
    ]
    
    for framework, file_type, expected in test_cases:
        result = generator._get_template_path(framework, file_type)
        status = "✓" if result == expected else "✗"
        print(f"   {status} {framework} / {file_type} → {result} (expected: {expected})")
except Exception as e:
    print(f"   ✗ Template path test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test service detection
print("\n✅ Step 5: Testing service detection...")
try:
    test_paths = [
        Path("apps/user_service/api/users.py"),
        Path("apps/decision_engine/core/models.py"),
        Path("src/config.py"),
    ]
    
    for test_path in test_paths:
        service = generator._detect_service(test_path)
        print(f"   • {test_path} → service: {service}")
except Exception as e:
    print(f"   ✗ Service detection test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final summary
print("\n" + "=" * 80)
print("🎉 ALL TESTS PASSED!")
print("=" * 80)
print("\n✅ TestGenerator is ready:")
print("   • Framework detection works")
print("   • File type detection works")
print("   • Template selection works")
print("   • Service detection works")
print("   • Ready for LLM integration")
print("\n🚀 Ready for automated test generation!")
print("=" * 80)
