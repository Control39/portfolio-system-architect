class CompetencyTracker:
    """Класс для отслеживания компетенций и карьерного развития"""
    
    def __init__(self):
        self.users = {}
        self.competency_markers = {}
    
    def add_user(self, user_id, username, email):
        """Добавить пользователя в систему"""
        self.users[user_id] = {
            'username': username,
            'email': email,
            'skills': {},
            'progress_history': []
        }
    
    def add_skill(self, user_id, skill_name, level=1):
        """Добавить навык пользователю"""
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        
        self.users[user_id]['skills'][skill_name] = level
    
    def add_competency_marker(self, marker_id, title, description="", required_level=1):
        """Добавить маркер компетенции"""
        self.competency_markers[marker_id] = {
            'title': title,
            'description': description,
            'required_level': required_level
        }
    
    def update_skill_level(self, user_id, skill_name, new_level):
        """Обновить уровень навыка пользователя"""
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        
        if skill_name not in self.users[user_id]['skills']:
            raise ValueError("Навык не найден у пользователя")
        
        old_level = self.users[user_id]['skills'][skill_name]
        
        # Записываем изменение в историю прогресса
        self.users[user_id]['progress_history'].append({
            'skill': skill_name,
            'from_level': old_level,
            'to_level': new_level,
            'date': self._get_current_date()
        })
        
        # Обновляем уровень навыка
        self.users[user_id]['skills'][skill_name] = new_level
    
    def get_user_skills(self, user_id):
        """Получить навыки пользователя"""
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        
        return self.users[user_id]['skills']
    
    def get_user_progress(self, user_id):
        """Получить историю прогресса пользователя"""
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        
        return self.users[user_id]['progress_history']
    
    def check_competency_achievement(self, user_id):
        """Проверить достижение маркеров компетенций пользователем"""
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        
        achieved_markers = []
        user_skills = self.users[user_id]['skills']
        
        for marker_id, marker in self.competency_markers.items():
            # Проверяем, есть ли у пользователя навык, соответствующий маркеру
            # В реальной системе здесь будет более сложная логика сопоставления
            for skill_name, skill_level in user_skills.items():
                if marker['required_level'] <= skill_level:
                    achieved_markers.append({
                        'marker_id': marker_id,
                        'marker_title': marker['title'],
                        'achieved_skill': skill_name,
                        'skill_level': skill_level
                    })
                    break
        
        return achieved_markers
    
    def generate_progress_report(self, user_id):
        """Сгенерировать отчет о прогрессе пользователя"""
        if user_id not in self.users:
            raise ValueError("Пользователь не найден")
        
        user = self.users[user_id]
        skills = user['skills']
        progress_history = user['progress_history']
        achieved_markers = self.check_competency_achievement(user_id)
        
        report = {
            'user': {
                'id': user_id,
                'username': user['username'],
                'email': user['email']
            },
            'current_skills': skills,
            'total_skills': len(skills),
            'progress_history': progress_history,
            'achieved_markers': achieved_markers,
            'next_milestones': self._calculate_next_milestones(user_id)
        }
        
        return report
    
    def _calculate_next_milestones(self, user_id):
        """Рассчитать следующие вехи для пользователя"""
        # Упрощенная реализация
        # В реальной системе здесь будет более сложная логика
        return [
            {"title": "Повышение уровня основного навыка", "target_date": "2026-06-01"},
            {"title": "Достижение нового маркера компетенции", "target_date": "2026-09-01"}
        ]
    
    def _get_current_date(self):
        """Получить текущую дату (в реальной системе будет использовать datetime)"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d")