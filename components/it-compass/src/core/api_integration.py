"""
Модуль отслеживания профессиональных компетенций в IT.

Этот модуль предоставляет основные классы и функции для отслеживания
профессиональных компетенций, генерации рекомендаций и анализа прогресса.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class CompetencyLevel(Enum):
    """Уровни компетентности"""
    BEGINNER = 1      # Начальный уровень
    INTERMEDIATE = 2   # Промежуточный уровень
    ADVANCED = 3      # Продвинутый уровень
    EXPERT = 4        # Экспертный уровень
    MASTER = 5        # Мастерский уровень


class ConfidenceLevel(Enum):
    """Уровни уверенности"""
    VERY_LOW = 1      # Очень низкая
    LOW = 2           # Низкая
    MEDIUM = 3        # Средняя
    HIGH = 4          # Высокая
    VERY_HIGH = 5     # Очень высокая


@dataclass
class TechnologyMarker:
    """
    Маркер технологии или компетенции.
    
    Представляет конкретную технологию или компетенцию, которую необходимо отслеживать.
    """
    id: str                    # Уникальный идентификатор
    name: str                  # Название технологии
    category: str              # Категория (например, "Frontend", "Backend", "DevOps")
    description: str          # Описание технологии
    learning_resources: List[str]  # Рекомендуемые ресурсы для изучения
    created_at: str          # Дата создания (ISO формат)
    
    def __post_init__(self):
        """Пост-инициализация объекта"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class UserProgress:
    """
    Прогресс пользователя по конкретной технологии.
    
    Отслеживает уровень компетенции и уверенности пользователя по конкретной технологии.
    """
    user_id: str              # Идентификатор пользователя
    marker_id: str            # Идентификатор маркера технологии
    competency_level: CompetencyLevel  # Уровень компетенции
    confidence_level: ConfidenceLevel  # Уровень уверенности
    experience_hours: int     # Количество часов опыта
    last_updated: str        # Дата последнего обновления (ISO формат)
    notes: str = ""           # Дополнительные заметки
    
    def __post_init__(self):
        """Пост-инициализация объекта"""
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


@dataclass
class Recommendation:
    """
    Рекомендация по развитию.
    
    Представляет рекомендацию по дальнейшему развитию компетенции.
    """
    id: str                   # Уникальный идентификатор
    user_id: str              # Идентификатор пользователя
    marker_id: str            # Идентификатор маркера технологии
    title: str                # Заголовок рекомендации
    description: str         # Описание рекомендации
    priority: int             # Приоритет (1-5)
    type: str                # Тип рекомендации ("course", "project", "practice", "article")
    resources: List[str]      # Ссылки на ресурсы
    created_at: str          # Дата создания (ISO формат)
    
    def __post_init__(self):
        """Пост-инициализация объекта"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class LearningPath:
    """
    Путь обучения.
    
    Представляет последовательность шагов для освоения технологии или компетенции.
    """
    id: str                   # Уникальный идентификатор
    user_id: str              # Идентификатор пользователя
    marker_id: str            # Идентификатор маркера технологии
    title: str                # Название пути обучения
    description: str         # Описание пути обучения
    steps: List[Dict[str, Any]]  # Шаги пути обучения (название, описание, статус)
    estimated_hours: int      # Оценка времени в часах
    created_at: str          # Дата создания (ISO формат)
    
    def __post_init__(self):
        """Пост-инициализация объекта"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class CompetencyTracker:
    """
    Основной класс для отслеживания профессиональных компетенций.
    
    Предоставляет функциональность для:
    - Управления маркерами технологий
    - Отслеживания прогресса пользователя
    - Генерации рекомендаций
    - Создания путей обучения
    """
    
    def __init__(self, user_id: str, data_dir: str = "./data"):
        """
        Инициализация трекера компетенций.
        
        Args:
            user_id (str): Идентификатор пользователя
            data_dir (str): Директория для хранения данных (по умолчанию "./data")
        """
        self.user_id = user_id
        self.data_dir = data_dir
        self.markers_file = os.path.join(data_dir, "markers.json")
        self.progress_file = os.path.join(data_dir, "user_progress.json")
        
        # Создание директории для данных, если она не существует
        os.makedirs(data_dir, exist_ok=True)
        
        # Загрузка данных
        self.markers = self._load_markers()
        self.progress = self._load_progress()
    
    def _load_markers(self) -> Dict[str, TechnologyMarker]:
        """
        Загрузка маркеров технологий из файла.
        
        Returns:
            Dict[str, TechnologyMarker]: Словарь маркеров технологий
        """
        if not os.path.exists(self.markers_file):
            return {}
        
        try:
            with open(self.markers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            markers = {}
            for marker_data in data:
                marker = TechnologyMarker(**marker_data)
                markers[marker.id] = marker
            
            return markers
        except Exception as e:
            print(f"Ошибка при загрузке маркеров: {e}")
            return {}
    
    def _save_markers(self) -> None:
        """
        Сохранение маркеров технологий в файл.
        """
        try:
            # Преобразование маркеров в словари для сериализации
            markers_data = [asdict(marker) for marker in self.markers.values()]
            
            with open(self.markers_file, 'w', encoding='utf-8') as f:
                json.dump(markers_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении маркеров: {e}")
    
    def _load_progress(self) -> Dict[str, UserProgress]:
        """
        Загрузка прогресса пользователя из файла.
        
        Returns:
            Dict[str, UserProgress]: Словарь прогресса пользователя
        """
        if not os.path.exists(self.progress_file):
            return {}
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            progress = {}
            for progress_data in data:
                # Преобразование строковых значений в Enum
                progress_data['competency_level'] = CompetencyLevel(
                    progress_data['competency_level']
                )
                progress_data['confidence_level'] = ConfidenceLevel(
                    progress_data['confidence_level']
                )
                
                progress_item = UserProgress(**progress_data)
                progress[progress_item.marker_id] = progress_item
            
            return progress
        except Exception as e:
            print(f"Ошибка при загрузке прогресса: {e}")
            return {}
    
    def _save_progress(self) -> None:
        """
        Сохранение прогресса пользователя в файл.
        """
        try:
            # Преобразование прогресса в словари для сериализации
            progress_data = []
            for progress_item in self.progress.values():
                item_dict = asdict(progress_item)
                # Преобразование Enum в значения
                item_dict['competency_level'] = progress_item.competency_level.value
                item_dict['confidence_level'] = progress_item.confidence_level.value
                progress_data.append(item_dict)
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении прогресса: {e}")
    
    def add_marker(self, marker: TechnologyMarker) -> None:
        """
        Добавление маркера технологии.
        
        Args:
            marker (TechnologyMarker): Маркер технологии для добавления
        """
        self.markers[marker.id] = marker
        self._save_markers()
    
    def get_marker(self, marker_id: str) -> Optional[TechnologyMarker]:
        """
        Получение маркера технологии по идентификатору.
        
        Args:
            marker_id (str): Идентификатор маркера
            
        Returns:
            Optional[TechnologyMarker]: Маркер технологии или None, если не найден
        """
        return self.markers.get(marker_id)
    
    def list_markers(self) -> List[TechnologyMarker]:
        """
        Получение списка всех маркеров технологий.
        
        Returns:
            List[TechnologyMarker]: Список маркеров технологий
        """
        return list(self.markers.values())
    
    def record_progress(self, progress: UserProgress) -> None:
        """
        Запись прогресса пользователя.
        
        Args:
            progress (UserProgress): Прогресс пользователя для записи
        """
        self.progress[progress.marker_id] = progress
        self._save_progress()
    
    def get_progress(self, marker_id: str) -> Optional[UserProgress]:
        """
        Получение прогресса пользователя по идентификатору маркера.
        
        Args:
            marker_id (str): Идентификатор маркера
            
        Returns:
            Optional[UserProgress]: Прогресс пользователя или None, если не найден
        """
        return self.progress.get(marker_id)
    
    def get_all_progress(self) -> List[UserProgress]:
        """
        Получение всего прогресса пользователя.
        
        Returns:
            List[UserProgress]: Список всего прогресса пользователя
        """
        return list(self.progress.values())
    
    def generate_recommendations(self) -> List[Recommendation]:
        """
        Генерация рекомендаций по развитию.
        
        Returns:
            List[Recommendation]: Список рекомендаций
        """
        recommendations = []
        
        # Для каждого маркера генерируем рекомендации
        for marker in self.markers.values():
            progress = self.progress.get(marker.id)
            
            # Если нет прогресса, рекомендуем начать изучение
            if not progress:
                rec = Recommendation(
                    id=f"rec_{marker.id}_start",
                    user_id=self.user_id,
                    marker_id=marker.id,
                    title=f"Начните изучать {marker.name}",
                    description=f"Начните изучение технологии {marker.name} с основ.",
                    priority=3,
                    type="course",
                    resources=marker.learning_resources,
                )
                recommendations.append(rec)
                continue
            
            # Если уровень компетенции низкий, рекомендуем практику
            if progress.competency_level in [CompetencyLevel.BEGINNER, CompetencyLevel.INTERMEDIATE]:
                rec = Recommendation(
                    id=f"rec_{marker.id}_practice",
                    user_id=self.user_id,
                    marker_id=marker.id,
                    title=f"Практикуйтесь в {marker.name}",
                    description=f"Улучшите свои навыки в {marker.name} через практику.",
                    priority=4,
                    type="project",
                    resources=marker.learning_resources,
                )
                recommendations.append(rec)
            
            # Если уровень уверенности низкий, рекомендуем поддержку
            if progress.confidence_level in [ConfidenceLevel.VERY_LOW, ConfidenceLevel.LOW]:
                rec = Recommendation(
                    id=f"rec_{marker.id}_support",
                    user_id=self.user_id,
                    marker_id=marker.id,
                    title=f"Поддержите уверенность в {marker.name}",
                    description=f"Работайте над уверенностью в {marker.name} через поддержку.",
                    priority=5,
                    type="practice",
                    resources=["https://example.com/confidence-building"],
                )
                recommendations.append(rec)
        
        return recommendations
    
    def generate_learning_path(self, marker_id: str) -> Optional[LearningPath]:
        """
        Генерация пути обучения для конкретной технологии.
        
        Args:
            marker_id (str): Идентификатор маркера технологии
            
        Returns:
            Optional[LearningPath]: Путь обучения или None, если маркер не найден
        """
        marker = self.markers.get(marker_id)
        if not marker:
            return None
        
        # Определяем шаги пути обучения на основе категории
        steps = []
        estimated_hours = 0
        
        if marker.category == "Frontend":
            steps = [
                {
                    "title": "Основы HTML/CSS",
                    "description": "Изучите основы HTML и CSS для создания веб-страниц",
                    "status": "pending"
                },
                {
                    "title": "JavaScript основы",
                    "description": "Изучите основы JavaScript для интерактивности",
                    "status": "pending"
                },
                {
                    "title": "Современные фреймворки",
                    "description": "Изучите популярные фреймворки (React, Vue, Angular)",
                    "status": "pending"
                }
            ]
            estimated_hours = 120
        elif marker.category == "Backend":
            steps = [
                {
                    "title": "Основы программирования",
                    "description": "Изучите основы программирования на выбранном языке",
                    "status": "pending"
                },
                {
                    "title": "Работа с базами данных",
                    "description": "Изучите работу с реляционными и нереляционными БД",
                    "status": "pending"
                },
                {
                    "title": "API разработка",
                    "description": "Изучите разработку RESTful и GraphQL API",
                    "status": "pending"
                }
            ]
            estimated_hours = 150
        else:
            steps = [
                {
                    "title": "Основы",
                    "description": "Изучите основы данной технологии",
                    "status": "pending"
                },
                {
                    "title": "Практика",
                    "description": "Примените знания на практике",
                    "status": "pending"
                },
                {
                    "title": "Продвинутые темы",
                    "description": "Изучите продвинутые аспекты технологии",
                    "status": "pending"
                }
            ]
            estimated_hours = 100
        
        path = LearningPath(
            id=f"path_{marker_id}",
            user_id=self.user_id,
            marker_id=marker_id,
            title=f"Путь обучения {marker.name}",
            description=f"Путь обучения для освоения технологии {marker.name}",
            steps=steps,
            estimated_hours=estimated_hours,
        )
        
        return path
    
    def get_competency_summary(self) -> Dict[str, Any]:
        """
        Получение сводки по компетенциям пользователя.
        
        Returns:
            Dict[str, Any]: Сводка по компетенциям
        """
        total_markers = len(self.markers)
        completed_markers = len(self.progress)
        
        # Подсчет уровней компетенций
        competency_counts = {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0,
            "expert": 0,
            "master": 0
        }
        
        # Подсчет уровней уверенности
        confidence_counts = {
            "very_low": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "very_high": 0
        }
        
        total_experience = 0
        
        for progress in self.progress.values():
            # Подсчет уровней компетенций
            if progress.competency_level == CompetencyLevel.BEGINNER:
                competency_counts["beginner"] += 1
            elif progress.competency_level == CompetencyLevel.INTERMEDIATE:
                competency_counts["intermediate"] += 1
            elif progress.competency_level == CompetencyLevel.ADVANCED:
                competency_counts["advanced"] += 1
            elif progress.competency_level == CompetencyLevel.EXPERT:
                competency_counts["expert"] += 1
            elif progress.competency_level == CompetencyLevel.MASTER:
                competency_counts["master"] += 1
            
            # Подсчет уровней уверенности
            if progress.confidence_level == ConfidenceLevel.VERY_LOW:
                confidence_counts["very_low"] += 1
            elif progress.confidence_level == ConfidenceLevel.LOW:
                confidence_counts["low"] += 1
            elif progress.confidence_level == ConfidenceLevel.MEDIUM:
                confidence_counts["medium"] += 1
            elif progress.confidence_level == ConfidenceLevel.HIGH:
                confidence_counts["high"] += 1
            elif progress.confidence_level == ConfidenceLevel.VERY_HIGH:
                confidence_counts["very_high"] += 1
            
            # Подсчет общего опыта
            total_experience += progress.experience_hours
        
        return {
            "total_markers": total_markers,
            "completed_markers": completed_markers,
            "competency_levels": competency_counts,
            "confidence_levels": confidence_counts,
            "total_experience_hours": total_experience,
            "completion_rate": completed_markers / total_markers if total_markers > 0 else 0
        }


# Пример использования
if __name__ == "__main__":
    # Создание трекера
    tracker = CompetencyTracker("user_001")
    
    # Добавление маркеров технологий
    python_marker = TechnologyMarker(
        id="python",
        name="Python",
        category="Backend",
        description="Универсальный язык программирования",
        learning_resources=["https://docs.python.org/"],
    )
    
    tracker.add_marker(python_marker)
    
    # Запись прогресса
    progress = UserProgress(
        user_id="user_001",
        marker_id="python",
        competency_level=CompetencyLevel.INTERMEDIATE,
        confidence_level=ConfidenceLevel.MEDIUM,
        experience_hours=50,
    )
    
    tracker.record_progress(progress)
    
    # Генерация рекомендаций
    recommendations = tracker.generate_recommendations()
    print(f"Сгенерировано {len(recommendations)} рекомендаций")
    
    # Получение сводки
    summary = tracker.get_competency_summary()
    print(f"Сводка: {summary}")