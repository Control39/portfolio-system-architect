#!/usr/bin/env python3
"""
Автоматическое создание тестов для интеграции AI Config Manager
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

SERVICES = [
    "ai_config_manager",
    "auth_service",
    "career_development",
    "cognitive_agent",
    "decision_engine",
    "infra_orchestrator",
    "it_compass",
    "job_automation_agent",
    "knowledge_graph",
    "mcp_server",
    "ml_model_registry",
    "portfolio_organizer",
    "system_proof",
    "thought_architecture",
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
        from config_integration import {service_class}Config
        assert {service_class}Config is not None

    def test_get_config_singleton(self):
        """Проверка singleton паттерна"""
        from config_integration import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_get_config_returns_dict(self):
        """Проверка что get_config возвращает dict"""
        from config_integration import get_config

        config = get_config()
        result = config.get_config()

        assert isinstance(result, dict)

    def test_reload_config(self):
        """Проверка hot reload"""
        from config_integration import reload_config

        # Не должно выбрасывать исключений
        reload_config()

    def test_is_available_method(self):
        """Проверка метода is_available"""
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

    # Проверка существования директории сервиса
    service_path = REPO_ROOT / "apps" / service_folder
    if not service_path.exists():
        print(f"⚠️  Сервис {service_folder} не существует, пропускаем")
        return False

    # Проверка наличия src/config_integration.py
    integration_file = service_path / "src" / "config_integration.py"
    if not integration_file.exists():
        print(f"⚠️  {service_folder}: нет config_integration.py, создаём заглушку")
        # Создаём базовый модуль интеграции
        src_dir = service_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        stub_content = f'''"""
Модуль интеграции с AI Config Manager для {service_folder}
"""

from typing import Dict, Optional
from pathlib import Path

# Попытка импорта AI Config Manager
try:
    from apps.ai_config_manager.src.config_manager import ConfigManager
    AI_CONFIG_AVAILABLE = True
except ImportError:
    AI_CONFIG_AVAILABLE = False
    ConfigManager = None


class {service_class}Config:
    """Конфигурация {service_folder}"""

    def __init__(self):
        self.config_manager = ConfigManager() if AI_CONFIG_AVAILABLE else None
        self._config: Optional[Dict] = None

    def get_config(self) -> Dict:
        """Получить конфигурацию"""
        if self._config is None and self.config_manager:
            self._config = self.config_manager.get_service_config("{service_folder}")
        return self._config or {{}}  # Экранирование фигурных скобок для f-string

    def is_available(self) -> bool:
        """Проверка доступности конфигурации"""
        return self._config is not None


# Singleton instance
_instance: Optional["{service_class}Config"] = None


def get_config() -> "{service_class}Config":
    """Получить singleton инстанс конфигурации"""
    global _instance
    if _instance is None:
        _instance = {service_class}Config()
    return _instance


def reload_config() -> None:
    """Перезагрузить конфигурацию (hot reload)"""
    global _instance
    if _instance:
        _instance._config = None
'''

        with open(integration_file, "w", encoding="utf-8") as f:
            f.write(stub_content)
        print(f"✅ Создан заглушка: {integration_file.relative_to(REPO_ROOT)}")

    # Создаём директорию для тестов
    tests_dir = REPO_ROOT / "apps" / service / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    test_file = tests_dir / "test_config_integration.py"

    content = TEST_TEMPLATE.format(
        service_name=service.replace("_", " ").title(),
        service_class=service_class,
        service_folder=service_folder,
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
