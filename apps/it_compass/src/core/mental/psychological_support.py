"""
Психологическая поддержка для IT Compass
Объединённый модуль, включающий функциональность low_energy_mode и mental_support.
"""

import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PsychologicalSupport:
    """
    Основной класс для психологической поддержки пользователей.
    Предоставляет мотивационные цитаты, контакты для кризисных ситуаций,
    простые активности, оценку риска выгорания и планы восстановления.
    """

    def __init__(self, resources_path: Optional[str] = None):
        """
        Инициализация модуля психологической поддержки.

        Args:
            resources_path: Путь к папке с ресурсами (JSON-файлы).
                Если не указан, используется стандартный путь.
        """
        self.logger = logger
        if resources_path is None:
            # Стандартный путь относительно этого файла
            base = Path(__file__).parent.parent.parent / "support" / "resources"
            self.resources_path = base
        else:
            self.resources_path = Path(resources_path)

        self.motivational_quotes = self._load_motivational_quotes()
        self.crisis_contacts = self._load_crisis_contacts()
        self.simple_activities = self._load_simple_activities()
        self.gentle_encouragements = self._load_gentle_encouragements()

    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Загружает JSON-файл из ресурсов."""
        file_path = self.resources_path / filename
        if not file_path.exists():
            self.logger.warning(f"Файл ресурсов не найден: {file_path}")
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Ошибка загрузки {filename}: {e}")
            return {}

    def _load_motivational_quotes(self) -> List[Dict[str, str]]:
        """Загружает мотивационные цитаты из JSON."""
        data = self._load_json_file("motivational_quotes.json")
        return data.get("motivational_quotes", [])

    def _load_crisis_contacts(self) -> List[Dict[str, str]]:
        """Загружает контакты для кризисных ситуаций из JSON."""
        data = self._load_json_file("crisis_contacts.json")
        return data.get("crisis_contacts", [])

    def _load_simple_activities(self) -> List[str]:
        """
        Загружает список простых активностей.
        Если файла нет, возвращает стандартный список.
        """
        # Можно вынести в отдельный JSON, но пока оставим hardcoded
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
        Загружает список мягких поощрений.
        Если файла нет, возвращает стандартный список.
        """
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

    # --- Основные функции поддержки ---

    def generate_support_report(self) -> Dict[str, Any]:
        """
        Генерирует отчёт психологической поддержки.

        Returns:
            Словарь с мотивационными элементами.
        """
        quote = self.get_random_quote()
        encouragement = random.choice(self.gentle_encouragements)
        activities = random.sample(self.simple_activities, 3)

        return {
            "timestamp": datetime.now().isoformat(),
            "gentle_encouragement": encouragement,
            "motivational_quote": quote,
            "simple_activities": activities,
            "positive_affirmation": self.get_random_affirmation(),
            "message": "Помните, что забота о себе — это не роскошь, а необходимость."
        }

    def get_random_quote(self) -> str:
        """Возвращает случайную мотивационную цитату."""
        if not self.motivational_quotes:
            return "Маленькие шаги ведут к большим достижениям."
        quote_obj = random.choice(self.motivational_quotes)
        return quote_obj.get("text", "")

    def get_random_affirmation(self) -> str:
        """Возвращает случайное позитивное утверждение."""
        affirmations = [
            "Вы способны на большее, чем думаете.",
            "Каждый день вы становитесь лучше.",
            "Ваши усилия имеют значение.",
            "Вы достойны успеха и счастья.",
            "Сегодня — отличный день для новых начинаний."
        ]
        return random.choice(affirmations)

    def is_burnout_risk(self, recent_activity: Dict[str, Any]) -> bool:
        """
        Определяет риск выгорания на основе данных активности.

        Args:
            recent_activity: Словарь с ключами:
                - last_activity: строка времени в ISO формате
                - break_count: количество перерывов за последние 4 часа

        Returns:
            True, если есть риск выгорания, иначе False.
        """
        last_activity_str = recent_activity.get("last_activity")
        break_count = recent_activity.get("break_count", 0)

        if not last_activity_str:
            return False

        try:
            last_activity = datetime.fromisoformat(last_activity_str)
            time_since = datetime.now() - last_activity

            # Риск выгорания, если прошло более 4 часов и мало перерывов
            if time_since > timedelta(hours=4) and break_count < 2:
                return True
        except ValueError:
            self.logger.warning("Некорректный формат даты последней активности")
            return False

        return False

    def suggest_recovery_plan(self) -> Dict[str, Any]:
        """
        Предлагает план восстановления на 3 дня.

        Returns:
            Словарь с планом восстановления.
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
                "Старайтесь спать 7–8 часов"
            ]
        }

    def get_crisis_resources(self) -> Dict[str, Any]:
        """
        Возвращает ресурсы для кризисных ситуаций.

        Returns:
            Словарь с контактами и сообщениями.
        """
        return {
            "contacts": self.crisis_contacts,
            "emergency_message": (
                "Если вы чувствуете, что вам нужна срочная помощь, "
                "немедленно свяжитесь с местными службами экстренной помощи."
            ),
            "support_message": "Вы не одиноки. Помощь доступна 24/7."
        }

    def get_daily_checkin_prompt(self) -> str:
        """Возвращает случайный вопрос для ежедневной самооценки."""
        prompts = [
            "Как вы себя чувствуете сегодня?",
            "Что принесло вам радость сегодня?",
            "Какую маленькую победу вы одержали сегодня?",
            "Что бы вы хотели изменить в своем дне?",
            "За что вы благодарны сегодня?"
        ]
        return random.choice(prompts)

    def export_support_data(self) -> Dict[str, Any]:
        """
        Экспортирует все данные поддержки в виде словаря.

        Returns:
            Словарь с данными поддержки.
        """
        return {
            "motivational_quotes": self.motivational_quotes,
            "crisis_contacts": self.crisis_contacts,
            "simple_activities": self.simple_activities,
            "gentle_encouragements": self.gentle_encouragements,
            "exported_at": datetime.now().isoformat()
        }

    def import_support_data(self, data: Dict[str, Any]):
        """
        Импортирует данные поддержки из словаря.

        Args:
            data: Словарь с данными для импорта.
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
    logging.basicConfig(level=logging.INFO)

    ps = PsychologicalSupport()
    print("=== Психологическая поддержка IT Compass ===")
    report = ps.generate_support_report()
    print(f"Поощрение: {report['gentle_encouragement']}")
    print(f"Цитата: {report['motivational_quote']}")
    print("\nПростые активности:")
    for act in report['simple_activities']:
        print(f"  - {act}")
    print(f"\nАффирмация: {report['positive_affirmation']}")

    # Проверка риска выгорания
    sample_activity = {
        "last_activity": (datetime.now() - timedelta(hours=5)).isoformat(),
        "break_count": 1
    }
    if ps.is_burnout_risk(sample_activity):
        print("\n⚠️  Обнаружен риск выгорания!")
        plan = ps.suggest_recovery_plan()
        print(f"Рекомендуется: {plan['title']}")
        print(plan['description'])
    else:
        print("\n✅ Нет признаков риска выгорания")

    # Кризисные ресурсы
    crisis = ps.get_crisis_resources()
    print(f"\nКонтакты для кризисных ситуаций: {len(crisis['contacts'])} доступно")
    print(f"Ежедневный вопрос: {ps.get_daily_checkin_prompt()}")
