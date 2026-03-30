"""
Основное приложение Portfolio Organizer.
Объединяет все API модули.
"""

import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from api.reasoning_api import app as reasoning_app
from api.ml_model_registry_integration import bp as ml_model_registry_bp

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise ValueError('SECRET_KEY environment variable not set!')
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

@app.route('/')
def index():
    return {
        'service': 'Portfolio Organizer',
        'version': '0.1.0',
        'endpoints': {
            '/api/ml-model-registry/*': 'ML Model Registry integration',
            '/api/projects': 'Projects API (see reasoning_api)',
            '/api/portfolio/analysis': 'Portfolio analysis (see reasoning_api)',
        }
    }

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8004))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')
