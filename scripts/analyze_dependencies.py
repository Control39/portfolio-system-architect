#!/usr/bin/env python3
"""Анализ зависимостей между сервисами."""

import re
from collections import defaultdict
from pathlib import Path

IGNORE_DIRS = {
    ".venv",
    "venv",
    "env",
    "repo-env",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".git",
    ".gigacode",
    ".idea",
    ".vscode",
    "logs",
    "plans",
    "reports",
    "tests",
    "utils",
    "docs",
    "examples",
    "sandbox",
    "legacy",
    "node_modules",
    "htmlcov",
    "chroma_db",
    "postgres",
    "prometheus",
}

SERVICES = {
    "ai_config_manager",
    "ai_provider_manager",
    "assistant_orchestrator",
    "auth_service",
    "career_development",
    "chat_backend",
    "cognitive_agent",
    "competency_gap_engine",
    "context_builder",
    "decision_engine",
    "embedding_agent",
    "infra_orchestrator",
    "it_compass",
    "job_automation_agent",
    "knowledge_graph",
    "mcp_server",
    "ml_model_registry",
    "portfolio_organizer",
    "project_mcp",
    "system_proof",
    "template_service",
    "thought_architecture",
}

HTTP_PATTERNS = [
    r'httpx\.(get|post|put|delete|patch)\([^)]*["\'](https?://[^"\']+)["\']',
    r'requests\.(get|post|put|delete|patch)\([^)]*["\'](https?://[^"\']+)["\']',
]


def should_ignore(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS or (part.startswith(".") and part not in {".agents", ".github"}):
            return True
    return False


def find_py_files(service_path: Path) -> list[Path]:
    py_files = []
    src_path = service_path / "src"
    if src_path.exists():
        py_files.extend(src_path.rglob("*.py"))
    for py_file in service_path.rglob("*.py"):
        if should_ignore(py_file) or "test" in py_file.name.lower() or "__pycache__" in str(py_file):
            continue
        if src_path.exists() and src_path in py_file.parents:
            continue
        py_files.append(py_file)
    return py_files


def main():
    repo_root = Path(__file__).parent.parent
    dependencies = defaultdict(lambda: {"calls": set(), "src_imports": set(), "file_count": 0})

    print("🔍 АНАЛИЗ ЗАВИСИМОСТЕЙ МЕЖДУ СЕРВИСАМИ")
    print("=" * 60)

    for service in sorted(SERVICES):
        service_path = repo_root / "apps" / service
        if not service_path.exists():
            continue

        py_files = find_py_files(service_path)
        dependencies[service]["file_count"] = len(py_files)

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in HTTP_PATTERNS:
                    for match in re.findall(pattern, content, re.IGNORECASE):
                        url = match[-1] if isinstance(match, tuple) else match
                        host_match = re.search(r"(?:http://|https://)?([a-z_\-]+)(?:\.local|:\d+|/|$)", url)
                        if host_match:
                            candidate = host_match.group(1).replace("-", "_")
                            if candidate in SERVICES and candidate != service:
                                dependencies[service]["calls"].add(candidate)
                for src_match in re.findall(r"from src\.(\w+) import", content):
                    dependencies[service]["src_imports"].add(src_match)
            except Exception as e:
                print(f"  ⚠️ {py_file.name}: {e}")

    print("\n📊 СВОДКА:")
    for service in sorted(SERVICES):
        if service not in dependencies:
            continue
        calls = dependencies[service]["calls"]
        src_imports = dependencies[service]["src_imports"]
        if calls or src_imports:
            print(f"\n🔹 {service}:")
            if calls:
                print(f"    📤 ВЫЗЫВАЕТ: {', '.join(sorted(calls))}")
            if src_imports:
                print(f"    📦 ИМПОРТЫ ИЗ SRC: {', '.join(sorted(src_imports))}")

    print("\n" + "=" * 60)
    print(f"✅ Всего сервисов: {len([s for s in SERVICES if (repo_root / 'apps' / s).exists()])}")
    print(f"📄 Всего .py файлов: {sum(d['file_count'] for d in dependencies.values())}")


if __name__ == "__main__":
    main()
