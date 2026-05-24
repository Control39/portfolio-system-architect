# components/cloud-reason/config/utils.py
from .loader import COMPONENT_CONFIG


def get_module_path(module_name):
    """Возвращает путь к модулю по его имени."""
    for module in COMPONENT_CONFIG["modules"]:
        if module["name"] == module_name:
            return module["path"]
    raise ValueError(f"Модуль {module_name} не найден в конфигурации")


def find_endpoint_by_path(path):
    """Находит эндпоинт по пути."""
    for endpoint in COMPONENT_CONFIG["endpoints"]:
        if endpoint["path"] == path:
            return endpoint
    return None


def get_env_variables():
    """Возвращает список переменных окружения из конфигурации."""
    return COMPONENT_CONFIG.get("env_variables", [])


def get_automation_script(script_name):
    """Возвращает команду автоматизации по имени."""
    for script in COMPONENT_CONFIG["automation"]["scripts"]:
        if script["name"] == script_name:
            return script["command"]
    return None
