#!/usr/bin/env python3
"""
Portfolio System Architect - Services Health Check
Проверка работоспособности всех микросервисов
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class ServiceHealthCheck:
    def __init__(self, root: str = "."):
        self.root = Path(root).resolve()
        self.apps_dir = self.root / "apps"
        self.results = {}
        
    def check_all_services(self) -> Dict:
        """Проверить все сервисы"""
        print("🏥 PORTFOLIO SYSTEM ARCHITECT - SERVICES HEALTH CHECK")
        print("=" * 80)
        
        services = sorted([d.name for d in self.apps_dir.iterdir() if d.is_dir()])
        
        for i, service in enumerate(services, 1):
            print(f"\n[{i}/{len(services)}] Checking: {service}")
            self.check_service(service)
        
        self.print_report()
        return self.results
    
    def check_service(self, service_name: str):
        """Проверить отдельный сервис"""
        service_path = self.apps_dir / service_name
        result = {
            "name": service_name,
            "path": str(service_path),
            "status": "🟢 OK",
            "checks": {}
        }
        
        # 1. Проверка структуры
        structure_check = self._check_structure(service_path)
        result["checks"]["structure"] = structure_check
        
        # 2. Проверка конфигурации
        config_check = self._check_config(service_path)
        result["checks"]["config"] = config_check
        
        # 3. Проверка зависимостей
        deps_check = self._check_dependencies(service_path)
        result["checks"]["dependencies"] = deps_check
        
        # 4. Проверка тестов
        tests_check = self._check_tests(service_path)
        result["checks"]["tests"] = tests_check
        
        # 5. Проверка документации
        docs_check = self._check_documentation(service_path)
        result["checks"]["documentation"] = docs_check
        
        # Определить общий статус
        if any(not v.get("ok") for v in result["checks"].values()):
            result["status"] = "🟡 WARNING"
        
        self.results[service_name] = result
        self._print_service_result(result)
    
    def _check_structure(self, service_path: Path) -> Dict:
        """Проверить основную структуру"""
        required = ["src", "config", "tests"]
        found = []
        missing = []
        
        for item in required:
            if (service_path / item).exists():
                found.append(item)
            else:
                missing.append(item)
        
        ok = len(missing) == 0
        status = "✅" if ok else "⚠️"
        
        print(f"  {status} Structure: {len(found)}/{len(required)} dirs found", end="")
        if missing:
            print(f" (missing: {', '.join(missing)})")
        else:
            print()
        
        return {
            "ok": ok,
            "found": found,
            "missing": missing,
            "score": len(found) / len(required)
        }
    
    def _check_config(self, service_path: Path) -> Dict:
        """Проверить конфигурационные файлы"""
        config_path = service_path / "config"
        files = []
        
        if config_path.exists():
            files = [f.name for f in config_path.glob("*") if f.is_file()]
        
        ok = len(files) > 0
        status = "✅" if ok else "⚠️"
        
        print(f"  {status} Config: {len(files)} files found")
        
        return {
            "ok": ok,
            "files": files,
            "count": len(files)
        }
    
    def _check_dependencies(self, service_path: Path) -> Dict:
        """Проверить файлы зависимостей"""
        dep_files = {
            "requirements.txt": False,
            "package.json": False,
            "pyproject.toml": False,
            "go.mod": False,
            "pom.xml": False
        }
        
        for dep_file in dep_files:
            if (service_path / dep_file).exists():
                dep_files[dep_file] = True
        
        found = [k for k, v in dep_files.items() if v]
        ok = len(found) > 0
        status = "✅" if ok else "⚠️"
        
        print(f"  {status} Dependencies: {len(found)} file(s) - {', '.join(found) if found else 'none'}")
        
        return {
            "ok": ok,
            "files": dep_files,
            "found": found
        }
    
    def _check_tests(self, service_path: Path) -> Dict:
        """Проверить тесты"""
        tests_path = service_path / "tests"
        test_files = []
        
        if tests_path.exists():
            test_files = list(tests_path.glob("**/*.py")) + list(tests_path.glob("**/*.ts"))
        
        ok = len(test_files) > 0
        status = "✅" if ok else "🔴"
        
        print(f"  {status} Tests: {len(test_files)} test files found")
        
        return {
            "ok": ok,
            "count": len(test_files),
            "exists": tests_path.exists()
        }
    
    def _check_documentation(self, service_path: Path) -> Dict:
        """Проверить документацию"""
        readme = service_path / "README.md"
        docs_dir = service_path / "docs"
        
        has_readme = readme.exists()
        has_docs = docs_dir.exists()
        
        doc_count = 0
        if has_docs:
            doc_count = len(list(docs_dir.glob("**/*.md")))
        
        ok = has_readme or has_docs
        status = "✅" if ok else "🔴"
        
        details = []
        if has_readme:
            details.append("README.md")
        if has_docs:
            details.append(f"docs/ ({doc_count} files)")
        
        print(f"  {status} Docs: {', '.join(details) if details else 'missing'}")
        
        return {
            "ok": ok,
            "has_readme": has_readme,
            "has_docs": has_docs,
            "doc_count": doc_count
        }
    
    def _print_service_result(self, result: Dict):
        """Вывести результат сервиса"""
        status_symbol = "✅" if result["status"] == "🟢 OK" else "⚠️"
        print(f"  └─ {status_symbol} Overall: {result['status']}")
    
    def print_report(self):
        """Вывести финальный отчет"""
        print("\n" + "=" * 80)
        print("📊 SUMMARY REPORT")
        print("=" * 80)
        
        total = len(self.results)
        healthy = sum(1 for r in self.results.values() if r["status"] == "🟢 OK")
        warning = total - healthy
        
        print(f"\n📌 Overall Status:")
        print(f"  • Total Services: {total}")
        print(f"  • Healthy (🟢): {healthy}")
        print(f"  • Warnings (🟡): {warning}")
        print(f"  • Health Score: {(healthy/total)*100:.1f}%")
        
        print(f"\n📋 Service Details:")
        print(f"  {'Service':<25} {'Status':<12} {'Structure':<12} {'Tests':<10} {'Docs':<10}")
        print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*10} {'-'*10}")
        
        for name, result in sorted(self.results.items()):
            status = "🟢 OK" if result["status"] == "🟢 OK" else "🟡 WARNING"
            struct_score = f"{result['checks']['structure']['score']*100:.0f}%"
            tests_ok = "✅" if result["checks"]["tests"]["ok"] else "❌"
            docs_ok = "✅" if result["checks"]["documentation"]["ok"] else "⚠️"
            
            print(f"  {name:<25} {status:<12} {struct_score:<12} {tests_ok:<10} {docs_ok:<10}")
        
        # Детальный анализ проблем
        issues = self._find_issues()
        if issues:
            print(f"\n⚠️ ISSUES FOUND:")
            for category, items in issues.items():
                print(f"  {category}:")
                for item in items:
                    print(f"    - {item}")
        
        print("\n" + "=" * 80)
        print("✅ HEALTH CHECK COMPLETE")
        print("=" * 80)
    
    def _find_issues(self) -> Dict[str, List[str]]:
        """Найти проблемы"""
        issues = {
            "Missing Tests": [],
            "Missing Documentation": [],
            "Incomplete Structure": []
        }
        
        for name, result in self.results.items():
            if not result["checks"]["tests"]["ok"]:
                issues["Missing Tests"].append(name)
            
            if not result["checks"]["documentation"]["ok"]:
                issues["Missing Documentation"].append(name)
            
            if not result["checks"]["structure"]["ok"]:
                issues["Incomplete Structure"].append(f"{name} (missing: {', '.join(result['checks']['structure']['missing'])})")
        
        return {k: v for k, v in issues.items() if v}
    
    def export_json(self, filename: str = "health_check_report.json"):
        """Экспортировать отчет в JSON"""
        output_path = self.root / filename
        
        summary = {
            "timestamp": str(Path(".").resolve()),
            "total_services": len(self.results),
            "healthy": sum(1 for r in self.results.values() if r["status"] == "🟢 OK"),
            "services": self.results
        }
        
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📄 Report exported to: {output_path}")


if __name__ == "__main__":
    checker = ServiceHealthCheck()
    checker.check_all_services()
    try:
        checker.export_json("health_check_report.json")
    except Exception as e:
        print(f"Warning: Could not export JSON: {e}")
