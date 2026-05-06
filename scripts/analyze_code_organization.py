#!/usr/bin/env python3
"""
Code Organization Analyzer
Находит где РЕАЛЬНО находится каждый сервис и его код
"""

from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path.cwd()

class CodeOrganizationAnalyzer:
    def __init__(self):
        self.services = {}
        self.code_locations = defaultdict(list)

    def find_services_in_apps(self):
        """Найти все сервисы в apps/"""
        apps_dir = REPO_ROOT / "apps"

        if not apps_dir.exists():
            return

        for service_dir in sorted(apps_dir.iterdir()):
            if not service_dir.is_dir() or service_dir.name.startswith("__"):
                continue

            service_name = service_dir.name

            # Посчитать Python файлы
            py_files = list(service_dir.rglob("*.py"))
            py_count = len([f for f in py_files if "__pycache__" not in str(f)])

            # Посчитать тесты
            test_files = list(service_dir.rglob("test_*.py")) + list(service_dir.rglob("*_test.py"))
            test_count = len(test_files)

            # Размер
            size_mb = sum(f.stat().st_size for f in py_files) / (1024*1024)

            self.services[service_name] = {
                'path': str(service_dir.relative_to(REPO_ROOT)),
                'python_files': py_count,
                'test_files': test_count,
                'size_mb': round(size_mb, 1),
                'main_file': self._find_main_file(service_dir),
                'has_docker': (service_dir / "Dockerfile").exists(),
                'has_k8s': any(service_dir.rglob("*.yaml")) or any(service_dir.rglob("*.yml"))
            }

    def _find_main_file(self, service_dir):
        """Найти main файл сервиса"""
        candidates = [
            service_dir / "main.py",
            service_dir / "app.py",
            service_dir / "server.py",
            service_dir / "__main__.py"
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate.name

        return None

    def analyze_scattered_code(self):
        """Найти код который разбросан по репо (но не в apps/)"""
        python_files = list(REPO_ROOT.rglob("*.py"))

        app_files = set()
        for service in self.services.values():
            app_path = REPO_ROOT / service['path']
            app_files.update(app_path.rglob("*.py"))

        scattered = defaultdict(list)
        for py_file in python_files:
            # Пропусти .venv, __pycache__, legacy
            if any(skip in str(py_file) for skip in [".venv", "__pycache__", "legacy", ".git"]):
                continue

            if py_file not in app_files:
                # Это разбросанный код
                category = self._categorize_code(py_file)
                scattered[category].append(str(py_file.relative_to(REPO_ROOT)))

        return scattered

    @staticmethod
    def _categorize_code(py_file):
        """Категоризировать найденный код"""
        path_str = str(py_file)

        if "src/" in path_str:
            return "src/ (shared code)"
        elif "tests/" in path_str:
            return "tests/ (tests)"
        elif "scripts/" in path_str:
            return "scripts/ (automation)"
        elif "tools/" in path_str:
            return "tools/ (tools)"
        elif "client/" in path_str:
            return "client/ (frontend)"
        else:
            return "root level (loose files)"

    def generate_report(self):
        """Генерировать отчет"""
        print("=" * 80)
        print("CODE ORGANIZATION REPORT")
        print("=" * 80)
        print()

        # Сервисы в apps/
        print("✅ MICROSERVICES IN apps/")
        print("-" * 80)
        print(f"{'Service':<30} {'Py Files':<12} {'Tests':<10} {'Size':<10} {'Main':<15}")
        print("-" * 80)

        total_py = 0
        total_tests = 0
        total_size = 0

        for name in sorted(self.services.keys()):
            service = self.services[name]
            main = service['main_file'] or "—"
            docker = "🐳" if service['has_docker'] else ""
            k8s = "☸️" if service['has_k8s'] else ""

            print(f"{name:<30} {service['python_files']:<12} {service['test_files']:<10} "
                  f"{service['size_mb']:.1f} MB    {main:<15} {docker}{k8s}")

            total_py += service['python_files']
            total_tests += service['test_files']
            total_size += service['size_mb']

        print("-" * 80)
        print(f"{'TOTAL':<30} {total_py:<12} {total_tests:<10} {total_size:.1f} MB")
        print()

        # Разбросанный код
        print("⚠️  SCATTERED CODE (Outside apps/)")
        print("-" * 80)

        scattered = self.analyze_scattered_code()

        if not scattered:
            print("✅ No scattered code found! Everything is organized!")
        else:
            for category in sorted(scattered.keys()):
                files = scattered[category]
                print(f"\n{category} ({len(files)} files)")
                for f in sorted(files)[:10]:  # Show first 10
                    print(f"  • {f}")
                if len(files) > 10:
                    print(f"  ... and {len(files) - 10} more")

        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Services: {len(self.services)}")
        print(f"Total Python files in services: {total_py}")
        print(f"Total tests in services: {total_tests}")
        print(f"Total size in services: {total_size:.1f} MB")
        print()

        # Service details
        print("\n" + "=" * 80)
        print("SERVICE DETAILS")
        print("=" * 80)

        for name in sorted(self.services.keys()):
            service = self.services[name]
            print(f"\n📦 {name}")
            print(f"   Path: {service['path']}")
            print(f"   Python: {service['python_files']} files | Tests: {service['test_files']} | Size: {service['size_mb']} MB")
            print(f"   Docker: {'✅' if service['has_docker'] else '❌'} | K8s: {'✅' if service['has_k8s'] else '❌'}")
            if service['main_file']:
                print(f"   Entry: {service['main_file']}")

if __name__ == "__main__":
    analyzer = CodeOrganizationAnalyzer()
    analyzer.find_services_in_apps()
    analyzer.generate_report()
