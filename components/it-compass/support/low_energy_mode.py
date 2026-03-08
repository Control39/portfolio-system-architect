"""
Режим низкой энергии для IT Compass
Поддержка пользователей в периоды низкой мотивации и энергии
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging


class LowEnergyMode:
    """Режим поддержки в периоды низкой энергии"""
    
    def __init__(self):
        """Инициализация режима низкой энергии"""
        self.logger = logging.getLogger(__name__)
        self.motivational_quotes = self._load_motivational_quotes()
        self.crisis_contacts = self._load_crisis_contacts()
        self.simple_activities = self._load_simple_activities()
        self.gentle_encouragements = self._load_gentle_encouragements()
    
    def _load_motivational_quotes(self) -> List[str]:
        """
        Загрузка мотивационных цитат
        
        Returns:
            Список мотивационных цитат
        """
        # В реальной реализации эти данные могут загружаться из файла
        return [
            "Маленькие шаги ведут к большим достижениям.",
            "Каждый день - это новая возможность.",
            "Ты сильнее, чем думаешь.",
            "Прогресс важнее совершенства.",
            "Отдых - это не лень, а необходимость.",
            "Ты уже сделал многое. Продолжай в том же духе.",
            "Не забывай заботиться о себе.",
            "Каждый момент - это шанс начать заново."
        ]
    
    def _load_crisis_contacts(self) -> List[Dict]:
        """
        Загрузка контактов для кризисных ситуаций
        
        Returns:
            Список контактов для кризисных ситуаций
        """
        # В реальной реализации эти данные могут загружаться из файла
        return [
            {
                "name": "Единый телефон доверия",
                "phone": "8-800-2000-122",
                "description": "Круглосуточная поддержка психологов"
            },
            {
                "name": "Служба спасения",
                "phone": "112",
                "description": "Экстренная помощь в любой ситуации"
            },
            {
                "name": "Детский телефон доверия",
                "phone": "8-800-2000-121",
                "description": "Поддержка для детей и подростков"
            }
        ]
    
    def _load_simple_activities(self) -> List[str]:
        """
        Загрузка списка простых активностей
        
        Returns:
            Список простых активностей
        """
        # В реальной реализации эти данные могут загружаться из файла
        return [
            "Сделайте 5 глубоких вдохов",
            "Выпейте стакан воды",
            "Посмотрите в окно 2 минуты",
            "Сделайте легкую растяжку",
            "Послушайте любимую музыку",
            "Напишите 3 вещи, за которые благодарны",
            "Погладьте домашнее животное",
            "Сходите на улицу на 5 минут",
            "Сделайте короткий перерыв",
            "Почитайте что-нибудь приятное"
        ]
    
    def _load_gentle_encouragements(self) -> List[str]:
        """
        Загрузка списка мягких поощрений
        
        Returns:
            Список мягких поощрений
        """
        # В реальной реализации эти данные могут загружаться из файла
        return [
            "Сегодня вы сделали важный шаг, просто включив это приложение.",
            "Вы заслуживаете отдыха и заботы.",
            "Ваше благополучие важнее любого достижения.",
            "Даже маленькие шаги имеют значение.",
            "Вы уже проявили силу, признав, что вам нужна поддержка.",
            "Позвольте себе быть неидеальным сегодня.",
            "Ваше чувство усталости понятно и закономерно.",
            "Вы имеете право на перерыв."
        ]
    
    def generate_low_energy_report(self) -> Dict:
        """
        Генерация отчета для режима низкой энергии
        
        Returns:
            Словарь с отчетом для режима низкой энергии
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "gentle_encouragement": random.choice(self.gentle_encouragements),
            "motivational_quote": random.choice(self.motivational_quotes),
            "simple_activities": random.sample(self.simple_activities, 3),
            "positive_affirmation": random.choice(self.motivational_quotes),
            "message": "Помните, что забота о себе - это не роскошь, а необходимость."
        }
    
    def is_burnout_risk(self, recent_activity: Dict) -> bool:
        """
        Определение риска выгорания
        
        Args:
            recent_activity: Данные о недавней активности
            
        Returns:
            True, если есть риск выгорания, иначе False
        """
        # Проверяем признаки выгорания:
        # 1. Длительный период без перерывов
        # 2. Снижение активности
        # 3. Частые записи о низком настроении (в реальной реализации)
        
        last_activity_str = recent_activity.get("last_activity")
        break_count = recent_activity.get("break_count", 0)
        
        if not last_activity_str:
            return False
        
        try:
            last_activity = datetime.fromisoformat(last_activity_str)
            time_since_last_activity = datetime.now() - last_activity
            
            # Риск выгорания, если:
            # - Прошло более 4 часов с последней активности И
            # - Мало перерывов
            if time_since_last_activity > timedelta(hours=4) and break_count < 2:
                return True
                
        except ValueError:
            # Некорректный формат даты
            self.logger.warning("Некорректный формат даты последней активности")
            return False
        
        return False
    
    def suggest_recovery_plan(self) -> Dict:
        """
        Предложение плана восстановления
        
        Returns:
            Словарь с планом восстановления
        """
        return {
            "title": "План восстановления",
            "description": "Пошаговый план для восстановления энергии и мотивации",
            "steps": [
                {
                    "day": 1,
                    "activities": [
                        "Полный день отдыха без работы",
                        "Минимум экранного времени",
                        "Прогулка на свежем воздухе",
                        "Ранний сон (до 22:00)"
                    ]
                },
                {
                    "day": 2,
                    "activities": [
                        "Легкие физические упражнения",
                        "Медитация или дыхательные практики",
                        "Чтение книги или журналов",
                        "Общение с близкими людьми"
                    ]
                },
                {
                    "day": 3,
                    "activities": [
                        "Постепенное возвращение к работе",
                        "Работа не более 4 часов в день",
                        "Частые перерывы (каждые 30 минут)",
                        "Работа только над простыми задачами"
                    ]
                }
            ],
            "recommendations": [
                "Установите напоминания для перерывов",
                "Избегайте сложных задач первые 2 дня",
                "Пейте достаточно воды",
                "Старайтесь спать 7-8 часов"
            ]
        }
    
    def get_crisis_resources(self) -> Dict:
        """
        Получение ресурсов для кризисных ситуаций
        
        Returns:
            Словарь с ресурсами для кризисных ситуаций
        """
        return {
            "contacts": self.crisis_contacts,
            "emergency_message": "Если вы чувствуете, что вам нужна срочная помощь, немедленно свяжитесь с местными службами экстренной помощи",
            "support_message": "Вы не одиноки. Помощь доступна 24/7."
        }
    
    def get_daily_checkin_prompt(self) -> str:
        """
        Получение ежедневного приглашения к самооценке
        
        Returns:
            Строка с приглашением к самооценке
        """
        prompts = [
            "Как вы себя чувствуете сегодня?",
            "Что принесло вам радость сегодня?",
            "Какую маленькую победу вы одержали сегодня?",
            "Что бы вы хотели изменить в своем дне?",
            "За что вы благодарны сегодня?"
        ]
        
        return random.choice(prompts)
    
    def export_support_data(self) -> Dict:
        """
        Экспорт данных поддержки
        
        Returns:
            Словарь с экспортированными данными поддержки
        """
        return {
            "motivational_quotes": self.motivational_quotes,
            "crisis_contacts": self.crisis_contacts,
            "simple_activities": self.simple_activities,
            "gentle_encouragements": self.gentle_encouragements,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_support_data(self, data: Dict):
        """
        Импорт данных поддержки
        
        Args:
            data: Словарь с данными для импорта
        """
        if "motivational_quotes" in data:
            self.motivational_quotes = data["motivational_quotes"]
        
        if "crisis_contacts" in data:
            self.crisis_contacts = data["crisis_contacts"]
        
        if "simple_activities" in data:
            self.simple_activities = data["simple_activities"]
        
        if "gentle_encouragements" in data:
            self.gentle_encouragements = data["gentle_encouragements"]
        
        self.logger.info("Данные поддержки успешно импортированы")


# Пример использования
if __name__ == "__main__":
    # Создаем режим низкой энергии
    low_energy_mode = LowEnergyMode()
    
    # Генерируем отчет
    report = low_energy_mode.generate_low_energy_report()
    
    print("=== Режим низкой энергии ===")
    print(f"Сообщение поддержки: {report['gentle_encouragement']}")
    print(f"Мотивационная цитата: {report['motivational_quote']}")
    print("\nПростые активности:")
    for activity in report['simple_activities']:
        print(f"- {activity}")
    print(f"\nПозитивное напоминание: {report['positive_affirmation']}")
    
    # Проверяем риск выгорания (пример)
    sample_activity = {
        "last_activity": (datetime.now() - timedelta(hours=5)).isoformat(),
        "break_count": 1
    }
    
    if low_energy_mode.is_burnout_risk(sample_activity):
        print("\n⚠️ Обнаружен риск выгорания!")
        recovery_plan = low_energy_mode.suggest_recovery_plan()
        print(f"Рекомендуется: {recovery_plan['title']}")
        print(recovery_plan['description'])
    else:
        print("\n✅ Нет признаков риска выгорания")