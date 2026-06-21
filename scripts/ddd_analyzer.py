#!/usr/bin/env python3
"""
DDD Analyzer - Глубокий анализ DDD-архитектуры
Анализирует:
- Доменные контексты (bounded contexts)
- Сущности и агрегаты
- Сервисы и репозитории
- Связи между сервисами
- Паттерны и анти-паттерны
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class DDDAnalyzer:
    """Анализатор DDD-архитектуры"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.apps_path = self.repo_path / "apps"
        self.src_path = self.repo_path / "src"
        self.scripts_path = self.repo_path / "scripts"
        self.agents_path = self.repo_path / "agents"

        # Результаты анализа
        self.results = {
            "domains": {},
            "services": {},
            "entities": {},
            "value_objects": {},
            "repositories": {},
            "dependencies": {},
            "api_contracts": {},
            "cross_service_calls": {},
            "events": {},
            "issues": [],
        }

        # Паттерны для распознавания DDD элементов
        self.domain_patterns = {
            "entity": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?entity", re.IGNORECASE),
            "value_object": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?value\s*object", re.IGNORECASE),
            "aggregate": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?aggregate", re.IGNORECASE),
            "repository": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?repository", re.IGNORECASE),
            "service": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?(?:domain\s*)?service", re.IGNORECASE),
            "event": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?event", re.IGNORECASE),
            "aggregate_root": re.compile(r"class\s+(\w+)(?:\(.*\))?:\s*#\s*(?:@)?aggregate\s*root", re.IGNORECASE),
        }

    def analyze(self) -> dict[str, Any]:
        """Запуск полного анализа"""
        print("🔍 Запуск DDD анализа репозитория...")
        print(f"📁 Путь: {self.repo_path}")

        # 1. Анализ структуры директорий
        self._analyze_structure()

        # 2. Анализ всех Python файлов
        self._analyze_python_files()

        # 3. Анализ зависимостей между сервисами
        self._analyze_dependencies()

        # 4. Анализ API контрактов
        self._analyze_api_contracts()

        # 5. Поиск проблем в архитектуре
        self._find_architecture_issues()

        # 6. Генерация отчета
        self._generate_report()

        return self.results

    def _analyze_structure(self):
        """Анализ структуры директорий"""
        print("📂 Анализ структуры...")

        # Анализ apps
        if self.apps_path.exists():
            for app_dir in self.apps_path.iterdir():
                if app_dir.is_dir() and not app_dir.name.startswith("."):
                    domain_name = app_dir.name
                    self.results["domains"][domain_name] = {
                        "path": str(app_dir.relative_to(self.repo_path)),
                        "has_src": (app_dir / "src").exists(),
                        "has_tests": (app_dir / "tests").exists(),
                        "has_init": (app_dir / "__init__.py").exists(),
                        "sub_domains": [],
                    }

                    # Проверка на под-домены
                    if (app_dir / "src").exists():
                        for sub_dir in (app_dir / "src").iterdir():
                            if sub_dir.is_dir() and not sub_dir.name.startswith("_"):
                                self.results["domains"][domain_name]["sub_domains"].append(sub_dir.name)

        # Анализ agents (агенты)
        if self.agents_path.exists():
            for agent_dir in self.agents_path.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                    domain_name = agent_dir.name
                    self.results["domains"][domain_name] = {
                        "path": str(agent_dir.relative_to(self.repo_path)),
                        "has_src": (agent_dir / "src").exists(),
                        "has_tests": (agent_dir / "tests").exists(),
                        "has_init": (agent_dir / "__init__.py").exists(),
                        "sub_domains": [],
                        "type": "agent",
                    }

                    # Проверка на под-домены
                    if (agent_dir / "src").exists():
                        for sub_dir in (agent_dir / "src").iterdir():
                            if sub_dir.is_dir() and not sub_dir.name.startswith("_"):
                                self.results["domains"][domain_name]["sub_domains"].append(sub_dir.name)

        # Анализ src
        if self.src_path.exists():
            for src_dir in self.src_path.iterdir():
                if src_dir.is_dir() and not src_dir.name.startswith("."):
                    self.results["services"][src_dir.name] = {
                        "path": str(src_dir.relative_to(self.repo_path)),
                        "type": "core_library",
                    }

        print(f"   ✅ Найдено доменов: {len(self.results['domains'])}")
        print(f"   ✅ Найдено сервисов: {len(self.results['services'])}")

    def _analyze_python_files(self):
        """Анализ Python файлов на предмет DDD паттернов"""
        print("🐍 Анализ Python файлов...")

        all_py_files = []

        # Собираем все .py файлы
        for py_file in self.repo_path.rglob("*.py"):
            if not self._is_excluded(py_file):
                all_py_files.append(py_file)

        print(f"   📄 Найдено файлов: {len(all_py_files)}")

        for py_file in all_py_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Определяем контекст (домен)
                context = self._detect_context(py_file)

                # Анализируем содержимое
                self._analyze_file_content(content, py_file, context)

            except Exception as e:
                print(f"   ⚠️ Ошибка при анализе {py_file}: {e}")

    def _detect_context(self, file_path: Path) -> str:
        """Определение доменного контекста по пути"""
        rel_path = file_path.relative_to(self.repo_path)
        parts = rel_path.parts

        # Ищем apps/xxx
        if "apps" in parts:
            idx = parts.index("apps")
            if idx + 1 < len(parts):
                return parts[idx + 1]

        # Ищем agents/xxx
        if "agents" in parts:
            idx = parts.index("agents")
            if idx + 1 < len(parts):
                return parts[idx + 1]

        # Ищем src/xxx
        if "src" in parts:
            idx = parts.index("src")
            if idx + 1 < len(parts):
                return parts[idx + 1]

        return "shared"

    def _analyze_file_content(self, content: str, file_path: Path, context: str):
        """Анализ содержимого файла"""

        # Поиск классов и паттернов
        for pattern_name, pattern in self.domain_patterns.items():
            matches = pattern.findall(content)
            for match in matches:
                if context not in self.results.get(pattern_name, {}):
                    self.results[pattern_name] = self.results.get(pattern_name, {})
                    self.results[pattern_name][context] = []

                self.results[pattern_name][context].append(
                    {"name": match, "file": str(file_path.relative_to(self.repo_path))}
                )

        # Поиск импортов (зависимости)
        import_pattern = re.compile(r"^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE)
        imports = import_pattern.findall(content)

        for imp in imports:
            if imp.startswith("apps.") or imp.startswith("agents."):
                parts = imp.split(".")
                if len(parts) >= 2:
                    target_context = parts[1]
                    if context != target_context:
                        self.results["cross_service_calls"].setdefault(context, {})
                        self.results["cross_service_calls"][context].setdefault(target_context, [])
                        self.results["cross_service_calls"][context][target_context].append(
                            str(file_path.relative_to(self.repo_path))
                        )

        # Поиск API эндпоинтов (FastAPI, Flask, Django)
        api_patterns = [
            re.compile(r"@app\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"),
            re.compile(r"@router\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"),
            re.compile(r"@api\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"),
        ]

        for api_pattern in api_patterns:
            matches = api_pattern.findall(content)
            for method, path in matches:
                if context not in self.results["api_contracts"]:
                    self.results["api_contracts"][context] = []

                self.results["api_contracts"][context].append(
                    {"method": method.upper(), "path": path, "file": str(file_path.relative_to(self.repo_path))}
                )

        # Поиск событий
        event_patterns = [
            re.compile(r"class\s+(\w+)\s*\(.*Event.*\)"),
            re.compile(r"class\s+(\w+)\s*\(.*Event\)"),
            re.compile(r"@event\s+class\s+(\w+)"),
        ]

        for event_pattern in event_patterns:
            matches = event_pattern.findall(content)
            for match in matches:
                if context not in self.results["events"]:
                    self.results["events"][context] = []
                self.results["events"][context].append(
                    {"name": match, "file": str(file_path.relative_to(self.repo_path))}
                )

    def _analyze_dependencies(self):
        """Анализ зависимостей между сервисами"""
        print("🔗 Анализ зависимостей...")

        for context, deps in self.results.get("cross_service_calls", {}).items():
            self.results["dependencies"][context] = list(deps.keys())

        print(f"   ✅ Найдено связей: {len(self.results['dependencies'])}")

    def _analyze_api_contracts(self):
        """Анализ API контрактов"""
        print("📡 Анализ API контрактов...")

        total_apis = sum(len(apis) for apis in self.results["api_contracts"].values())
        print(f"   ✅ Найдено API эндпоинтов: {total_apis}")

    def _find_architecture_issues(self):
        """Поиск проблем в архитектуре"""
        print("🔍 Поиск архитектурных проблем...")

        issues = self.results["issues"]

        # 1. Проверка на циклические зависимости
        for context, deps in self.results.get("dependencies", {}).items():
            for dep in deps:
                if dep in self.results.get("dependencies", {}) and context in self.results["dependencies"][dep]:
                    issues.append(
                        {
                            "type": "circular_dependency",
                            "severity": "high",
                            "message": f"Циклическая зависимость между {context} и {dep}",
                            "context": context,
                        }
                    )

        # 2. Проверка на отсутствие тестов
        for domain, info in self.results.get("domains", {}).items():
            if not info.get("has_tests"):
                issues.append(
                    {
                        "type": "no_tests",
                        "severity": "medium",
                        "message": f"Домен {domain} не имеет тестов",
                        "context": domain,
                    }
                )

        # 3. Проверка на отсутствие src директории
        for domain, info in self.results.get("domains", {}).items():
            if not info.get("has_src"):
                issues.append(
                    {
                        "type": "no_src_dir",
                        "severity": "low",
                        "message": f"Домен {domain} не имеет src директории",
                        "context": domain,
                    }
                )

        # 4. Проверка на отсутствие __init__.py
        for domain, info in self.results.get("domains", {}).items():
            if not info.get("has_init"):
                issues.append(
                    {
                        "type": "missing_init",
                        "severity": "low",
                        "message": f"Домен {domain} не имеет __init__.py",
                        "context": domain,
                    }
                )

        # 5. Проверка на большие файлы
        for domain, info in self.results.get("domains", {}).items():
            path_parts = info.get("path", "").split("/")
            domain_path = self.repo_path
            for part in path_parts:
                domain_path = domain_path / part

            if domain_path.exists():
                for py_file in domain_path.rglob("*.py"):
                    if py_file.is_file():
                        size = py_file.stat().st_size
                        if size > 100000:  # 100KB
                            issues.append(
                                {
                                    "type": "large_file",
                                    "severity": "medium",
                                    "message": f"Большой файл: {py_file.relative_to(domain_path)} ({size/1024:.1f}KB)",
                                    "context": domain,
                                }
                            )

        print(f"   ✅ Найдено проблем: {len(issues)}")

    def _is_excluded(self, file_path: Path) -> bool:
        """Проверка, исключен ли файл"""
        excluded = [".venv", "__pycache__", ".git", "node_modules", ".pytest_cache", ".mypy_cache", "venv"]
        return any(part in excluded for part in file_path.parts)

    def _generate_report(self):
        """Генерация отчета"""
        print("📊 Генерация отчета...")

        # Сохраняем результаты
        report_path = self.repo_path / "ddd_analysis_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Генерация человеко-читаемого отчета
        self._generate_human_report()

        print(f"✅ Отчет сохранен: {report_path}")

    def _generate_human_report(self):
        """Генерация человеко-читаемого отчета"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("🏗️  DDD АРХИТЕКТУРНЫЙ АНАЛИЗ")
        report_lines.append("=" * 60)
        report_lines.append(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Домены
        report_lines.append("📂 ДОМЕНЫ (Bounded Contexts):")
        for domain, info in self.results.get("domains", {}).items():
            report_lines.append(f"  📁 {domain}")
            report_lines.append(f"     Путь: {info['path']}")
            report_lines.append(f"     Тесты: {'✅' if info.get('has_tests') else '❌'}")
            if info.get("sub_domains"):
                report_lines.append(f"     Под-домены: {', '.join(info['sub_domains'])}")
        report_lines.append("")

        # API Контракты
        report_lines.append("📡 API КОНТРАКТЫ:")
        for context, apis in self.results.get("api_contracts", {}).items():
            report_lines.append(f"  📍 {context}: {len(apis)} эндпоинтов")
            for api in apis[:3]:
                report_lines.append(f"     {api['method']} {api['path']}")
        report_lines.append("")

        # Зависимости
        report_lines.append("🔗 ЗАВИСИМОСТИ МЕЖДУ СЕРВИСАМИ:")
        for context, deps in self.results.get("dependencies", {}).items():
            if deps:
                report_lines.append(f"  {context} → {', '.join(deps)}")
        report_lines.append("")

        # Проблемы
        report_lines.append("🐛 НАЙДЕННЫЕ ПРОБЛЕМЫ:")
        if self.results.get("issues"):
            for issue in self.results["issues"]:
                severity = "🔴" if issue["severity"] == "high" else "🟡" if issue["severity"] == "medium" else "🟢"
                report_lines.append(f"  {severity} [{issue['severity']}] {issue['message']}")
        else:
            report_lines.append("  ✅ Проблем не найдено!")
        report_lines.append("")

        report_lines.append("=" * 60)

        # Сохраняем
        report_path = self.repo_path / "ddd_analysis_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        # Выводим в консоль
        print("\n".join(report_lines))


def main():
    """Запуск анализа"""
    import sys

    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    analyzer = DDDAnalyzer(repo_path)
    results = analyzer.analyze()

    print("\n📊 СТАТИСТИКА:")
    print(f"   Доменов: {len(results['domains'])}")
    print(f"   API эндпоинтов: {sum(len(v) for v in results['api_contracts'].values())}")
    print(f"   Связей между сервисами: {len(results['dependencies'])}")
    print(f"   Проблем найдено: {len(results['issues'])}")


if __name__ == "__main__":
    main()
