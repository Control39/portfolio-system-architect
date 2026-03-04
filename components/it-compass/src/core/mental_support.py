"""
Модуль психологической поддержки для IT Compass.

Этот модуль предоставляет функции для отслеживания психологического состояния
пользователя и предоставления рекомендаций по поддержанию ментального здоровья
в процессе профессионального развития.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import os


class MoodLevel(Enum):
    """Уровни настроения"""
    VERY_SAD = 1      # Очень грустно
    SAD = 2           # Грустно
    NEUTRAL = 3       # Нейтрально
    HAPPY = 4         # Счастливо
    VERY_HAPPY = 5    # Очень счастливо


class StressLevel(Enum):
    """Уровни стресса"""
    VERY_LOW = 1      # Очень низкий
    LOW = 2           # Низкий
    MEDIUM = 3        # Средний
    HIGH = 4          # Высокий
    VERY_HIGH = 5     # Очень высокий


class EnergyLevel(Enum):
    """Уровни энергии"""
    VERY_LOW = 1      # Очень низкий
    LOW = 2           # Низкий
    MEDIUM = 4        # Средний
    HIGH = 6          # Высокий
    VERY_HIGH = 8     # Очень высокий


class SatisfactionLevel(Enum):
    """Уровни удовлетворенности"""
    VERY_DISSATISFIED = 1   # Очень неудовлетворен
    DISSATISFIED = 2        # Неудовлетворен
    NEUTRAL = 3             # Нейтрально
    SATISFIED = 4           # Удовлетворен
    VERY_SATISFIED = 5      # Очень удовлетворен


@dataclass
class MoodRecord:
    """
    Запись психологического состояния пользователя.
    """
    user_id: str              # Идентификатор пользователя
    timestamp: str           # Время записи (ISO формат)
    mood_level: MoodLevel   # Уровень настроения
    stress_level: StressLevel  # Уровень стресса
    energy_level: EnergyLevel  # Уровень энергии
    satisfaction_level: SatisfactionLevel  # Уровень удовлетворенности
    notes: str = ""          # Дополнительные заметки
    activities: List[str] = None  # Активности, которые повлияли на состояние


@dataclass
class SupportRecommendation:
    """
    Рекомендация по психологической поддержке.
    """
    id: str                   # Уникальный идентификатор
    user_id: str              # Идентификатор пользователя
    title: str               # Заголовок рекомендации
    description: str         # Описание рекомендации
    type: str                # Тип рекомендации ("practice", "resource", "activity")
    priority: int             # Приоритет (1-5)
    resources: List[str] = None  # Ссылки на ресурсы
    estimated_duration: int = 0  # Оценка времени в минутах
    created_at: str = ""     # Дата создания (ISO формат)


class MentalSupport:
    """
    Основной класс для психологической поддержки пользователя.
    
    Предоставляет функциональность для:
    - Отслеживания психологического состояния
    - Генерации рекомендаций по поддержке
    - Предоставления практик самопомощи
    """
    
    def __init__(self, user_id: str, data_dir: str = "./support/data"):
        """
        Инициализация системы психологической поддержки.
        
        Args:
            user_id (str): Идентификатор пользователя
            data_dir (str): Директория для хранения данных (по умолчанию "./support/data")
        """
        self.user_id = user_id
        self.data_dir = data_dir
        self.mood_records_file = os.path.join(data_dir, f"{user_id}_mood_records.json")
        self.recommendations_file = os.path.join(data_dir, f"{user_id}_recommendations.json")
        
        # Создание директории для данных, если она не существует
        os.makedirs(data_dir, exist_ok=True)
        
        # Загрузка данных
        self.mood_records = self._load_mood_records()
        self.recommendations = self._load_recommendations()
        
        # Инициализация практик самопомощи
        self.self_help_practices = SelfHelpPractices()
    
    def _load_mood_records(self) -> List[MoodRecord]:
        """
        Загрузка записей психологического состояния из файла.
        
        Returns:
            List[MoodRecord]: Список записей психологического состояния
        """
        if not os.path.exists(self.mood_records_file):
            return []
        
        try:
            with open(self.mood_records_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = []
            for record_data in data:
                # Преобразование строковых значений в Enum
                record_data['mood_level'] = MoodLevel(record_data['mood_level'])
                record_data['stress_level'] = StressLevel(record_data['stress_level'])
                record_data['energy_level'] = EnergyLevel(record_data['energy_level'])
                record_data['satisfaction_level'] = SatisfactionLevel(record_data['satisfaction_level'])
                
                record = MoodRecord(**record_data)
                records.append(record)
            
            return records
        except Exception as e:
            print(f"Ошибка при загрузке записей состояния: {e}")
            return []
    
    def _save_mood_records(self) -> None:
        """
        Сохранение записей психологического состояния в файл.
        """
        try:
            # Преобразование записей в словари для сериализации
            records_data = []
            for record in self.mood_records:
                record_dict = asdict(record)
                # Преобразование Enum в значения
                record_dict['mood_level'] = record.mood_level.value
                record_dict['stress_level'] = record.stress_level.value
                record_dict['energy_level'] = record.energy_level.value
                record_dict['satisfaction_level'] = record.satisfaction_level.value
                records_data.append(record_dict)
            
            with open(self.mood_records_file, 'w', encoding='utf-8') as f:
                json.dump(records_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении записей состояния: {e}")
    
    def _load_recommendations(self) -> List[SupportRecommendation]:
        """
        Загрузка рекомендаций по психологической поддержке из файла.
        
        Returns:
            List[SupportRecommendation]: Список рекомендаций
        """
        if not os.path.exists(self.recommendations_file):
            return []
        
        try:
            with open(self.recommendations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            recommendations = []
            for rec_data in data:
                rec = SupportRecommendation(**rec_data)
                recommendations.append(rec)
            
            return recommendations
        except Exception as e:
            print(f"Ошибка при загрузке рекомендаций: {e}")
            return []
    
    def _save_recommendations(self) -> None:
        """
        Сохранение рекомендаций по психологической поддержке в файл.
        """
        try:
            # Преобразование рекомендаций в словари для сериализации
            recs_data = [asdict(rec) for rec in self.recommendations]
            
            with open(self.recommendations_file, 'w', encoding='utf-8') as f:
                json.dump(recs_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении рекомендаций: {e}")
    
    def record_mood(self, mood_record: MoodRecord) -> None:
        """
        Запись психологического состояния пользователя.
        
        Args:
            mood_record (MoodRecord): Запись психологического состояния
        """
        self.mood_records.append(mood_record)
        self._save_mood_records()
    
    def get_recent_mood(self, days: int = 7) -> List[MoodRecord]:
        """
        Получение недавних записей психологического состояния.
        
        Args:
            days (int): Количество дней для анализа (по умолчанию 7)
            
        Returns:
            List[MoodRecord]: Список недавних записей состояния
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = []
        
        for record in self.mood_records:
            record_date = datetime.fromisoformat(record.timestamp)
            if record_date >= cutoff_date:
                recent_records.append(record)
        
        # Сортировка по дате
        recent_records.sort(key=lambda x: x.timestamp, reverse=True)
        
        return recent_records
    
    def get_current_recommendations(self) -> List[SupportRecommendation]:
        """
        Получение текущих рекомендаций по психологической поддержке.
        
        Returns:
            List[SupportRecommendation]: Список текущих рекомендаций
        """
        # Фильтрация непросроченных рекомендаций
        current_date = datetime.now()
        current_recommendations = []
        
        for rec in self.recommendations:
            created_date = datetime.fromisoformat(rec.created_at)
            # Рекомендации действительны 7 дней
            if current_date - created_date <= timedelta(days=7):
                current_recommendations.append(rec)
        
        return current_recommendations
    
    def generate_recommendations(self) -> List[SupportRecommendation]:
        """
        Генерация рекомендаций по психологической поддержке.
        
        Returns:
            List[SupportRecommendation]: Список сгенерированных рекомендаций
        """
        recommendations = []
        
        # Анализ последних записей состояния
        recent_records = self.get_recent_mood(7)
        if not recent_records:
            return recommendations
        
        # Определение трендов
        avg_mood = sum(record.mood_level.value for record in recent_records) / len(recent_records)
        avg_stress = sum(record.stress_level.value for record in recent_records) / len(recent_records)
        avg_energy = sum(record.energy_level.value for record in recent_records) / len(recent_records)
        
        # Генерация рекомендаций на основе трендов
        if avg_mood < 3:
            # Низкое настроение
            rec = SupportRecommendation(
                id=f"rec_{self.user_id}_mood_{int(datetime.now().timestamp())}",
                user_id=self.user_id,
                title="Поддержите свое настроение",
                description="Вы отметили низкое настроение в последние дни. Попробуйте практики повышения настроения.",
                type="practice",
                priority=5,
                resources=["https://example.com/mood-boosting-practices"],
                estimated_duration=15
            )
            recommendations.append(rec)
        
        if avg_stress > 3:
            # Высокий уровень стресса
            rec = SupportRecommendation(
                id=f"rec_{self.user_id}_stress_{int(datetime.now().timestamp())}",
                user_id=self.user_id,
                title="Снизьте уровень стресса",
                description="Ваши записи показывают высокий уровень стресса. Попробуйте техники релаксации.",
                type="practice",
                priority=5,
                resources=["https://example.com/stress-relief-techniques"],
                estimated_duration=20
            )
            recommendations.append(rec)
        
        if avg_energy < 4:
            # Низкий уровень энергии
            rec = SupportRecommendation(
                id=f"rec_{self.user_id}_energy_{int(datetime.now().timestamp())}",
                user_id=self.user_id,
                title="Повысьте уровень энергии",
                description="Ваши записи показывают низкий уровень энергии. Попробуйте практики повышения энергии.",
                type="activity",
                priority=4,
                resources=["https://example.com/energy-boosting-activities"],
                estimated_duration=30
            )
            recommendations.append(rec)
        
        # Добавление рекомендаций на основе практик самопомощи
        practices = self.self_help_practices.get_relevant_practices(
            avg_mood, avg_stress, avg_energy
        )
        
        for practice in practices:
            rec = SupportRecommendation(
                id=f"rec_{self.user_id}_practice_{int(datetime.now().timestamp())}_{practice['id']}",
                user_id=self.user_id,
                title=practice["title"],
                description=practice["description"],
                type="practice",
                priority=3,
                resources=practice["resources"],
                estimated_duration=practice["duration"]
            )
            recommendations.append(rec)
        
        # Сохранение рекомендаций
        self.recommendations.extend(recommendations)
        self._save_recommendations()
        
        return recommendations
    
    def get_mood_summary(self) -> Dict[str, Any]:
        """
        Получение сводки по психологическому состоянию пользователя.
        
        Returns:
            Dict[str, Any]: Сводка по психологическому состоянию
        """
        recent_records = self.get_recent_mood(30)  # Анализ за последние 30 дней
        
        if not recent_records:
            return {}
        
        # Подсчет средних значений
        total_mood = sum(record.mood_level.value for record in recent_records)
        total_stress = sum(record.stress_level.value for record in recent_records)
        total_energy = sum(record.energy_level.value for record in recent_records)
        total_satisfaction = sum(record.satisfaction_level.value for record in recent_records)
        
        avg_mood = total_mood / len(recent_records)
        avg_stress = total_stress / len(recent_records)
        avg_energy = total_energy / len(recent_records)
        avg_satisfaction = total_satisfaction / len(recent_records)
        
        # Определение трендов
        first_half = recent_records[len(recent_records)//2:]
        second_half = recent_records[:len(recent_records)//2]
        
        if first_half and second_half:
            first_avg_mood = sum(record.mood_level.value for record in first_half) / len(first_half)
            second_avg_mood = sum(record.mood_level.value for record in second_half) / len(second_half)
            
            if second_avg_mood > first_avg_mood:
                mood_trend = "improving"
            elif second_avg_mood < first_avg_mood:
                mood_trend = "declining"
            else:
                mood_trend = "stable"
        else:
            mood_trend = "unknown"
        
        return {
            "average_mood": round(avg_mood, 2),
            "average_stress": round(avg_stress, 2),
            "average_energy": round(avg_energy, 2),
            "average_satisfaction": round(avg_satisfaction, 2),
            "total_records": len(recent_records),
            "mood_trend": mood_trend,
            "last_record_date": recent_records[0].timestamp if recent_records else None
        }


class SelfHelpPractices:
    """
    Класс для предоставления практик самопомощи.
    """
    
    def __init__(self):
        """
        Инициализация практик самопомощи.
        """
        self.practices = self._load_practices()
    
    def _load_practices(self) -> List[Dict[str, Any]]:
        """
        Загрузка практик самопомощи.
        
        Returns:
            List[Dict[str, Any]]: Список практик самопомощи
        """
        # В реальной реализации эти данные могут загружаться из файла или API
        return [
            {
                "id": "breathing_1",
                "title": "Дыхательная практика для расслабления",
                "description": "Практика глубокого дыхания для снижения стресса и тревожности.",
                "category": "breathing",
                "resources": ["https://example.com/breathing-exercise-1"],
                "duration": 10,
                "suitable_for": {
                    "low_mood": True,
                    "high_stress": True,
                    "low_energy": True
                }
            },
            {
                "id": "mindfulness_1",
                "title": "Медитация осознанности",
                "description": "Практика осознанности для развития концентрации и спокойствия.",
                "category": "mindfulness",
                "resources": ["https://example.com/mindfulness-meditation"],
                "duration": 15,
                "suitable_for": {
                    "low_mood": True,
                    "high_stress": True,
                    "low_energy": False
                }
            },
            {
                "id": "gratitude_1",
                "title": "Практика благодарности",
                "description": "Ежедневная практика выражения благодарности для развития позитивного мышления.",
                "category": "gratitude",
                "resources": ["https://example.com/gratitude-practice"],
                "duration": 5,
                "suitable_for": {
                    "low_mood": True,
                    "high_stress": True,
                    "low_energy": True
                }
            },
            {
                "id": "physical_1",
                "title": "Физическая активность",
                "description": "Легкая физическая активность для повышения уровня энергии и настроения.",
                "category": "physical",
                "resources": ["https://example.com/light-exercise"],
                "duration": 20,
                "suitable_for": {
                    "low_mood": True,
                    "high_stress": True,
                    "low_energy": False
                }
            },
            {
                "id": "journaling_1",
                "title": "Ведение дневника",
                "description": "Письменное выражение мыслей и чувств для лучшего понимания себя.",
                "category": "journaling",
                "resources": ["https://example.com/journaling-tips"],
                "duration": 15,
                "suitable_for": {
                    "low_mood": True,
                    "high_stress": True,
                    "low_energy": True
                }
            }
        ]
    
    def get_relevant_practices(self, avg_mood: float, avg_stress: float, avg_energy: float) -> List[Dict[str, Any]]:
        """
        Получение релевантных практик на основе текущего состояния.
        
        Args:
            avg_mood (float): Средний уровень настроения
            avg_stress (float): Средний уровень стресса
            avg_energy (float): Средний уровень энергии
            
        Returns:
            List[Dict[str, Any]]: Список релевантных практик
        """
        relevant_practices = []
        
        for practice in self.practices:
            suitable = practice["suitable_for"]
            
            # Проверка соответствия практики текущему состоянию
            if (avg_mood < 3 and suitable["low_mood"]) or \
               (avg_stress > 3 and suitable["high_stress"]) or \
               (avg_energy < 4 and suitable["low_energy"]):
                relevant_practices.append(practice)
        
        # Ограничение количества практик
        return relevant_practices[:3]


class ITCompassMentalSupport:
    """
    Интеграция психологической поддержки с IT Compass.
    
    Обеспечивает связь между системой отслеживания компетенций и психологической поддержкой.
    """
    
    def __init__(self, user_id: str, it_compass_data_dir: str = "./data"):
        """
        Инициализация интеграции.
        
        Args:
            user_id (str): Идентификатор пользователя
            it_compass_data_dir (str): Директория данных IT Compass
        """
        self.user_id = user_id
        self.it_compass_data_dir = it_compass_data_dir
        self.mental_support = MentalSupport(user_id, "./support/data")
    
    def get_integrated_recommendations(self) -> List[SupportRecommendation]:
        """
        Получение интегрированных рекомендаций.
        
        Returns:
            List[SupportRecommendation]: Список интегрированных рекомендаций
        """
        # Получение рекомендаций от системы психологической поддержки
        mental_recommendations = self.mental_support.generate_recommendations()
        
        # В реальной реализации здесь можно добавить
        # рекомендации на основе данных IT Compass
        # Например, если пользователь долго не занимался обучением,
        # можно предложить мотивационные практики
        
        return mental_recommendations
    
    def record_learning_related_mood(self, mood_record: MoodRecord, learning_context: str = "") -> None:
        """
        Запись психологического состояния, связанного с обучением.
        
        Args:
            mood_record (MoodRecord): Запись психологического состояния
            learning_context (str): Контекст обучения
        """
        # Добавление контекста обучения в заметки
        if learning_context:
            mood_record.notes = f"{mood_record.notes} [Контекст обучения: {learning_context}]"
        
        self.mental_support.record_mood(mood_record)


# Пример использования
if __name__ == "__main__":
    # Создание системы психологической поддержки
    support = MentalSupport("user_001")
    
    # Запись психологического состояния
    mood_record = MoodRecord(
        user_id="user_001",
        timestamp=datetime.now().isoformat(),
        mood_level=MoodLevel.NEUTRAL,
        stress_level=StressLevel.MEDIUM,
        energy_level=EnergyLevel.MEDIUM,
        satisfaction_level=SatisfactionLevel.NEUTRAL,
        notes="Обычный день, немного устал от программирования",
        activities=["coding", "meeting"]
    )
    
    support.record_mood(mood_record)
    
    # Генерация рекомендаций
    recommendations = support.generate_recommendations()
    print(f"Сгенерировано {len(recommendations)} рекомендаций")
    
    # Получение сводки
    summary = support.get_mood_summary()
    print(f"Сводка по состоянию: {summary}")