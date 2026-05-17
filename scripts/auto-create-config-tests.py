#!/usr/bin/env python3
"""
Автоматическое создание тестов для интеграции AI Config Manager
"""

from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

SERVICES = [
    "ai-config-manager",
    "auth_service",
    "career_development",
    "cognitive-agent",
    "decision_engine",
    "infra-orchestrator",
    "it_compass",
    "job-automation-agent",
    "knowledge_graph",
    "mcp_server",
    "ml_model_registry",
    "portfolio_organizer",
    "system_proof",
    "thought-architecture",
]

TEST_TEMPLATE = '''"""
Тесты интеграции с AI Config Manager для {service_name}
"""

import pytest
from pathlib import Path
import sys

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class Test{service_class}ConfigIntegration:
    """Тесты интеграции конфигурации {service_name}"""

    def test_config_manager_available(self):
        """Проверка доступности AI Config Manager"""
        try:
            from apps.ai_config_manager.src.config_manager import ConfigManager
            assert ConfigManager is not None
        except ImportError:
            pytest.skip("AI Config Manager не доступен")

    def test_config_integration_module(self):
        """Проверка импорта модуля интеграции"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "{service_folder}" / "src"))
        from config_integration import {service_class}Config
        assert {service_class}Config is not None

    def test_get_config_singleton(self):
        """Проверка singleton паттерна"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "{service_folder}" / "src"))
        from config_integration import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_get_config_returns_dict(self):
        """Проверка что get_config возвращает dict"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "{service_folder}" / "src"))
        from config_integration import get_config

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)

    def test_reload_config(self):
        """Проверка hot reload"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "{service_folder}" / "src"))
        from config_integration import reload_config

        # Не должно выбрасывать исключений
        reload_config()

    def test_is_available_method(self):
        """Проверка метода is_available"""
        sys.path.insert(0, str(REPO_ROOT / "apps" / "{service_folder}" / "src"))
        from config_integration import get_config

        config = get_config()
        assert hasattr(config, 'is_available')
        assert callable(config.is_available)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


def create_test_file(service: str) -> bool:
    """Создать тестовый файл для сервиса"""
    service_folder = service
    service_class = service.replace("-", "_").title().replace("_", "")

    tests_dir = REPO_ROOT / "apps" / service / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    test_file = tests_dir / "test_config_integration.py"

    content = TEST_TEMPLATE.format(
        service_name=service.replace("_", " ").title(), service_class=service_class, service_folder=service_folder
    )

    with open(test_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Создан {test_file.relative_to(REPO_ROOT)}")
    return True


def main():
    """Основная функция"""
    print("=" * 60)
    print("Создание тестов для интеграции AI Config Manager")
    print("=" * 60)

    success_count = 0
    failed_services: list[str] = []

    for service in SERVICES:
        try:
            if create_test_file(service):
                success_count += 1
        except Exception as e:
            print(f"❌ Ошибка для {service}: {e}")
            failed_services.append(service)

    print("=" * 60)
    print(f"✅ Успешно: {success_count}/{len(SERVICES)}")

    if failed_services:
        print(f"❌ Ошибки: {', '.join(failed_services)}")

    print("=" * 60)


if __name__ == "__main__":
    main()
