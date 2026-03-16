# Интеграция с системой рассуждений (Cloud Reason)
# -*- coding: utf-8 -*-

"""
Скрипт интеграции IT Compass с системой рассуждений Cloud Reason.

Этот скрипт обеспечивает:
1. Интеграцию данных о навыках и прогрессе с системой рассуждений
2. Генерацию сложных рекомендаций на основе анализа рассуждений
3. Обратную связь между системами для улучшения персонализации
4. Синхронизацию моделей пользователя в обеих системах
"""

import json
import requests
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================
# Модели данных
# ======================

@dataclass
class ReasoningRequest:
    """Запрос к системе рассуждений"""
    user_id: str
    context: Dict[str, Any]
    query: str
    session_id: str
    timestamp: datetime.datetime


@dataclass
class ReasoningResponse:
    """Ответ от системы рассуждений"""
    response: str
    confidence: float
    reasoning_chain: List[str]
    metadata: Dict[str, Any]
    generated_at: datetime.datetime


@dataclass
class SkillAnalysis:
    """Анализ навыка для рассуждений"""
    skill_id: str
    skill_name: str
    current_level: str
    progress_trend: str
    estimated_completion: Optional[str]
    related_skills: List[str]
    learning_efficiency: float


@dataclass
class UserContext:
    """Контекст пользователя для рассуждений"""
    user_id: str
    current_skills: List[SkillAnalysis]
    recent_activity: List[Dict[str, Any]]
    mood_state: Dict[str, Any]
    goals: List[Dict[str, Any]]
    preferences: Dict[str, Any]


# ======================
# Основной класс интеграции
# ======================

class ReasoningIntegration:
    """Класс интеграции с системой рассуждений"""
    
    def __init__(self, reasoning_api_url: str, api_key: Optional[str] = None):
        self.reasoning_api_url = reasoning_api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Установка заголовков
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ITCompass-Reasoning-Integration/1.0'
        })
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        
        logger.info(f"Инициализирована интеграция с системой рассуждений по адресу: {reasoning_api_url}")
    
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Выполнить запрос к API рассуждений"""
        url = f"{self.reasoning_api_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к системе рассуждений: {e}")
            raise
    
    def analyze_user_context(self, user_context: UserContext) -> ReasoningResponse:
        """
        Анализ контекста пользователя с помощью системы рассуждений
        
        Args:
            user_context: Контекст пользователя
            
        Returns:
            ReasoningResponse: Ответ от системы рассуждений
        """
        logger.info(f"Анализ контекста пользователя: {user_context.user_id}")
        
        request_data = {
            "user_id": user_context.user_id,
            "context": asdict(user_context),
            "query": "Проанализируй контекст пользователя и предоставь рекомендации по развитию",
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        response_data = self._make_request("/analyze/context", request_data)
        
        return ReasoningResponse(
            response=response_data.get("response", ""),
            confidence=response_data.get("confidence", 0.0),
            reasoning_chain=response_data.get("reasoning_chain", []),
            metadata=response_data.get("metadata", {}),
            generated_at=datetime.datetime.now()
        )
    
    def generate_skill_recommendations(self, user_context: UserContext) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций по навыкам на основе рассуждений
        
        Args:
            user_context: Контекст пользователя
            
        Returns:
            List[Dict]: Список рекомендаций
        """
        logger.info(f"Генерация рекомендаций для пользователя: {user_context.user_id}")
        
        request_data = {
            "user_id": user_context.user_id,
            "context": asdict(user_context),
            "query": "Сгенерируй персонализированные рекомендации по развитию навыков",
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        response_data = self._make_request("/recommendations/skills", request_data)
        return response_data.get("recommendations", [])
    
    def predict_learning_outcomes(self, user_context: UserContext, 
                                target_skills: List[str]) -> Dict[str, Any]:
        """
        Предсказание результатов обучения
        
        Args:
            user_context: Контекст пользователя
            target_skills: Целевые навыки
            
        Returns:
            Dict: Предсказания результатов обучения
        """
        logger.info(f"Предсказание результатов обучения для пользователя: {user_context.user_id}")
        
        request_data = {
            "user_id": user_context.user_id,
            "context": asdict(user_context),
            "target_skills": target_skills,
            "query": "Предскажи результаты обучения для указанных навыков",
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        response_data = self._make_request("/predict/learning", request_data)
        return response_data
    
    def optimize_learning_path(self, user_context: UserContext, 
                             target_skills: List[str]) -> List[Dict[str, Any]]:
        """
        Оптимизация пути обучения
        
        Args:
            user_context: Контекст пользователя
            target_skills: Целевые навыки
            
        Returns:
            List[Dict]: Оптимизированный путь обучения
        """
        logger.info(f"Оптимизация пути обучения для пользователя: {user_context.user_id}")
        
        request_data = {
            "user_id": user_context.user_id,
            "context": asdict(user_context),
            "target_skills": target_skills,
            "query": "Оптимизируй путь обучения для достижения целевых навыков",
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        response_data = self._make_request("/optimize/path", request_data)
        return response_data.get("optimized_path", [])
    
    def analyze_mood_impact(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Анализ влияния настроения на обучение
        
        Args:
            user_context: Контекст пользователя
            
        Returns:
            Dict: Анализ влияния настроения
        """
        logger.info(f"Анализ влияния настроения для пользователя: {user_context.user_id}")
        
        request_data = {
            "user_id": user_context.user_id,
            "context": asdict(user_context),
            "query": "Проанализируй влияние текущего состояния пользователя на эффективность обучения",
            "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        response_data = self._make_request("/analyze/mood", request_data)
        return response_data


# ======================
# Интеграция с IT Compass
# ======================

class ITCompassIntegration:
    """Интеграция с IT Compass"""
    
    def __init__(self, compass_data_path: str, reasoning_url: str, api_key: Optional[str] = None):
        self.compass_data_path = Path(compass_data_path)
        self.reasoning_integration = ReasoningIntegration(reasoning_url, api_key)
        logger.info("Инициализирована интеграция IT Compass с системой рассуждений")
    
    def load_compass_data(self, user_id: str) -> Dict[str, Any]:
        """
        Загрузка данных пользователя из IT Compass
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Данные пользователя
        """
        user_file = self.compass_data_path / f"user_{user_id}.json"
        if user_file.exists():
            with open(user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Файл данных пользователя не найден: {user_file}")
            return {}
    
    def create_user_context(self, compass_data: Dict[str, Any]) -> UserContext:
        """
        Создание контекста пользователя для рассуждений
        
        Args:
            compass_data: Данные из IT Compass
            
        Returns:
            UserContext: Контекст пользователя
        """
        user_id = compass_data.get("user_id", "unknown")
        
        # Создание анализа навыков
        skills_analysis = []
        for skill_id, skill_data in compass_data.get("skills", {}).items():
            analysis = SkillAnalysis(
                skill_id=skill_id,
                skill_name=skill_data.get("name", ""),
                current_level=skill_data.get("level", "beginner"),
                progress_trend=skill_data.get("trend", "stable"),
                estimated_completion=skill_data.get("estimated_completion"),
                related_skills=skill_data.get("related_skills", []),
                learning_efficiency=skill_data.get("efficiency", 0.0)
            )
            skills_analysis.append(analysis)
        
        # Создание контекста пользователя
        user_context = UserContext(
            user_id=user_id,
            current_skills=skills_analysis,
            recent_activity=compass_data.get("recent_activity", []),
            mood_state=compass_data.get("mood_state", {}),
            goals=compass_data.get("goals", []),
            preferences=compass_data.get("preferences", {})
        )
        
        return user_context
    
    def process_user_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Обработка рекомендаций для пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Результат обработки
        """
        logger.info(f"Обработка рекомендаций для пользователя: {user_id}")
        
        # Загрузка данных пользователя
        compass_data = self.load_compass_data(user_id)
        if not compass_data:
            logger.error(f"Не удалось загрузить данные пользователя: {user_id}")
            return {"error": "Не удалось загрузить данные пользователя"}
        
        # Создание контекста пользователя
        user_context = self.create_user_context(compass_data)
        
        # Получение рекомендаций от системы рассуждений
        try:
            recommendations = self.reasoning_integration.generate_skill_recommendations(user_context)
            
            # Анализ контекста пользователя
            context_analysis = self.reasoning_integration.analyze_user_context(user_context)
            
            # Предсказание результатов обучения
            target_skills = [rec.get("skill_id") for rec in recommendations[:3] if rec.get("skill_id")]
            learning_predictions = self.reasoning_integration.predict_learning_outcomes(user_context, target_skills)
            
            # Оптимизация пути обучения
            optimized_path = self.reasoning_integration.optimize_learning_path(user_context, target_skills)
            
            # Анализ влияния настроения
            mood_analysis = self.reasoning_integration.analyze_mood_impact(user_context)
            
            result = {
                "user_id": user_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "recommendations": recommendations,
                "context_analysis": {
                    "response": context_analysis.response,
                    "confidence": context_analysis.confidence,
                    "reasoning_chain": context_analysis.reasoning_chain
                },
                "learning_predictions": learning_predictions,
                "optimized_path": optimized_path,
                "mood_analysis": mood_analysis
            }
            
            # Сохранение результатов
            self.save_recommendations(user_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при обработке рекомендаций: {e}")
            return {"error": str(e)}
    
    def save_recommendations(self, user_id: str, recommendations: Dict[str, Any]):
        """
        Сохранение рекомендаций в файл
        
        Args:
            user_id: ID пользователя
            recommendations: Рекомендации
        """
        recommendations_dir = self.compass_data_path / "recommendations"
        recommendations_dir.mkdir(exist_ok=True)
        
        filename = recommendations_dir / f"recommendations_{user_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Рекомендации сохранены в файл: {filename}")


# ======================
# CLI интерфейс
# ======================

def main():
    """Основная функция CLI"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Интеграция IT Compass с системой рассуждений")
    parser.add_argument("--user-id", required=True, help="ID пользователя")
    parser.add_argument("--data-path", required=True, help="Путь к данным IT Compass")
    parser.add_argument("--reasoning-url", required=True, help="URL системы рассуждений")
    parser.add_argument("--api-key", help="API ключ для системы рассуждений")
    
    args = parser.parse_args()
    
    try:
        # Создание интеграции
        integration = ITCompassIntegration(
            compass_data_path=args.data_path,
            reasoning_url=args.reasoning_url,
            api_key=args.api_key
        )
        
        # Обработка рекомендаций
        result = integration.process_user_recommendations(args.user_id)
        
        # Вывод результата
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        
        if "error" in result:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Ошибка при выполнении интеграции: {e}")
        sys.exit(1)


# ======================
# Пример использования
# ======================

def example_usage():
    """Пример использования интеграции"""
    print("=== Пример интеграции IT Compass с системой рассуждений ===\n")
    
    # Создание интеграции (в реальном использовании замените URL)
    integration = ITCompassIntegration(
        compass_data_path="./data",
        reasoning_url="http://localhost:8000/api/v1",
        api_key="your-api-key-here"
    )
    
    # Создание тестовых данных
    test_data = {
        "user_id": "test_user_001",
        "skills": {
            "python_basics": {
                "name": "Основы Python",
                "level": "intermediate",
                "trend": "improving",
                "efficiency": 0.85,
                "related_skills": ["python_oop", "django_basics"]
            },
            "javascript_basics": {
                "name": "Основы JavaScript",
                "level": "basic",
                "trend": "stable",
                "efficiency": 0.72,
                "related_skills": ["react_basics", "nodejs_basics"]
            }
        },
        "recent_activity": [
            {"type": "skill_completed", "skill_id": "python_basics", "timestamp": "2024-01-15T10:30:00"},
            {"type": "mood_recorded", "mood": 8, "timestamp": "2024-01-15T14:00:00"}
        ],
        "mood_state": {
            "mood_level": 7,
            "stress_level": 3,
            "energy_level": 8
        },
        "goals": [
            {"name": "Стать Full-stack разработчиком", "priority": 1, "deadline": "2024-12-31"},
            {"name": "Изучить React", "priority": 2, "deadline": "2024-06-30"}
        ],
        "preferences": {
            "learning_style": "visual",
            "preferred_time": "evening",
            "difficulty_tolerance": "moderate"
        }
    }
    
    # Сохранение тестовых данных
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    with open(data_dir / "user_test_user_001.json", 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print("Тестовые данные сохранены в ./data/user_test_user_001.json")
    print("Для запуска интеграции используйте команду:")
    print("python reasoning_integration.py --user-id test_user_001 --data-path ./data --reasoning-url http://localhost:8000/api/v1")
    print("\nПримечание: Замените URL системы рассуждений на реальный адрес.")


if __name__ == "__main__":
    # Если скрипт запущен напрямую, показываем пример использования
    example_usage()