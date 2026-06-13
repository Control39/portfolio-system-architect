#!/usr/bin/env python3
"""
Portfolio System Architect - REAL Metrics Collector
Собирает ИСТИННЫЕ метрики для динамических бейджей
"""

import json
import subprocess
from pathlib import Path

# ROOT репо
REPO_ROOT = Path.cwd()


class MetricsCollector:
    def __init__(self):
        self.metrics = {}

    def count_python_files(self):
        """Сколько Python файлов реально есть"""
        count = len(list(REPO_ROOT.rglob("*.py")))
        self.metrics["python_files"] = count
        return count

    def count_test_files(self):
        """Сколько тестов реально есть"""
        tests = list(REPO_ROOT.rglob("test_*.py")) + list(REPO_ROOT.rglob("*_test.py"))
        count = len(tests)
        self.metrics["test_files"] = count
        return count

    def count_microservices(self):
        """Сколько микросервисов реально есть"""
        apps_dir = REPO_ROOT / "apps"
        if not apps_dir.exists():
            return 0

        services = [d for d in apps_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
        count = len(services)
        self.metrics["microservices"] = count
        self.metrics["services_list"] = [s.name for s in services]
        return count

    def get_test_coverage(self):
        """Попытка получить реальное покрытие"""
        try:
            # Ищем .coverage файл
            coverage_file = REPO_ROOT / ".coverage"
            if coverage_file.exists():
                return "see .coverage file"

            # Пытаемся запустить pytest с --collect-only
            result = subprocess.run(
                ["pytest", "--collect-only", "-q", "tests/", "apps/"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=REPO_ROOT,
            )

            # Парсим количество собранных тестов
            output = result.stdout + result.stderr
            if "test selected" in output or "test collected" in output:
                self.metrics["coverage_method"] = "pytest_collected"
                return "pytest collected"

        except Exception:
            pass

        self.metrics["coverage_method"] = "not_available"
        return "not available"

    def get_git_info(self):
        """Git информация"""
        try:
            # Commits
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=REPO_ROOT,
            )
            commits = int(result.stdout.strip()) if result.returncode == 0 else 0
            self.metrics["git_commits"] = commits

            # Branches
            result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, timeout=5, cwd=REPO_ROOT)
            branches = len(result.stdout.strip().split("\n")) if result.returncode == 0 else 0
            self.metrics["git_branches"] = branches

            # Last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ai"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=REPO_ROOT,
            )
            last_commit = result.stdout.strip() if result.returncode == 0 else "unknown"
            self.metrics["git_last_commit"] = last_commit

        except Exception as e:
            self.metrics["git_error"] = str(e)

    def count_lines_of_code(self):
        """Сколько строк кода реально"""
        total_lines = 0

        for py_file in REPO_ROOT.rglob("*.py"):
            # Пропусти __pycache__ и .venv
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    total_lines += len(f.readlines())
            except:
                pass

        self.metrics["lines_of_code"] = total_lines
        return total_lines

    def get_docker_images(self):
        """Сколько Docker образов есть"""
        dockerfiles = list(REPO_ROOT.rglob("Dockerfile"))
        docker_compose = list(REPO_ROOT.rglob("docker-compose*.yml"))

        self.metrics["dockerfiles"] = len(dockerfiles)
        self.metrics["docker_compose_files"] = len(docker_compose)

    def get_k8s_resources(self):
        """Kubernetes ресурсы"""
        k8s_files = list(REPO_ROOT.rglob("*.yaml")) + list(REPO_ROOT.rglob("*.yml"))
        k8s_files = [f for f in k8s_files if "deployment" in str(f).lower() or "k8s" in str(f).lower()]

        self.metrics["k8s_files"] = len(k8s_files)

    def collect_all(self):
        """Собрать все метрики"""
        print("🔍 Собираю РЕАЛЬНЫЕ метрики...")
        print()

        print("📊 Python файлы:", self.count_python_files())
        print("🧪 Тест файлы:", self.count_test_files())
        print("🏗️ Микросервисы:", self.count_microservices())
        print("📝 Строк кода:", self.count_lines_of_code())

        print("\n📦 Docker & K8s:")
        self.get_docker_images()
        print(f"  • Dockerfiles: {self.metrics['dockerfiles']}")
        print(f"  • Docker Compose: {self.metrics['docker_compose_files']}")

        self.get_k8s_resources()
        print(f"  • K8s файлы: {self.metrics['k8s_files']}")

        print("\n🔗 Git:")
        self.get_git_info()
        print(f"  • Commits: {self.metrics.get('git_commits', 'unknown')}")
        print(f"  • Branches: {self.metrics.get('git_branches', 'unknown')}")
        print(f"  • Last commit: {self.metrics.get('git_last_commit', 'unknown')}")

        print("\n✅ Коллекция завершена!")
        return self.metrics

    def generate_badges(self):
        """Генерировать динамические бейджи"""
        return {
            "python_files": {
                "label": "Python Files",
                "message": str(self.metrics.get("python_files", 0)),
                "color": "blue",
            },
            "test_files": {
                "label": "Test Files",
                "message": str(self.metrics.get("test_files", 0)),
                "color": "green",
            },
            "microservices": {
                "label": "Microservices",
                "message": str(self.metrics.get("microservices", 0)),
                "color": "brightgreen",
            },
            "lines_of_code": {
                "label": "Lines of Code",
                "message": self._format_number(self.metrics.get("lines_of_code", 0)),
                "color": "orange",
            },
            "git_commits": {
                "label": "Git Commits",
                "message": str(self.metrics.get("git_commits", 0)),
                "color": "purple",
            },
            "git_branches": {
                "label": "Git Branches",
                "message": str(self.metrics.get("git_branches", 0)),
                "color": "blue",
            },
        }

    @staticmethod
    def _format_number(num):
        """Форматировать большие числа"""
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        if num >= 1_000:
            return f"{num / 1_000:.1f}k"
        return str(num)

    def print_badges_markdown(self):
        """Печать бейджей в Markdown формате"""
        badges = self.generate_badges()

        print("\n" + "=" * 70)
        print("DYNAMIC BADGES FOR README.md")
        print("=" * 70 + "\n")

        for _badge_id, badge_data in badges.items():
            label = badge_data["label"]
            message = badge_data["message"]
            color = badge_data["color"]

            # Static badge (shields.io)
            badge_url = f"https://img.shields.io/badge/{label.replace(' ', '%20')}-{message}-{color}?style=flat-square"

            # Dynamic badge (using shields.io endpoint)
            markdown = f"![{label}]({badge_url})"

            print(f"{label}:")
            print(f"  {markdown}")
            print(f"  URL: {badge_url}")
            print()


if __name__ == "__main__":
    collector = MetricsCollector()
    collector.collect_all()
    collector.print_badges_markdown()

    # Сохранить как JSON
    output_file = REPO_ROOT / "metrics.json"
    with open(output_file, "w") as f:
        json.dump(collector.metrics, f, indent=2, default=str)

    print(f"\n✅ Метрики сохранены в: {output_file}")
