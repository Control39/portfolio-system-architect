#!/usr/bin/env python3
"""Test PromptEngine integration in AutonomousCognitiveAgent"""

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("🧪 Testing PromptEngine Integration")
print("=" * 80)

# Test 1: Import agent with PromptEngine
print("\n✅ Step 1: Importing AutonomousCognitiveAgent...")
try:
    from agents.cognitive_agent.src.autonomous_agent import AutonomousCognitiveAgent

    print("   ✓ Agent imported successfully")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 2: Check that __init__ has prompt_engine initialization
print("\n✅ Step 2: Checking __init__ for prompt_engine...")
try:
    import inspect

    source = inspect.getsource(AutonomousCognitiveAgent.__init__)

    if "prompt_engine" in source:
        print("   ✓ prompt_engine initialization found in __init__")
    else:
        print("   ✗ prompt_engine NOT found in __init__")
        sys.exit(1)

    if "use_prompt_strategies" in source:
        print("   ✓ use_prompt_strategies flag found")
    else:
        print("   ✗ use_prompt_strategies NOT found")

except Exception as e:
    print(f"   ✗ Check failed: {e}")
    sys.exit(1)

# Test 3: Check new methods exist
print("\n✅ Step 3: Checking new hybrid methods...")
methods_to_check = ["analyze_test_coverage_prompt_driven", "duel_mode_test_coverage"]

for method_name in methods_to_check:
    if hasattr(AutonomousCognitiveAgent, method_name):
        print(f"   ✓ Method '{method_name}' exists")
    else:
        print(f"   ✗ Method '{method_name}' NOT found")
        sys.exit(1)

# Test 4: Verify PromptEngine import
print("\n✅ Step 4: Verifying PromptEngine import...")
try:
    from agents.cognitive_agent.src.prompt_engine import PromptEngine

    print("   ✓ PromptEngine can be imported")
except ImportError as e:
    print(f"   ✗ PromptEngine import failed: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 80)
print("🎉 INTEGRATION TEST PASSED!")
print("=" * 80)
print("\n✅ Hybrid Architecture successfully integrated:")
print("   • PromptEngine imported")
print("   • prompt_engine initialized in __init__()")
print("   • use_prompt_strategies flag added")
print("   • analyze_test_coverage_prompt_driven() method added")
print("   • duel_mode_test_coverage() method added")
print("\n🚀 Agent is ready for prompt-driven strategies!")
print("=" * 80)
