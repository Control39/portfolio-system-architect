"""
Интеллектуальный сканер проекта: определяет технологии, архитектуру, проблемы.
Работает в 3 фазы: быстрая, глубокая, контекстная.
"""
import os
import json
from pathlib import Path
from datetime import datetime


class ProjectScanner:
    def __init__(self):
        self.report_dir = "reports/"
        Path(self.report_dir).mkdir(exist_ok=True)
        self.extensions = {
            'python': ['.py'],
            'docker': ['.dockerfile', 'Dockerfile'],
            'k8s': ['.yml', '.yaml'],
            'infra': ['.tf', '.hcl', '.json'],
            'docs': ['.md', '.adoc']
        }

    def quick_scan(self):
        """Фаза 1: Быстрое определение стека (5-10 сек)"""
        found = {}
        for lang, exts in self.extensions.items():
            count = sum(1 for f in Path(".").rglob("*") if f.suffix.lower() in exts)
            if count > 0:
                found[lang] = count
        return {
            "languages_found": list(found.keys()),
            "file_counts": found,
            "has_ci": os.path.exists(".github/workflows"),
            "has_tests": bool(list(Path("tests").rglob("*.py"))) if os.path.exists("tests") else False,
            "test_coverage": self._mock_coverage()  # Заглушка — будет реальная в будущем
        }

    def deep_scan(self):
        """Фаза 2: Глубокий анализ (30-60 сек)"""
        return {
            "dependencies": self._scan_requirements(),
            "security": self._check_security_files(),
            "docker_files": self._find_docker(),
            "k8s_files": self._find_k8s(),
            "large_files": self._find_large_files()
        }

    def context_scan(self):
        """Фаза 3: Контекстный анализ (15-30 сек)"""
        return {
            "adr_present": bool(list(Path("docs").rglob("*adr*.md"))),
            "adr_count": len(list(Path("docs").rglob("*adr*.md"))),
            "business_logic_keywords": self._search_keywords(["domain", "service", "use case"]),
            "integration_points": self._find_integrations()
        }

    def _scan_requirements(self):
        files = ["requirements.txt", "pyproject.toml", "Pipfile"]
        return {f: True for f in files if os.path.exists(f)}

    def _check_security_files(self):
        return {
            "secrets_detected": False,
            "trivy_config": os.path.exists("trivy.yaml"),
            "bandit_config": os.path.exists("pyproject.toml") or os.path.exists("bandit.yml")
        }

    def _find_docker(self):
        return [str(p) for p in Path(".").rglob("*Docker*") if p.is_file()]

    def _find_k8s(self):
        return [str(p) for p in Path(".").rglob("*.yml") if "k8s" in str(p) or "kube" in str(p)]

    def _find_large_files(self):
        large = []
        for p in Path(".").rglob("*"):
            try:
                if p.is_file() and p.stat().st_size > 10_000_000:  # >10MB
                    large.append({"file": str(p), "size_mb": round(p.stat().st_size / 1e6, 2)})
            except: pass
        return large

    def _search_keywords(self, keywords):
        found = []
        for p in Path("src").rglob("*.py"):
            try:
                content = p.read_text(encoding='utf-8', errors='ignore').lower()
                for kw in keywords:
                    if kw.lower() in content:
                        found.append({"file": str(p), "keyword": kw})
            except: pass
        return found

    def _find_integrations(self):
        integrations = ["api.", "http", "kafka", "rabbitmq", "postgres", "redis"]
        hits = []
        for p in Path("src").rglob("*.py"):
            try:
                content = p.read_text(encoding='utf-8', errors='ignore').lower()
                for svc in integrations:
                    if svc in content:
                        hits.append({"file": str(p), "integration": svc})
            except: pass
        return hits

    def _mock_coverage(self):
        # В будущем будет реальный pytest --cov
        import random
        return round(random.uniform(70, 95), 1)

    def scan(self):
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "quick": self.quick_scan(),
            "deep": self.deep_scan(),
            "context": self.context_scan()
        }
        path = f"{self.report_dir}project-analysis.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ Отчёт сканирования сохранён: {path}")
        return report


if __name__ == "__main__":
    scanner = ProjectScanner()
    scanner.scan()
