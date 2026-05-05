#!/usr/bin/env python3
"""
Phase 2.1 Integration Tests Runner
Запускает интеграционные тесты для top-5 критических сервисов
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class IntegrationTestRunner:
    def __init__(self):
        self.root = Path(".").resolve()
        self.critical_services = [
            "cognitive-agent",
            "decision-engine",
            "it_compass",
            "mcp-server",
            "infra-orchestrator",
        ]
        self.results = {}
    
    def run_all(self):
        """Запустить тесты для всех сервисов"""
        print("🧪 PHASE 2.1: INTEGRATION TESTS - TOP 5 CRITICAL SERVICES")
        print("=" * 80)
        
        for service_name in self.critical_services:
            self.run_service_tests(service_name)
        
        self.print_summary()
    
    def run_service_tests(self, service_name: str):
        """Запустить тесты для одного сервиса"""
        test_file = self.root / "apps" / service_name / "tests" / f"test_integration_{service_name.replace('-', '_')}.py"
        
        if not test_file.exists():
            print(f"\n❌ {service_name}: Test file not found")
            self.results[service_name] = {"status": "MISSING", "passed": 0, "failed": 0, "error": "File not found"}
            return
        
        print(f"\n🔍 Testing {service_name}...")
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # Parse results
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            error = output.count(" ERROR")
            
            status = "PASS" if failed == 0 and error == 0 else "FAIL"
            
            self.results[service_name] = {
                "status": status,
                "passed": passed,
                "failed": failed,
                "error": error
            }
            
            print(f"   ✅ Passed: {passed}, ❌ Failed: {failed}, ⚠️ Error: {error}")
            
        except subprocess.TimeoutExpired:
            self.results[service_name] = {"status": "TIMEOUT", "passed": 0, "failed": 0, "error": "Test timeout"}
            print(f"   ⏱️ Test timeout")
        except Exception as e:
            self.results[service_name] = {"status": "ERROR", "passed": 0, "failed": 0, "error": str(e)}
            print(f"   ⚠️ Error: {str(e)}")
    
    def print_summary(self):
        """Вывести итоговый отчет"""
        print("\n" + "=" * 80)
        print("📊 SUMMARY REPORT")
        print("=" * 80)
        
        total_tests = sum(r.get("passed", 0) + r.get("failed", 0) for r in self.results.values())
        total_passed = sum(r.get("passed", 0) for r in self.results.values())
        total_failed = sum(r.get("failed", 0) for r in self.results.values())
        
        print(f"\n📌 Overall Results:")
        print(f"  • Services Tested: {len(self.critical_services)}")
        print(f"  • Total Tests: {total_tests}")
        print(f"  • Passed: {total_passed}")
        print(f"  • Failed: {total_failed}")
        
        if total_tests > 0:
            pass_rate = (total_passed / total_tests) * 100
        else:
            pass_rate = 0
        
        print(f"  • Pass Rate: {pass_rate:.1f}%")
        
        print(f"\n📋 Service Details:")
        print(f"  {'Service':<20} {'Status':<10} {'Passed':<8} {'Failed':<8} {'Error':<8}")
        print(f"  {'-'*20} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")
        
        for service in self.critical_services:
            result = self.results.get(service, {})
            status = result.get("status", "UNKNOWN")
            passed = result.get("passed", 0)
            failed = result.get("failed", 0)
            error = result.get("error", 0)
            
            print(f"  {service:<20} {status:<10} {passed:<8} {failed:<8} {error:<8}")
        
        print("\n" + "=" * 80)
        print("✅ INTEGRATION TEST RUN COMPLETE")
        print("=" * 80)
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Сохранить результаты в JSON"""
        report_file = self.root / "phase2_integration_test_results.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "phase": "2.1",
            "results": self.results
        }
        
        with open(report_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n📄 Results saved to: phase2_integration_test_results.json")


if __name__ == "__main__":
    runner = IntegrationTestRunner()
    runner.run_all()
