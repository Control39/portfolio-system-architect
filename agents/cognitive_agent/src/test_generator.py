"""
TestGenerator для Cognitive Agent
Генерирует тесты на основе профилей сервисов и промпт-шаблонов.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.cognitive_agent.src.code_analyzer import CodeAnalyzer
from agents.cognitive_agent.src.service_registry import ServiceProfile, ServiceRegistry

# Импорт AI провайдера
try:
    from apps.ai_provider_manager.src.ai_provider_manager import (
        chat_with_fallback,
        get_provider_manager,
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("AI Provider not available, using stub mode")

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).parent.parent.parent


class TestGenerator:
    """
    Генератор тестов для когнитивного агента.

    Стратегия работы:
    1. Определить профиль сервиса по пути файла
    2. Прочитать код файла
    3. Выбрать промпт-шаблон на основе технологии
    4. Вызвать AI для генерации тестов
    5. Вернуть результат с инструкциями по применению
    """

    def __init__(
        self,
        project_path: str,
        service_registry: ServiceRegistry | None = None,
        config_path: str = None
    ):
        self.project_path = Path(project_path)
        self.config_path = Path(config_path) if config_path else None
        self.prompts_dir = REPO_ROOT / "prompts"

        # Инициализация ServiceRegistry
        if service_registry:
            self.service_registry = service_registry
        else:
            config_file = self.project_path / "agents" / "cognitive_agent" / "config" / "service-profiles.yaml"
            self.service_registry = ServiceRegistry(
                repo_root=str(self.project_path),
                config_path=str(config_file) if config_file.exists() else None
            )

        # Инициализация CodeAnalyzer
        self.code_analyzer = CodeAnalyzer(str(self.project_path))

        logger.info(f"✅ TestGenerator initialized for {self.project_path}")
        logger.info(f"📁 Found {len(self.service_registry.profiles)} services")

    def analyze_and_generate(self, file_path: str) -> dict[str, Any]:
        """
        Проанализировать код и сгенерировать тесты.

        Args:
            file_path: Путь к файлу, для которого нужно сгенерировать тесты

        Returns:
            Словарь с результатами генерации
        """
        file_path = Path(file_path)

        # 1. Определить профиль сервиса
        service_profile = self.service_registry.get_profile_by_path(str(file_path))

        if not service_profile:
            logger.warning(f"⚠️ File outside known services: {file_path}")
            return {
                "status": "skipped",
                "message": f"File outside known services: {file_path}",
                "reasoning": "Could not determine service profile"
            }

        logger.info(f"📋 Service profile found: {service_profile.name} (criticality: {service_profile.criticality})")

        # 2. Прочитать код файла
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read file: {e}",
                "reasoning": str(e)
            }

        # 3. Выполнить анализ кода через CodeAnalyzer
        analysis_results = self.code_analyzer.run_full_analysis()

        # 4. Выбрать промпт-шаблон
        prompt_template = self._select_prompt_template(
            service_profile=service_profile,
            file_path=file_path
        )

        # 5. Сформировать контекст для AI
        context = {
            "file_path": str(file_path.relative_to(self.project_path)),
            "service_name": service_profile.name,
            "framework": service_profile.framework,
            "coverage_target": service_profile.coverage_target,
            "code": code,
            "analysis_results": analysis_results
        }

        # 6. Вызвать AI для генерации тестов
        generated_tests = self._call_ai_for_generation(prompt_template, context)

        # 7. Вернуть результат
        return {
            "status": "success",
            "service_name": service_profile.name,
            "service_profile": {
                "name": service_profile.name,
                "path": service_profile.path,
                "criticality": service_profile.criticality,
                "framework": service_profile.framework,
                "coverage_target": service_profile.coverage_target
            },
            "file_path": str(file_path),
            "generated_tests": generated_tests,
            "reasoning": f"Generated tests for {service_profile.name} ({service_profile.criticality} criticality)",
            "timestamp": datetime.now().isoformat()
        }

    def _select_prompt_template(self, service_profile: ServiceProfile, file_path: Path) -> str:
        """
        Выбрать промпт-шаблон на основе технологии и типа теста.

        Args:
            service_profile: Профиль сервиса
            file_path: Путь к файлу

        Returns:
            Путь к файлу шаблона
        """
        # Структура: prompts/{language}/{framework}/{test_type}.md
        prompts_path = self.prompts_dir / service_profile.language / service_profile.framework

        if not prompts_path.exists():
            logger.warning(f"⚠️ Prompts directory not found: {prompts_path}")
            # Использовать дефолтный шаблон
            prompts_path = self.prompts_dir / service_profile.language / "base"

        # Определить тип теста по содержимому файла
        test_type = self._determine_test_type(file_path, service_profile.framework)

        template_path = prompts_path / f"{test_type}.md"

        if not template_path.exists():
            logger.warning(f"⚠️ Template not found: {template_path}, using base template")
            template_path = self.prompts_dir / service_profile.language / "base" / f"{test_type}.md"

        if not template_path.exists():
            # Если и дефолтного шаблона нет, вернуть базовый
            return "# Base prompt template for {file_path} in {service_name}"

        # Прочитать шаблон
        return template_path.read_text(encoding='utf-8')

    def _determine_test_type(self, file_path: Path, framework: str) -> str:
        """
        Определить тип теста на основе имени файла.

        Args:
            file_path: Путь к файлу
            framework: Фреймворк

        Returns:
            Тип теста: 'unit', 'integration', 'e2e', 'api'
        """
        filename = file_path.name.lower()

        if 'test' in filename or filename.startswith('test_'):
            # Это уже тест-файл
            return 'unit'

        # Определить по названию файла
        if filename.endswith('_test.py'):
            return 'unit'
        elif 'integration' in filename:
            return 'integration'
        elif 'e2e' in filename or 'scenario' in filename:
            return 'e2e'
        elif 'api' in filename or 'endpoint' in filename:
            return 'api'
        else:
            # По умолчанию юнит-тесты
            return 'unit'

    def _call_ai_for_generation(self, prompt_template: str, context: dict[str, Any]) -> str:
        """
        Вызвать AI для генерации тестов.

        Args:
            prompt_template: Шаблон промпта
            context: Контекст для подстановки

        Returns:
            Сгенерированные тесты или сообщение об ошибке
        """
        # Подставить контекст в шаблон
        prompt = prompt_template.format(**context)

        # Вызвать AI
        if AI_AVAILABLE:
            try:
                # Получить провайдер AI
                ai_manager = get_provider_manager()

                # Сформировать сообщение
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                # Вызвать AI
                response = chat_with_fallback(
                    messages=messages,
                    provider=ai_manager.primary_provider
                )

                return response.get("content", "# Tests generation failed")

            except Exception as e:
                logger.error(f"❌ AI generation failed: {e}")
                return f"# AI generation failed: {e}"
        else:
            # Stub режим - вернуть заглушку
            logger.warning("⚠️ AI not available, returning stub tests")
            return f"""
# Stub tests for {context.get('file_path', 'unknown_file')}
# Generated by TestGenerator (stub mode)

import pytest


def test_example():
    \"\"\"Example test stub.\"\"\"
    assert True
"""

    def generate_for_service(self, service_name: str) -> dict[str, Any]:
        """
        Сгенерировать тесты для всего сервиса.

        Args:
            service_name: Имя сервиса

        Returns:
            Результат генерации
        """
        profile = self.service_registry.get_profile(service_name)

        if not profile:
            return {
                "status": "error",
                "message": f"Service not found: {service_name}"
            }

        # Сканировать все Python файлы в сервисе
        service_path = Path(profile.path)
        py_files = list(service_path.rglob('*.py'))

        results = []

        for py_file in py_files:
            result = self.analyze_and_generate(str(py_file))
            results.append(result)

        return {
            "status": "success",
            "service_name": service_name,
            "files_processed": len(results),
            "results": results
        }
