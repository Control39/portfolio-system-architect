"""
Тесты для классификатора монорепозитория
"""

import os
import sys

import pytest


# Добавьте путь к скрипту, если он в другой папке
sys.path.insert(0, os.path.abspath("."))
from classify_v4 import MonorepoClassifier


@pytest.fixture
def tmp_repo(tmp_path):
    """Создаёт изолированную директорию для каждого теста"""
    return tmp_path


@pytest.fixture
def classifier(tmp_repo):
    """Инициализирует классификатор без ripgrep"""
    return MonorepoClassifier(str(tmp_repo), use_ripgrep=False)


# ─────────────────────────────────────────────────────────────
# 1. Тесты логики исключения / переопределения
# ─────────────────────────────────────────────────────────────
class TestExclusionLogic:
    def test_excludes_venv_without_critical(self, classifier, tmp_repo):
        venv = tmp_repo / ".venv"
        venv.mkdir()
        (venv / "pyvenv.cfg").touch()

        excluded, reason = classifier._is_excluded(venv)
        assert excluded is True
        assert "чёрном списке" in reason

    def test_overrides_excluded_dir_with_critical_file(self, classifier, tmp_repo):
        # .env в чёрном списке, но с main.py внутри -> не исключать
        env_dir = tmp_repo / ".env"
        env_dir.mkdir()
        (env_dir / "main.py").touch()
        (env_dir / "Dockerfile").touch()

        excluded, reason = classifier._is_excluded(env_dir)
        assert excluded is False
        assert "переопределено" in reason


# ─────────────────────────────────────────────────────────────
# 2. Тесты извлечения признаков
# ─────────────────────────────────────────────────────────────
class TestFeatureExtraction:
    def test_microservice_features(self, classifier, tmp_repo):
        (tmp_repo / "main.py").touch()
        (tmp_repo / "Dockerfile").touch()
        (tmp_repo / "requirements.txt").touch()
        (tmp_repo / "tests").mkdir()
        (tmp_repo / "tests" / "test_main.py").touch()

        features = classifier._extract_features(tmp_repo)
        assert features["has_main"] is True
        assert features["has_dockerfile"] is True
        assert features["has_requirements"] is True
        assert features["has_tests"] is True

    def test_library_features(self, classifier, tmp_repo):
        (tmp_repo / "setup.py").touch()
        (tmp_repo / "pyproject.toml").touch()
        (tmp_repo / "src").mkdir()
        (tmp_repo / "src" / "__init__.py").touch()

        features = classifier._extract_features(tmp_repo)
        assert features["has_setup"] is True
        assert features["has_main"] is False
        assert features["has_src"] is True

    def test_infrastructure_terraform(self, classifier, tmp_repo):
        (tmp_repo / "main.tf").touch()
        (tmp_repo / "variables.tf").touch()
        (tmp_repo / "terragrunt.hcl").touch()

        features = classifier._extract_features(tmp_repo)
        assert features["has_terraform"] is True


# ─────────────────────────────────────────────────────────────
# 3. Тесты классификации ролей
# ────────────────────────────────────────────────────────────
class TestRoleDetermination:
    def test_classify_microservice(self, classifier, tmp_repo):
        (tmp_repo / "main.py").touch()
        (tmp_repo / "Dockerfile").touch()
        (tmp_repo / "tests").mkdir()

        features = classifier._extract_features(tmp_repo)
        role, conf, reasons = classifier._determine_role(features, tmp_repo.name)

        assert role == "microservice"
        assert conf >= 0.95
        assert any("Точка входа" in r for r in reasons)

    def test_classify_library(self, classifier, tmp_repo):
        (tmp_repo / "setup.py").touch()
        (tmp_repo / "src").mkdir()

        features = classifier._extract_features(tmp_repo)
        role, conf, _reasons = classifier._determine_role(features, tmp_repo.name)

        assert role == "library"
        assert conf >= 0.90

    def test_classify_infrastructure_compose_only(self, classifier, tmp_repo):
        (tmp_repo / "docker-compose.yml").touch()
        (tmp_repo / "Makefile").touch()

        features = classifier._extract_features(tmp_repo)
        role, conf, _reasons = classifier._determine_role(features, tmp_repo.name)

        assert role == "infrastructure"
        assert conf >= 0.85


# ─────────────────────────────────────────────────────────────
# 4. Тесты поиска циклов (3-color DFS)
# ─────────────────────────────────────────────────────────────
class TestCycleDetection:
    def test_find_simple_cycle(self, classifier, tmp_repo):
        # Граф: A -> B -> C -> A
        classifier.projects = [
            type("obj", (object,), {"name": "A", "dependencies": ["B"]})(),
            type("obj", (object,), {"name": "B", "dependencies": ["C"]})(),
            type("obj", (object,), {"name": "C", "dependencies": ["A"]})(),
        ]
        classifier.is_monorepo = True
        classifier.use_ripgrep = True

        cycles = classifier.find_cycles()
        assert len(cycles) == 1
        assert set(cycles[0].cycle) == {"A", "B", "C"}

    def test_no_cycle_linear(self, classifier, tmp_repo):
        # Граф: A -> B -> C (без возврата)
        classifier.projects = [
            type("obj", (object,), {"name": "A", "dependencies": ["B"]})(),
            type("obj", (object,), {"name": "B", "dependencies": ["C"]})(),
            type("obj", (object,), {"name": "C", "dependencies": []})(),
        ]
        classifier.is_monorepo = True
        classifier.use_ripgrep = True

        cycles = classifier.find_cycles()
        assert len(cycles) == 0

    def test_detect_cross_cycle(self, classifier, tmp_repo):
        # Граф: A -> B, A -> C, B -> D, C -> D, D -> A (сложный цикл)
        classifier.projects = [
            type("obj", (object,), {"name": "A", "dependencies": ["B", "C"]})(),
            type("obj", (object,), {"name": "B", "dependencies": ["D"]})(),
            type("obj", (object,), {"name": "C", "dependencies": ["D"]})(),
            type("obj", (object,), {"name": "D", "dependencies": ["A"]})(),
        ]
        classifier.is_monorepo = True
        classifier.use_ripgrep = True

        cycles = classifier.find_cycles()
        assert len(cycles) == 1
        assert "A" in cycles[0].cycle and "D" in cycles[0].cycle


# ─────────────────────────────────────────────────────────────
# 5. Тесты детекции монорепозитория
# ─────────────────────────────────────────────────────────────
class TestMonorepoDetection:
    def test_detect_by_apps_folder(self, classifier, tmp_repo):
        (tmp_repo / "apps").mkdir()
        (tmp_repo / "libs").mkdir()

        assert classifier.detect_monorepo() is True
        assert classifier.is_monorepo is True

    def test_detect_by_config_file(self, classifier, tmp_repo):
        (tmp_repo / "nx.json").touch()

        assert classifier.detect_monorepo() is True

    def test_not_monorepo(self, classifier, tmp_repo):
        (tmp_repo / "main.py").touch()
        (tmp_repo / "utils").mkdir()

        assert classifier.detect_monorepo() is False
