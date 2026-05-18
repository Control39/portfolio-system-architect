# Проверка импорта всех 5 завершённых сервисов
import importlib.util
import sys
from pathlib import Path


# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))

services = [
    "system_proof",
    "knowledge_graph",
    "thought-architecture",
    "infra-orchestrator",
    "ai-config-manager",
]

print("Проверка импорта сервисов...\n")

for name in services:
    try:
        # Путь к main.py сервиса
        main_path = REPO_ROOT / "apps" / name / "main.py"
        if not main_path.exists():
            print(f"✗ {name} — main.py не найден")
            continue

        # Динамический импорт
        spec = importlib.util.spec_from_file_location(f"apps.{name}.main", main_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "app"):
            print(f"✓ {name} OK")
        else:
            print(f"✗ {name} — нет app в модуле")
    except Exception as e:
        print(f"✗ {name} — {type(e).__name__}: {e}")

print("\nПроверка завершена!")
