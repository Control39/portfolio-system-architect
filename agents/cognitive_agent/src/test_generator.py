"""
Модуль для автоматической генерации тестов

Использует PromptEngine, LLM и BusinessLogicAnalyzer для умной генерации тестов.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import structlog

from agents.cognitive_agent.src.prompt_engine import PromptEngine

logger = structlog.get_logger(__name__)

# Импорт BusinessLogicAnalyzer для умной генерации
try:
    from agents.cognitive_agent.src.business_logic_analyzer import (
        BusinessLogicAnalyzer,
        TestCoverageCalculator,
    )
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False
    logger.warning("BusinessLogicAnalyzer not available, using basic generation")


class TestGenerator:
    """
    Генератор тестов для Python кода

    Использует шаблоны из PromptEngine и LLM для автоматической генерации тестов.
    """

    def __init__(self, project_path: str, prompts_dir: Path | None = None):
        """
        Инициализация TestGenerator

        Args:
            project_path: Путь к проекту
            prompts_dir: Путь к директории с шаблонами (по умолчанию agents/cognitive_agent/prompts)
        """
        self.project_path = Path(project_path)
        self.prompts_dir = prompts_dir or Path("agents/cognitive_agent/prompts")

        # Инициализация PromptEngine
        self.prompt_engine = PromptEngine(prompts_dir=self.prompts_dir)
        logger.info(f"✅ TestGenerator initialized: {self.project_path}")

    def _detect_framework(self, file_path: Path) -> str:
        """
        Определить фреймворк по файлу

        Args:
            file_path: Путь к файлу кода

        Returns:
            Название фреймворка (fastapi, flask, django, base)
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # FastAPI
            if "from fastapi" in content or "import fastapi" in content:
                return "fastapi"

            # Flask
            if "from flask" in content or "import flask" in content:
                return "flask"

            # Django
            if "from django" in content or "import django" in content:
                return "django"

            return "base"
        except Exception as e:
            logger.warning(f"Ошибка при определении фреймворка для {file_path}: {e}")
            return "base"

    def _detect_file_type(self, file_path: Path, framework: str) -> str:
        """
        Определить тип файла для выбора шаблона

        Args:
            file_path: Путь к файлу
            framework: Фреймворк

        Returns:
            Тип файла (api, models, unit, integration)
        """
        name = file_path.name.lower()

        # FastAPI
        if framework == "fastapi":
            if "api" in name or "endpoint" in name:
                return "api"
            elif "integration" in name or "test_" in name or "_test" in name:
                return "integration"
            elif "model" in name or "schema" in name:
                return "api"  # FastAPI использует api.md для моделей

        # Flask
        if framework == "flask":
            if "api" in name or "endpoint" in name or "view" in name or "route" in name:
                return "api"

        # Django
        if framework == "django":
            if "model" in name:
                return "models"
            elif "view" in name or "form" in name:
                return "unit"  # Django unit тесты

        # Base / Other
        if "model" in name:
            return "models"
        elif "test" in name or "spec" in name:
            return "unit"

        return "unit"

    def _get_template_path(self, framework: str, file_type: str) -> str:
        """
        Получить путь к шаблону по фреймворку и типу файла

        Args:
            framework: Фреймворк (fastapi, flask, django, base)
            file_type: Тип файла (api, models, unit, integration)

        Returns:
            Путь к шаблону (например, "python/fastapi/api")
        """
        framework_templates = {
            "fastapi": {
                "api": "python/fastapi/api",
                "integration": "python/fastapi/integration",
            },
            "flask": {
                "api": "python/flask/api",
            },
            "django": {
                "models": "python/django/unit",
                "unit": "python/django/unit",
            },
            "base": {
                "unit": "python/base/unit",
                "models": "python/base/unit",
            },
        }

        templates = framework_templates.get(framework, framework_templates["base"])
        return templates.get(file_type, "python/base/unit")

    async def generate_test_for_file(
        self,
        file_path: str | Path,
        llm_client: Any,
        service_name: str | None = None,
        target_coverage: int = 85,
    ) -> dict[str, Any]:
        """
        Сгенерировать тесты для одного файла

        Args:
            file_path: Путь к файлу кода
            llm_client: Клиент LLM для выполнения запросов
            service_name: Название сервиса (если не указан, будет определено автоматически)
            target_coverage: Целевое покрытие процентами

        Returns:
            Словарь с результатами генерации
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        # Определить сервис
        if service_name is None:
            service_name = self._detect_service(file_path)

        # Определить фреймворк и тип файла
        framework = self._detect_framework(file_path)
        file_type = self._detect_file_type(file_path, framework)

        # Получить код файла
        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise IOError(f"Ошибка при чтении файла {file_path}: {e}")

        # 🚀 УМНАЯ ГЕНЕРАЦИЯ: Анализ бизнес-логики
        business_logic_analysis = None
        if HAS_ANALYZER:
            try:
                analyzer = BusinessLogicAnalyzer(code)
                business_logic_analysis = analyzer.analyze()
                logger.info(
                    "Business logic analysis completed",
                    functions=len(business_logic_analysis.get("functions", [])),
                    classes=len(business_logic_analysis.get("classes", [])),
                    models=len(business_logic_analysis.get("models", [])),
                )
            except Exception as e:
                logger.warning(f"Business logic analysis failed: {e}")

        # Определить путь к шаблону
        template_path = self._get_template_path(framework, file_type)
        logger.info(
            f"Generating tests for {file_path}",
            service=service_name,
            framework=framework,
            file_type=file_type,
            template=template_path,
        )

        # Создать контекст
        context = {
            "repo_path": str(self.project_path),
            "service_name": service_name,
            "python_version": "3.12",
            "framework": framework,
            "current_coverage": "45",
            "coverage_target": str(target_coverage),
            "file_path": str(file_path),
            "file_type": file_type,
            "code": code,
        }

        # 🚀 Добавить анализ бизнес-логики в контекст для LLM
        if business_logic_analysis:
            context["business_logic"] = json.dumps(
                business_logic_analysis,
                ensure_ascii=False,
                indent=2,
            )

        # Выполнить стратегию через LLM
        result = await self.prompt_engine.execute_strategy(
            strategy=template_path,
            context=context,
            timeout=120,  # 2 минуты на генерацию
        )

        return {
            "success": result["success"],
            "output": result.get("output", ""),
            "template_used": template_path,
            "framework": framework,
            "file_type": file_type,
            "file_path": str(file_path),
            "execution_time": result["execution_time"],
            "prompt_length": result.get("prompt_length", 0),
            "response_length": len(result.get("output", "")),
        }

    def _detect_service(self, file_path: Path) -> str:
        """
        Определить название сервиса по пути файла

        Args:
            file_path: Путь к файлу

        Returns:
            Название сервиса
        """
        # Пытаемся найти в apps/
        try:
            relative_path = file_path.relative_to(self.project_path / "apps")
            parts = relative_path.parts
            if len(parts) > 0:
                return parts[0]
        except ValueError:
            pass

        # По умолчанию - последний элемент пути
        return file_path.parent.name

    async def generate_tests_for_directory(
        self,
        directory: str | Path,
        llm_client: Any,
        target_coverage: int = 85,
        file_patterns: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Сгенерировать тесты для всех файлов в директории

        Args:
            directory: Путь к директории
            llm_client: Клиент LLM
            target_coverage: Целевое покрытие
            file_patterns: Паттерны файлов для генерации (по умолчанию *.py)

        Returns:
            Список результатов генерации для каждого файла
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Директория не найдена: {directory}")

        if file_patterns is None:
            file_patterns = ["*.py", "**/*.py"]

        # Найти все файлы
        files_to_test = []
        for pattern in file_patterns:
            files_to_test.extend(directory.glob(pattern))

        # Удалить дубликаты и файлы из venv
        files_to_test = [
            f for f in files_to_test
            if f.is_file()
            and "venv" not in str(f)
            and "__pycache__" not in str(f)
            and "test_" not in f.name.lower()
            and "_test" not in f.name.lower()
        ]

        results = []

        for file_path in files_to_test:
            try:
                result = await self.generate_test_for_file(
                    file_path=file_path,
                    llm_client=llm_client,
                    target_coverage=target_coverage,
                )
                results.append(result)
                logger.info(f"Generated tests for {file_path}", success=result["success"])
            except Exception as e:
                logger.error(f"Failed to generate tests for {file_path}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "file_path": str(file_path),
                })

        return results

    def apply_generated_tests(
        self,
        test_code: str,
        output_file: str | Path,
        mode: str = "append",
    ) -> None:
        """
        Применить сгенерированные тесты к файлу

        Args:
            test_code: Сгенерированный код тестов
            output_file: Путь к файлу для записи тестов
            mode: Режим записи ("append" или "overwrite")
        """
        output_file = Path(output_file)

        # Убедиться, что директория существует
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Определить режим записи
        if mode == "overwrite" or not output_file.exists():
            mode = "w"
        else:
            mode = "a"

        # Записать код
        with open(output_file, mode, encoding="utf-8") as f:
            # Если добавляем, добавляем пустую строку перед кодом
            if mode == "a":
                f.write("\n\n")
            f.write(test_code)

        logger.info(f"Applied generated tests to {output_file}", mode=mode)
