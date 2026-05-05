#!/usr/bin/env python3
"""
Phase 2.2 Enhanced Tests Runner
Запускает улучшенные тесты для всех 15 сервисов
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class EnhancedTestRunner:
    def __init__(self):
        self.root = Path(".").resolve()
        self.apps_dir = self.root / "apps"
        self.services = sorted([d.name for d in self.apps_dir.iterdir() if d.is_dir()])
        self.results = {}
    
    def run_all(self):
        """Запустить тесты для всех сервисов"""
        print("🧪 PHASE 2.2: ENHANCED TESTS - ALL 15 SERVICES")
        print("=" * 80)
        
        for i, service_name in enumerate(self.services, 1):
            print(f"\n[{i:2d}/15] Testing {service_name}...")
            self.run_service_tests(service_name)
        
        self.print_summary()
    
    def run_service_tests(self, service_name: str):
        """Запустить тесты для одного сервиса"""
        test_file = self.apps_dir / service_name / "tests" / "test_basic.py"
        
        if not test_file.exists():
            self.results[service_name] = {"status": "SKIP", "passed": 0, "failed": 0, "reason": "test_basic.py not found"}
            print(f"   ⏭️  Skipped: test_basic.py not found")
            return
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.root)
            )
            
            output = result.stdout + result.stderr
            
            # Parse results from output
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            error = output.count(" ERROR")
            
            status = "PASS" if (failed == 0 and error == 0 and passed > 0) else "FAIL" if failed > 0 or error > 0 else "SKIP"
            
            self.results[service_name] = {
                "status": status,
                "passed": passed,
                "failed": failed,
                "error": error
            }
            
            if status == "PASS":
                print(f"   ✅ All tests passed: {passed} tests")
            elif status == "FAIL":
                print(f"   ❌ Some tests failed: {passed} passed, {failed} failed")
            else:
                print(f"   ⚠️ Issues: {error} errors")
            
        except subprocess.TimeoutExpired:
            self.results[service_name] = {"status": "TIMEOUT", "passed": 0, "failed": 0, "error": "Timeout"}
            print(f"   ⏱️  Timeout")
        except Exception as e:
            self.results[service_name] = {"status": "ERROR", "passed": 0, "failed": 0, "error": str(e)}
            print(f"   ⚠️ Error: {str(e)}")
    
    def print_summary(self):
        """Вывести итоговый отчет"""
        print("\n" + "=" * 80)
        print("📊 SUMMARY REPORT - PHASE 2.2 ENHANCED TESTS")
        print("=" * 80)
        
        total_passed = sum(r.get("passed", 0) for r in self.results.values())
        total_failed = sum(r.get("failed", 0) for r in self.results.values())
        total_error = sum(r.get("error", 0) if isinstance(r.get("error"), int) else 0 for r in self.results.values())
        
        services_pass = sum(1 for r in self.results.values() if r["status"] == "PASS")
        services_fail = sum(1 for r in self.results.values() if r["status"] == "FAIL")
        services_error = sum(1 for r in self.results.values() if r["status"] == "ERROR")
        
        print(f"\n📌 Overall Results:")
        print(f"  • Total Services: {len(self.services)}")
        print(f"  • Services Passing: {services_pass}/{len(self.services)} ✅")
        print(f"  • Services Failing: {services_fail}/{len(self.services)} ❌")
        print(f"  • Services with Errors: {services_error}/{len(self.services)} ⚠️")
        print(f"  • Total Tests Passed: {total_passed}")
        print(f"  • Total Tests Failed: {total_failed}")
        
        print(f"\n📋 Service Results (Tier-based):")
        print(f"  {'Service':<25} {'Tier':<8} {'Status':<8} {'Tests':<20}")
        print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*20}")
        
        tiers = {"cognitive-agent": "Core", "decision-engine": "Core", "it_compass": "Core", "knowledge-graph": "Core",
                 "infra-orchestrator": "Infra", "auth_service": "Infra", "mcp-server": "Infra", "ml-model-registry": "Infra",
                 "portfolio_organizer": "Biz", "career_development": "Biz", "job-automation-agent": "Biz",
                 "ai-config-manager": "Biz", "template-service": "Biz", "system-proof": "Biz", "thought-architecture": "Biz"}
        
        for service in self.services:
            result = self.results.get(service, {})
            status = result.get("status", "UNKNOWN")
            passed = result.get("passed", 0)
            failed = result.get("failed", 0)
            tier = tiers.get(service, "?")
            
            tests_str = f"{passed}✅" if failed == 0 else f"{passed}✅ {failed}❌"
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            
            print(f"  {service:<25} {tier:<8} {status_icon} {status:<6} {tests_str:<20}")
        
        print("\n" + "=" * 80)
        print("✅ ENHANCED TEST RUN COMPLETE")
        print("=" * 80)
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Сохранить результаты"""
        report_file = self.root / "phase2_2_enhanced_test_results.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "phase": "2.2",
            "total_services": len(self.services),
            "results": self.results
        }
        
        with open(report_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n📄 Results saved to: phase2_2_enhanced_test_results.json")


if __name__ == "__main__":
    runner = EnhancedTestRunner()
    runner.run_all()
