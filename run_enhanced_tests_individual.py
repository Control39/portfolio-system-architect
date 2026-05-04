#!/usr/bin/env python3
"""
Run enhanced tests for each service individually to avoid import conflicts
"""

import subprocess
from pathlib import Path
import json

services = [
    "cognitive-agent", "decision-engine", "it_compass", "knowledge-graph",
    "auth_service", "mcp-server", "infra-orchestrator", "ml-model-registry",
    "portfolio_organizer", "career_development", "job-automation-agent",
    "ai-config-manager", "template-service", "system-proof", "thought-architecture"
]

results = {}
total_passed = 0
total_failed = 0

print("🧪 PHASE 2.2: ENHANCED TESTS FOR ALL 15 SERVICES")
print("=" * 80)

for i, service in enumerate(services, 1):
    test_file = Path("apps") / service / "tests" / "test_basic.py"
    
    if not test_file.exists():
        print(f"[{i:2d}/15] {service:<25} ❌ SKIP (test_basic.py not found)")
        continue
    
    print(f"[{i:2d}/15] {service:<25} ", end="", flush=True)
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", str(test_file), "-v", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        # Count test results
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        
        if "passed" in output:
            # Extract from summary line like "15 passed in 0.09s"
            import re
            match = re.search(r'(\d+) passed', output)
            if match:
                passed = int(match.group(1))
        
        if "failed" in output:
            import re
            match = re.search(r'(\d+) failed', output)
            if match:
                failed = int(match.group(1))
        
        total_passed += passed
        total_failed += failed
        results[service] = {"passed": passed, "failed": failed, "status": "PASS" if failed == 0 else "FAIL"}
        
        if failed == 0 and passed > 0:
            print(f"✅ {passed} tests passed")
        elif failed > 0:
            print(f"❌ {passed} passed, {failed} failed")
        else:
            print(f"⚠️  No tests found or error")
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
        results[service] = {"passed": 0, "failed": 0, "status": "ERROR"}

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(f"Total Services: {len(services)}")
print(f"Total Tests Passed: {total_passed}")
print(f"Total Tests Failed: {total_failed}")
print(f"Services with All Tests Passing: {sum(1 for r in results.values() if r['failed'] == 0)}/{len(services)}")

print("\n" + "=" * 80)
print("✅ ENHANCED TESTS COMPLETED")
print("=" * 80)

# Save results
with open("phase2_2_enhanced_test_results.json", "w") as f:
    json.dump({
        "total_services": len(services),
        "total_passed": total_passed,
        "total_failed": total_failed,
        "results": results
    }, f, indent=2)

print(f"\n📄 Results saved to phase2_2_enhanced_test_results.json")
