# components/cognitive-agent/config/loader.py
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Приоритет: AI Config Manager → локальный конфиг
try:
    from apps.cognitive_agent.src.config_integration import get_config

    AI_CONFIG_AVAILABLE = True
    _config_instance = get_config()
    COMPONENT_CONFIG = _config_instance.get_config()
    print("✅ Cognitive Agent: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Cognitive Agent: AI Config Manager недоступен ({e}), используется локальный конфиг")

    # Fallback на локальный конфиг
    import yaml

    config_path = REPO_ROOT / "apps" / "cognitive_agent" / "configs" / "api-gateway.yaml"

    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            COMPONENT_CONFIG = yaml.safe_load(f) or {}
    else:
        COMPONENT_CONFIG = {}
