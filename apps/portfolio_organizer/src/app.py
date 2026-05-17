"""
Основное приложение Portfolio Organizer.
Объединяет все API модули.
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Интеграция с AI Config Manager
try:
    from apps.portfolio_organizer.src.config_integration import get_config
    AI_CONFIG_AVAILABLE = True
    config_manager = get_config()
    po_config = config_manager.get_config()
    print("✅ Portfolio Organizer: использован AI Config Manager")
except Exception as e:
    AI_CONFIG_AVAILABLE = False
    print(f"⚠️  Portfolio Organizer: AI Config Manager недоступен ({e}), используется локальный конфиг")
    po_config = {}

from flask import Flask
from flask_wtf import CSRFProtect

from .api.ml_model_registry_integration import bp as ml_model_registry_bp


app = Flask(__name__)

# Конфигурация из AI Config Manager или fallback
if po_config:
    app.secret_key = po_config.get('flask', {}).get('secret_key', os.environ.get("SECRET_KEY", "dev-secret-key"))
    app.config['WTF_CSRF_ENABLED'] = po_config.get('flask', {}).get('csrf_enabled', True)
else:
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config['WTF_CSRF_ENABLED'] = True

csrf = CSRFProtect(app)

# Регистрируем blueprint для интеграции с ML Model Registry
app.register_blueprint(ml_model_registry_bp)

# Копируем маршруты из reasoning_api
# Поскольку reasoning_api определяет маршруты напрямую на объекте app,
# мы не можем просто импортировать его. Вместо этого мы можем создать
# отдельный blueprint для reasoning_api или изменить его структуру.
# Для простоты временно оставим reasoning_api как отдельное приложение,
# но в будущем стоит рефакторить.

# Для текущей задачи мы запустим reasoning_api отдельно.
# Этот файл app.py будет использоваться для интеграции с ML Model Registry.


@app.route("/")
def index():
    return {
        "service": "Portfolio Organizer",
        "version": "0.1.0",
        "endpoints": {
            "/api/ml-model-registry/*": "ML Model Registry integration",
            "/api/projects": "Projects API (see reasoning_api)",
            "/api/portfolio/analysis": "Portfolio analysis (see reasoning_api)",
        },
    }


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8004))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true",
    )
