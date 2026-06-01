#!/usr/bin/env python3
"""
Автоматическая интеграция AI Config Manager со всеми сервисами
"""

from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

# Список всех сервисов
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

# Шаблон модуля интеграции
INTEGRATION_TEMPLATE = '''"""
Интеграция с AI Config Manager для {service_name}
Обеспечивает централизованное управление конфигурациями
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from apps.ai_config_manager.src.config_manager import ConfigManager
    AI_CONFIG_AVAILABLE = True
except ImportError:
    AI_CONFIG_AVAILABLE = False
    print("⚠️  AI Config Manager не доступен, используется локальная конфигурация")


class {service_class}Config:
    """Обёртка для конфигурации {service_name} через AI Config Manager"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация конфигурации

        Args:
            config_path: Путь к файлу конфигурации (по умолчанию: config/ai-config.yaml)
        """
        self.config_path = config_path or str(REPO_ROOT / "config" / "ai-config.yaml")
        self._config_manager: Optional[ConfigManager] = None
        self._local_config: Optional[Dict[str, Any]] = None

        if AI_CONFIG_AVAILABLE:
            self._init_config_manager()
        else:
            self._load_local_config()

    def _init_config_manager(self) -> None:
        """Инициализация ConfigManager"""
        try:
            self._config_manager = ConfigManager(config_path=self.config_path)
            if not self._config_manager.validate():
                print(f"⚠️  Конфигурация не валидна, используется fallback")
                self._load_local_config()
        except Exception as e:
            print(f"⚠️  Ошибка инициализации ConfigManager: {{e}}")
            self._load_local_config()

    def _load_local_config(self) -> None:
        """Загрузка локальной конфигурации (fallback)"""
        import yaml
        local_config_path = REPO_ROOT / "apps" / "{service_folder}" / "config" / "{config_file}"

        if local_config_path.exists():
            with open(local_config_path, 'r', encoding='utf-8') as f:
                self._local_config = yaml.safe_load(f)
        else:
            self._local_config = {{}}

    def get_config(self) -> Dict[str, Any]:
        """Получить полную конфигурацию"""
        if self._config_manager:
            try:
                return self._config_manager.get_agent_config("{service_key}")
            except Exception:
                return self._local_config or {{}}
        return self._local_config or {{}}

    def reload(self) -> None:
        """Перезагрузить конфигурацию (hot reload)"""
        if self._config_manager:
            self._config_manager.reload()
        else:
            self._load_local_config()

    def is_available(self) -> bool:
        """Проверить доступность AI Config Manager"""
        return AI_CONFIG_AVAILABLE and self._config_manager is not None


# Singleton для удобства
_config_instance: Optional[{service_class}Config] = None

def get_config() -> {service_class}Config:
    """Получить глобальный экземпляр конфигурации"""
    global _config_instance
    if _config_instance is None:
        _config_instance = {service_class}Config()
    return _config_instance


def reload_config() -> None:
    """Перезагрузить глобальную конфигурацию"""
    global _config_instance
    if _config_instance:
        _config_instance.reload()
'''


def create_integration_file(service: str) -> bool:
    """Создать файл интеграции для сервиса"""
    # Определяем параметры сервиса
    service_folder = service
    service_key = service.replace("-", "_")
    service_class = service.replace("-", "_").title().replace("_", "")

    # Ищем конфигурационный файл
    config_dir = REPO_ROOT / "apps" / service / "config"
    configs_dir = REPO_ROOT / "apps" / service / "configs"

    config_file = "config.yaml"
    if config_dir.exists():
        existing_configs = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))
        if existing_configs:
            config_file = existing_configs[0].name
    elif configs_dir.exists():
        existing_configs = list(configs_dir.glob("*.yaml")) + list(configs_dir.glob("*.yml"))
        if existing_configs:
            config_file = existing_configs[0].name

    # Создаём модуль интеграции
    src_dir = REPO_ROOT / "apps" / service / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    integration_file = src_dir / "config_integration.py"

    content = INTEGRATION_TEMPLATE.format(
        service_name=service.replace("_", " ").title(),
        service_class=service_class,
        service_folder=service_folder,
        service_key=service_key,
        config_file=config_file,
    )

    with open(integration_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Создан {integration_file.relative_to(REPO_ROOT)}")
    return True


def main():
    """Основная функция"""
    print("=" * 60)
    print("Автоматическая интеграция AI Config Manager")
    print("=" * 60)

    success_count = 0
    failed_services: list[str] = []

    for service in SERVICES:
        try:
            if create_integration_file(service):
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