from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///career_dev.db')
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Для хранения хэшированного пароля
    password_hash = db.Column(db.String(255), nullable=False)
    # Для хранения соли
    password_salt = db.Column(db.String(255), nullable=False)
    skills = db.relationship('Skill', backref='user', lazy=True)
    
    def set_password(self, password):
        """Установить пароль пользователя"""
        self.password_salt = secrets.token_hex(16)
        self.password_hash = hashlib.sha256((password + self.password_salt).encode()).hexdigest()
    
    def check_password(self, password):
        """Проверить пароль пользователя"""
        password_hash = hashlib.sha256((password + self.password_salt).encode()).hexdigest()
        return password_hash == self.password_hash

# Модель навыка
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Маркер компетенции
class CompetencyMarker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    required_level = db.Column(db.Integer, default=1)

# Модель прогресса
class ProgressRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    from_level = db.Column(db.Integer)
    to_level = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Связи
    user = db.relationship('User', backref='progress_records')
    skill = db.relationship('Skill', backref='progress_records')

@app.route('/api/users', methods=['GET'])
def get_users():
    """Получить список всех пользователей"""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email
    } for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Получить пользователя по ID"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    """Создать нового пользователя"""
    data = request.get_json()
    
    # Валидация данных
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email and password are required'}), 400
    
    # Проверка уникальности
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Создание пользователя с хэшированным паролем
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """Обновить пользователя"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        # Проверка уникальности username
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'email' in data:
        # Проверка уникальности email
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    """Удалить пользователя"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/api/users/<int:user_id>/skills', methods=['GET'])
@require_auth
def get_user_skills(user_id):
    """Получить навыки пользователя"""
    user = User.query.get_or_404(user_id)
    return jsonify([{
        'id': skill.id,
        'name': skill.name,
        'level': skill.level
    } for skill in user.skills])

@app.route('/api/users/<int:user_id>/skills/<int:skill_id>', methods=['GET'])
@require_auth
def get_user_skill(user_id, skill_id):
    """Получить конкретный навык пользователя"""
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first_or_404()
    return jsonify({
        'id': skill.id,
        'name': skill.name,
        'level': skill.level
    })

@app.route('/api/users/<int:user_id>/skills', methods=['POST'])
@require_auth
def add_user_skill(user_id):
    """Добавить навык пользователю"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Валидация данных
    if not data.get('name'):
        return jsonify({'error': 'Skill name is required'}), 400
    
    # Проверка существования навыка
    existing_skill = Skill.query.filter_by(name=data['name'], user_id=user_id).first()
    if existing_skill:
        return jsonify({'error': 'Skill already exists for this user'}), 400
    
    skill = Skill(name=data['name'], level=data.get('level', 1), user_id=user.id)
    db.session.add(skill)
    db.session.commit()
    return jsonify({'id': skill.id, 'name': skill.name, 'level': skill.level}), 201

@app.route('/api/users/<int:user_id>/skills/<int:skill_id>', methods=['PUT'])
@require_auth
def update_user_skill(user_id, skill_id):
    """Обновить навык пользователя"""
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    # Сохраняем предыдущий уровень для записи в историю
    from_level = skill.level
    
    if 'name' in data:
        # Проверка существования навыка с таким именем
        existing_skill = Skill.query.filter(Skill.name == data['name'],
                                          Skill.user_id == user_id,
                                          Skill.id != skill_id).first()
        if existing_skill:
            return jsonify({'error': 'Skill with this name already exists for this user'}), 400
        skill.name = data['name']
    
    if 'level' in data:
        new_level = data['level']
        if not isinstance(new_level, int) or new_level < 1 or new_level > 5:
            return jsonify({'error': 'Level must be an integer between 1 and 5'}), 400
        skill.level = new_level
        
        # Записываем изменение в историю прогресса
        progress_record = ProgressRecord(
            user_id=user_id,
            skill_id=skill_id,
            from_level=from_level,
            to_level=new_level
        )
        db.session.add(progress_record)
    
    db.session.commit()
    return jsonify({'id': skill.id, 'name': skill.name, 'level': skill.level})

@app.route('/api/users/<int:user_id>/skills/<int:skill_id>', methods=['DELETE'])
@require_auth
def delete_user_skill(user_id, skill_id):
    """Удалить навык пользователя"""
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    return jsonify({'message': 'Skill deleted successfully'})

@app.route('/api/markers', methods=['GET'])
@require_auth
def get_competency_markers():
    """Получить все маркеры компетенций"""
    markers = CompetencyMarker.query.all()
    return jsonify([{
        'id': marker.id,
        'title': marker.title,
        'description': marker.description,
        'required_level': marker.required_level
    } for marker in markers])

@app.route('/api/markers/<int:marker_id>', methods=['GET'])
@require_auth
def get_competency_marker(marker_id):
    """Получить маркер компетенции по ID"""
    marker = CompetencyMarker.query.get_or_404(marker_id)
    return jsonify({
        'id': marker.id,
        'title': marker.title,
        'description': marker.description,
        'required_level': marker.required_level
    })

@app.route('/api/markers', methods=['POST'])
@require_auth
def create_competency_marker():
    """Создать маркер компетенции"""
    data = request.get_json()
    
    # Валидация данных
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    marker = CompetencyMarker(
        title=data['title'],
        description=data.get('description', ''),
        required_level=data.get('required_level', 1)
    )
    db.session.add(marker)
    db.session.commit()
    return jsonify({
        'id': marker.id,
        'title': marker.title,
        'description': marker.description,
        'required_level': marker.required_level
    }), 201

@app.route('/api/markers/<int:marker_id>', methods=['PUT'])
@require_auth
def update_competency_marker(marker_id):
    """Обновить маркер компетенции"""
    marker = CompetencyMarker.query.get_or_404(marker_id)
    data = request.get_json()
    
    if 'title' in data:
        marker.title = data['title']
    if 'description' in data:
        marker.description = data['description']
    if 'required_level' in data:
        marker.required_level = data['required_level']
    
    db.session.commit()
    return jsonify({
        'id': marker.id,
        'title': marker.title,
        'description': marker.description,
        'required_level': marker.required_level
    })

@app.route('/api/markers/<int:marker_id>', methods=['DELETE'])
@require_auth
def delete_competency_marker(marker_id):
    """Удалить маркер компетенции"""
    marker = CompetencyMarker.query.get_or_404(marker_id)
    db.session.delete(marker)
    db.session.commit()
    return jsonify({'message': 'Marker deleted successfully'})

@app.route('/api/users/<int:user_id>/progress', methods=['GET'])
@require_auth
def get_user_progress(user_id):
    """Получить историю прогресса пользователя"""
    user = User.query.get_or_404(user_id)
    progress_records = ProgressRecord.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': record.id,
        'skill_id': record.skill_id,
        'skill_name': record.skill.name,
        'from_level': record.from_level,
        'to_level': record.to_level,
        'timestamp': record.timestamp.isoformat()
    } for record in progress_records])

# Эндпоинт для аутентификации
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Вход пользователя в систему"""
    data = request.get_json()
    
    # Валидация данных
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Поиск пользователя
    user = User.query.filter_by(username=data['username']).first()
    
    # Проверка существования пользователя и правильности пароля
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Создание сессии
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Выход пользователя из системы"""
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Проверка статуса аутентификации"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
    
    return jsonify({'authenticated': False})

# Декоратор для проверки аутентификации
def require_auth(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    
    return decorated_function

# Применяем декоратор к существующим эндпоинтам
@app.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    """Получить список всех пользователей"""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email
    } for user in users])

# Защита существующих эндпоинтов с помощью декоратора
# Пример для одного эндпоинта:
# @app.route('/api/protected_endpoint', methods=['GET'])
# @require_auth
# def protected_endpoint():
#     return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    # Для сессий необходимо установить секретный ключ
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    with app.app_context():
        db.create_all()
    app.run(debug=True)