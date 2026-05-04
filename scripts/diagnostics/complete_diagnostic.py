#!/usr/bin/env python3
"""
Portfolio System Architect - Complete Diagnostic
Полная диагностика проекта для понимания масштаба работ
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import os

class CompleteDiagnostic:
    def __init__(self, root: str = "."):
        self.root = Path(root).resolve()
        self.apps_dir = self.root / "apps"
        self.report = {}
        
    def run_full_diagnostic(self):
        """Запустить полную диагностику"""
        print("🔬 PORTFOLIO SYSTEM ARCHITECT - COMPLETE DIAGNOSTIC")
        print("=" * 90)
        
        self.report = {
            "timestamp": str(Path.cwd()),
            "sections": {}
        }
        
        # 1. Структура проекта
        print("\n[1/6] Analyzing Project Structure...")
        self.report["sections"]["structure"] = self._analyze_structure()
        
        # 2. Сервисы
        print("[2/6] Analyzing Services...")
        self.report["sections"]["services"] = self._analyze_services()
        
        # 3. Code metrics
        print("[3/6] Analyzing Code Metrics...")
        self.report["sections"]["code_metrics"] = self._analyze_code_metrics()
        
        # 4. Testing
        print("[4/6] Analyzing Testing...")
        self.report["sections"]["testing"] = self._analyze_testing()
        
        # 5. Documentation
        print("[5/6] Analyzing Documentation...")
        self.report["sections"]["documentation"] = self._analyze_documentation()
        
        # 6. Infrastructure
        print("[6/6] Analyzing Infrastructure...")
        self.report["sections"]["infrastructure"] = self._analyze_infrastructure()
        
        self._print_diagnostic_report()
        return self.report
    
    def _analyze_structure(self) -> Dict:
        """Анализ структуры проекта"""
        result = {
            "total_directories": 0,
            "total_files": 0,
            "root_dirs": [],
            "largest_dirs": []
        }
        
        # Count directories and files
        total_dirs = 0
        total_files = 0
        dir_sizes = {}
        
        for root, dirs, files in os.walk(self.root):
            # Skip hidden and common dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['__pycache__', 'node_modules', '.git', 'venv', 'env']]
            
            total_dirs += len(dirs)
            total_files += len(files)
            
            rel_path = Path(root).relative_to(self.root)
            if str(rel_path) != ".":
                dir_sizes[str(rel_path)] = len(files)
        
        result["total_directories"] = total_dirs
        result["total_files"] = total_files
        result["root_dirs"] = [d.name for d in self.root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        result["largest_dirs"] = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return result
    
    def _analyze_services(self) -> Dict:
        """Анализ микросервисов"""
        result = {
            "total_count": 0,
            "services": {},
            "by_tier": {
                "tier1_core": [],
                "tier2_infra": [],
                "tier3_business": [],
                "other": []
            }
        }
        
        # Tier classification
        tier1 = ['cognitive-agent', 'decision-engine', 'it_compass', 'knowledge-graph']
        tier2 = ['infra-orchestrator', 'auth_service', 'mcp-server', 'ml-model-registry']
        tier3 = ['portfolio_organizer', 'career_development', 'job-automation-agent',
                'ai-config-manager', 'template-service', 'system-proof']
        
        if not self.apps_dir.exists():
            return result
        
        services = sorted([d.name for d in self.apps_dir.iterdir() if d.is_dir()])
        result["total_count"] = len(services)
        
        for service in services:
            service_path = self.apps_dir / service
            info = {
                "path": str(service_path),
                "has_src": (service_path / "src").exists(),
                "has_config": (service_path / "config").exists(),
                "has_tests": (service_path / "tests").exists(),
                "has_readme": (service_path / "README.md").exists(),
                "has_docs": (service_path / "docs").exists(),
                "file_count": len(list(service_path.glob("**/*"))),
                "tier": "unknown"
            }
            
            # Assign tier
            if service in tier1:
                info["tier"] = "Tier 1 (Core)"
                result["by_tier"]["tier1_core"].append(service)
            elif service in tier2:
                info["tier"] = "Tier 2 (Infrastructure)"
                result["by_tier"]["tier2_infra"].append(service)
            elif service in tier3:
                info["tier"] = "Tier 3 (Business)"
                result["by_tier"]["tier3_business"].append(service)
            else:
                info["tier"] = "Other"
                result["by_tier"]["other"].append(service)
            
            result["services"][service] = info
        
        return result
    
    def _analyze_code_metrics(self) -> Dict:
        """Анализ кода"""
        result = {
            "python_files": 0,
            "javascript_files": 0,
            "typescript_files": 0,
            "total_lines": 0,
            "by_extension": {}
        }
        
        extensions = {}
        
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ['__pycache__', 'node_modules']]
            
            for file in files:
                ext = Path(file).suffix
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
        
        result["by_extension"] = dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:15])
        result["python_files"] = extensions.get('.py', 0)
        result["javascript_files"] = extensions.get('.js', 0)
        result["typescript_files"] = extensions.get('.ts', 0)
        
        return result
    
    def _analyze_testing(self) -> Dict:
        """Анализ тестирования"""
        result = {
            "services_with_tests": 0,
            "services_without_tests": 0,
            "test_files_count": 0,
            "total_tests": 0,
            "by_service": {}
        }
        
        if not self.apps_dir.exists():
            return result
        
        for service_dir in self.apps_dir.iterdir():
            if not service_dir.is_dir():
                continue
            
            tests_dir = service_dir / "tests"
            test_files = list(tests_dir.glob("**/*.py")) + list(tests_dir.glob("**/*.ts")) if tests_dir.exists() else []
            
            if test_files:
                result["services_with_tests"] += 1
            else:
                result["services_without_tests"] += 1
            
            result["test_files_count"] += len(test_files)
            result["by_service"][service_dir.name] = len(test_files)
        
        return result
    
    def _analyze_documentation(self) -> Dict:
        """Анализ документации"""
        result = {
            "readme_files": 0,
            "md_files": 0,
            "services_with_readme": 0,
            "services_without_readme": 0,
            "by_service": {}
        }
        
        if not self.apps_dir.exists():
            return result
        
        for root, dirs, files in os.walk(self.root):
            result["md_files"] += len([f for f in files if f.endswith('.md')])
        
        for service_dir in self.apps_dir.iterdir():
            if not service_dir.is_dir():
                continue
            
            has_readme = (service_dir / "README.md").exists()
            if has_readme:
                result["services_with_readme"] += 1
            else:
                result["services_without_readme"] += 1
            
            result["by_service"][service_dir.name] = {
                "has_readme": has_readme,
                "has_docs_dir": (service_dir / "docs").exists()
            }
        
        result["readme_files"] = result["services_with_readme"]
        
        return result
    
    def _analyze_infrastructure(self) -> Dict:
        """Анализ инфраструктуры"""
        result = {
            "deployment_files": [],
            "docker_files": [],
            "k8s_files": [],
            "config_files": [],
            "ci_cd_files": [],
            "monitoring_files": []
        }
        
        # Check for various infrastructure files
        if (self.root / "deployment").exists():
            result["deployment_files"] = len(list((self.root / "deployment").glob("**/*")))
        
        if (self.root / "docker").exists():
            result["docker_files"] = len(list((self.root / "docker").glob("**/*")))
        
        if (self.root / "deployment" / "k8s").exists():
            result["k8s_files"] = len(list((self.root / "deployment" / "k8s").glob("**/*")))
        
        if (self.root / "config").exists():
            result["config_files"] = len(list((self.root / "config").glob("**/*")))
        
        if (self.root / ".github" / "workflows").exists():
            result["ci_cd_files"] = len(list((self.root / ".github" / "workflows").glob("**/*")))
        
        if (self.root / "monitoring").exists():
            result["monitoring_files"] = len(list((self.root / "monitoring").glob("**/*")))
        
        return result
    
    def _print_diagnostic_report(self):
        """Вывести диагностический отчет"""
        print("\n" + "=" * 90)
        print("📋 DIAGNOSTIC REPORT")
        print("=" * 90)
        
        # Structure
        struct = self.report["sections"]["structure"]
        print(f"\n📁 PROJECT STRUCTURE:")
        print(f"  • Total Directories: {struct['total_directories']}")
        print(f"  • Total Files: {struct['total_files']}")
        print(f"  • Root Directories: {', '.join(struct['root_dirs'][:10])}")
        if len(struct['root_dirs']) > 10:
            print(f"    ... and {len(struct['root_dirs']) - 10} more")
        
        # Services
        svcs = self.report["sections"]["services"]
        print(f"\n🏗️  MICROSERVICES:")
        print(f"  • Total: {svcs['total_count']}")
        print(f"  • Tier 1 (Core): {len(svcs['by_tier']['tier1_core'])} services")
        print(f"  • Tier 2 (Infrastructure): {len(svcs['by_tier']['tier2_infra'])} services")
        print(f"  • Tier 3 (Business): {len(svcs['by_tier']['tier3_business'])} services")
        
        # Code metrics
        code = self.report["sections"]["code_metrics"]
        print(f"\n💻 CODE METRICS:")
        print(f"  • Python Files: {code['python_files']}")
        print(f"  • JavaScript Files: {code['javascript_files']}")
        print(f"  • TypeScript Files: {code['typescript_files']}")
        print(f"  • Top File Types: {', '.join(f'{k}({v})' for k, v in list(code['by_extension'].items())[:5])}")
        
        # Testing
        test = self.report["sections"]["testing"]
        print(f"\n🧪 TESTING:")
        print(f"  • Services with Tests: {test['services_with_tests']}")
        print(f"  • Services WITHOUT Tests: {test['services_without_tests']}")
        print(f"  • Total Test Files: {test['test_files_count']}")
        print(f"  • Coverage: {(test['services_with_tests']/(test['services_with_tests']+test['services_without_tests'])*100):.1f}%")
        
        # Documentation
        docs = self.report["sections"]["documentation"]
        print(f"\n📚 DOCUMENTATION:")
        print(f"  • README Files: {docs['readme_files']}")
        print(f"  • Markdown Files: {docs['md_files']}")
        print(f"  • Services with README: {docs['services_with_readme']}")
        print(f"  • Services WITHOUT README: {docs['services_without_readme']}")
        print(f"  • Doc Coverage: {(docs['services_with_readme']/(docs['services_with_readme']+docs['services_without_readme'])*100):.1f}%")
        
        # Infrastructure
        infra = self.report["sections"]["infrastructure"]
        print(f"\n⚙️  INFRASTRUCTURE:")
        print(f"  • Deployment Files: {infra['deployment_files']}")
        print(f"  • Docker Files: {infra['docker_files']}")
        print(f"  • K8s Files: {infra['k8s_files']}")
        print(f"  • Config Files: {infra['config_files']}")
        print(f"  • CI/CD Files: {infra['ci_cd_files']}")
        print(f"  • Monitoring Files: {infra['monitoring_files']}")
        
        # Assessment
        print(f"\n" + "=" * 90)
        print("📊 OVERALL ASSESSMENT")
        print("=" * 90)
        
        test_score = (test['services_with_tests']/(test['services_with_tests']+test['services_without_tests'])*100) if (test['services_with_tests']+test['services_without_tests']) > 0 else 0
        doc_score = (docs['services_with_readme']/(docs['services_with_readme']+docs['services_without_readme'])*100) if (docs['services_with_readme']+docs['services_without_readme']) > 0 else 0
        
        print(f"  Testing Coverage: {test_score:.0f}% ({'✅' if test_score > 80 else '⚠️' if test_score > 50 else '🔴'})")
        print(f"  Documentation: {doc_score:.0f}% ({'✅' if doc_score > 80 else '⚠️' if doc_score > 50 else '🔴'})")
        print(f"  Infrastructure: {'✅' if infra['k8s_files'] > 0 else '⚠️'} (K8s configured)")
        print(f"  CI/CD: {'✅' if infra['ci_cd_files'] > 0 else '⚠️'} (GitHub Actions configured)")
        
        # Recommendations
        print(f"\n💡 KEY FINDINGS:")
        recommendations = []
        
        if test_score < 70:
            recommendations.append("- Add tests to more services (critical)")
        
        if doc_score < 70:
            recommendations.append("- Improve documentation coverage")
        
        if svcs['total_count'] > 10:
            recommendations.append(f"- Manage complexity: {svcs['total_count']} services is substantial")
        
        if infra['k8s_files'] > 0 and infra['deployment_files'] > 20:
            recommendations.append("- Infrastructure is well-defined")
        
        if not recommendations:
            recommendations.append("- Project is in good shape overall")
        
        for rec in recommendations:
            print(f"  {rec}")
        
        print("\n" + "=" * 90)


if __name__ == "__main__":
    diagnostic = CompleteDiagnostic()
    report = diagnostic.run_full_diagnostic()
    
    # Export JSON
    with open("diagnostic_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n📄 Full report exported to: diagnostic_report.json")
