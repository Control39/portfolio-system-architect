"""
Monorepo Classifier - классификация структуры репозитория
"""

import os
from dataclasses import dataclass
from pathlib import Path


EXCLUDED_DIRS = {".venv", "venv", "node_modules", ".git", "__pycache__", ".env"}
CRITICAL_FILES = {"main.py", "Dockerfile", "setup.py", "package.json", "Makefile"}


@dataclass
class Cycle:
    """Представление цикла зависимостей"""

    cycle: list[str]
    severity: str = "high"


class MonorepoClassifier:
    """Классификатор монорепозитория"""

    def __init__(self, repo_path: str, use_ripgrep: bool = False):
        self.repo_path = Path(repo_path)
        self.use_ripgrep = use_ripgrep
        self.projects: list = []
        self.is_monorepo = False

    def _is_excluded(self, path: Path) -> tuple[bool, str]:
        """Проверка исключения директории"""
        name = path.name

        # Проверка на критические файлы
        if any(path.glob("*")):
            for file in path.iterdir():
                if file.is_file() and file.name in CRITICAL_FILES:
                    return False, f"переопределено критическим файлом {file.name}"

        # Проверка чёрного списка
        if name in EXCLUDED_DIRS:
            return True, f"директория '{name}' в чёрном списке"

        return False, ""

    def _extract_features(self, path: Path) -> dict:
        """Извлечение признаков из директории (рекурсивно)"""
        features = {
            "has_main": False,
            "has_dockerfile": False,
            "has_requirements": False,
            "has_tests": False,
            "has_setup": False,
            "has_src": False,
            "has_terraform": False,
            "has_docker_compose": False,
        }

        if not path.exists():
            return features

        # Проверка файлов в текущей директории и поддиректориях (до 2 уровней)
        for root, dirs, files in os.walk(path, topdown=True):
            root_path = Path(root)

            # Пропуск исключённых директорий
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith("_")]

            # Глубина сканирования (2 уровня)
            if root_path.relative_to(path).parts.__len__() >= 2:
                continue

            for item in files:
                if item == "main.py":
                    features["has_main"] = True
                elif item == "Dockerfile":
                    features["has_dockerfile"] = True
                elif item == "requirements.txt":
                    features["has_requirements"] = True
                elif item in ("setup.py", "setup.cfg") or item == "pyproject.toml":
                    features["has_setup"] = True
                elif item.endswith(".tf") or item == "terragrunt.hcl":
                    features["has_terraform"] = True
                elif item in ("docker-compose.yml", "docker-compose.yaml", "compose.yml"):
                    features["has_docker_compose"] = True

            for item in dirs:
                if item == "tests" or item == "test":
                    features["has_tests"] = True
                elif item == "src":
                    features["has_src"] = True

        return features

    def _determine_role(self, features: dict, name: str) -> tuple[str, float, list[str]]:
        """Определение роли компонента"""
        reasons = []
        confidence = 0.0

        # Microservice detection
        if features["has_main"] and features["has_dockerfile"]:
            confidence = 0.95
            reasons.append("Точка входа (main.py) и Dockerfile")
            if features["has_tests"]:
                confidence = 0.98
                reasons.append("Есть тесты")
            return "microservice", confidence, reasons

        # Library detection
        if features["has_setup"] or features["has_src"]:
            confidence = 0.90
            reasons.append("Библиотека Python (setup.py/pyproject.toml)")
            if features["has_src"]:
                reasons.append("Имеет структуру src/")
            return "library", confidence, reasons

        # Infrastructure detection
        if features["has_terraform"]:
            confidence = 0.95
            reasons.append("Инфраструктура Terraform")
            return "infrastructure", confidence, reasons

        if features["has_docker_compose"] or features["has_requirements"] or features["has_dockerfile"]:
            confidence = 0.85
            reasons.append("Инфраструктура (docker-compose/requirements)")
            return "infrastructure", confidence, reasons

        return "unknown", 0.5, ["Недостаточно признаков"]

    def find_cycles(self) -> list[Cycle]:
        """Поиск циклов зависимостей (3-color DFS)"""
        cycles = []
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {p.name: WHITE for p in self.projects}
        path = []

        def dfs(node_name: str):
            node = next((p for p in self.projects if p.name == node_name), None)
            if not node:
                return

            color[node_name] = GRAY
            path.append(node_name)

            for dep in node.dependencies:
                if color.get(dep) == GRAY:
                    # Найдён цикл
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:]
                    cycles.append(Cycle(cycle=cycle))
                elif color.get(dep) == WHITE:
                    dfs(dep)

            path.pop()
            color[node_name] = BLACK

        for project in self.projects:
            if color[project.name] == WHITE:
                dfs(project.name)

        return cycles

    def detect_monorepo(self) -> bool:
        """Определение монорепозитория"""
        # Проверка папок apps/libs
        if (self.repo_path / "apps").exists() or (self.repo_path / "libs").exists():
            self.is_monorepo = True
            return True

        # Проверка конфигурационных файлов
        config_files = {"nx.json", "lerna.json", "pnpm-workspace.yaml", "turbo.json"}
        for config in config_files:
            if (self.repo_path / config).exists():
                self.is_monorepo = True
                return True

        self.is_monorepo = False
        return False


def analyze_repo(repo_path: str):
    """Анализ репозитория с выводом результатов"""
    print(f"\n{'=' * 60}")
    print(f"Анализ репозитория: {repo_path}")
    print(f"{'=' * 60}\n")

    classifier = MonorepoClassifier(repo_path, use_ripgrep=False)

    # Детекция монорепозитория
    is_mono = classifier.detect_monorepo()
    print(f"📊 Монорепозиторий: {'✅ Да' if is_mono else '❌ Нет'}\n")

    if not is_mono:
        print(
            "⚠️ Не найден монорепозиторий. Проверьте наличие папок 'apps/', 'libs/' или файлов 'nx.json', 'lerna.json'"
        )
        return

    # Сканирование проектов
    print("🔍 Сканирование компонентов...\n")

    projects = []
    apps_path = Path(repo_path) / "apps"
    if apps_path.exists():
        for item in apps_path.iterdir():
            if item.is_dir() and not item.name.startswith("_") and item.name not in EXCLUDED_DIRS:
                excluded, _reason = classifier._is_excluded(item)
                if not excluded:
                    projects.append(type("obj", (object,), {"name": item.name, "path": item, "dependencies": []})())

    print(f"📁 Найдено компонентов: {len(projects)}\n")

    for project in projects:
        features = classifier._extract_features(project.path)
        role, conf, reasons = classifier._determine_role(features, project.name)

        print(f"  • {project.name}")
        print(f"    Роль: {role} (confidence: {conf:.0%})")
        if reasons:
            print(f"    Признаки: {', '.join(reasons[:2])}")
        print()

    # Поиск циклов
    print("🔄 Поиск циклов зависимостей...")
    cycles = classifier.find_cycles()
    if cycles:
        print(f"  ⚠️ Обнаружено {len(cycles)} циклов:")
        for cycle in cycles:
            print(f"    - {' -> '.join(cycle.cycle)} -> {cycle.cycle[0]}")
    else:
        print("  ✅ Циклов не обнаружено")

    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "."

    analyze_repo(repo_path)
