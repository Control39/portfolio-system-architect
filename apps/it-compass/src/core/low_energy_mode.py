"""
Режим низкой энергии для IT Compass (обновлённая версия)
Использует объединённый модуль PsychologicalSupport для обеспечения функциональности.
Обеспечивает обратную совместимость с предыдущими версиями.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Импортируем PsychologicalSupport из core.mental
try:
    from .mental.psychological_support import PsychologicalSupport
except ImportError:
    # Fallback для случаев, когда модуль не найден
    from ..support.low_energy_mode import PsychologicalSupport


class LowEnergyMode:
    """Режим поддержки в периоды низкой энергии (совместимость)"""
    
    def __init__(self):
        """Инициализация режима низкой энергии"""
        self.logger = logging.getLogger(__name__)
        self.psychological_support = PsychologicalSupport()
    
    def generate_low_energy_report(self) -> Dict:
        """
        Генерация отчета для режима низкой энергии
        
        Returns:
            Словарь с отчетом для режима низкой энергии
        """
        report = self.psychological_support.generate_support_report()
        # Преобразуем в старый формат для совместимости
        return {
            "timestamp": report["timestamp"],
            "gentle_encouragement": report["gentle_encouragement"],
            "motivational_quote": report["motivational_quote"],
            "simple_activities": report["simple_activities"],
            "positive_affirmation": report["positive_affirmation"],
            "message": report.get("message", "Помните, что забота о себе - это не роскошь, а необходимость.")
        }
    
    def is_burnout_risk(self, recent_activity: Dict) -> bool:
        """
        Определение риска выгорания
        
        Args:
            recent_activity: Данные о недавней активности
            
        Returns:
            True, если есть риск выгорания, иначе False
        """
        return self.psychological_support.is_burnout_risk(recent_activity)
    
    def suggest_recovery_plan(self) -> Dict:
        """
        Предложение плана восстановления
        
        Returns:
            Словарь с планом восстановления
        """
        return self.psychological_support.suggest_recovery_plan()
    
    def get_crisis_resources(self) -> Dict:
        """
        Получение ресурсов для кризисных ситуаций
        
        Returns:
            Словарь с ресурсами для кризисных ситуаций
        """
        return self.psychological_support.get_crisis_resources()
    
    def get_daily_checkin_prompt(self) -> str:
        """
        Получение ежедневного приглашения к самооценке
        
        Returns:
            Строка с приглашением к самооценке
        """
        return self.psychological_support.get_daily_checkin_prompt()
    
    def export_support_data(self) -> Dict:
        """
        Экспорт данных поддержки
        
        Returns:
            Словарь с экспортированными данными поддержки
        """
        return self.psychological_support.export_support_data()
    
    def import_support_data(self, data: Dict):
        """
        Импорт данных поддержки
        
        Args:
            data: Словарь с данными для импорта
        """
        self.psychological_support.import_support_data(data)


# Алиас для обратной совместимости (можно использовать PsychologicalSupport напрямую)
LowEnergyModeAlias = PsychologicalSupport


# Пример использования
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # Создаем режим низкой энергии
    low_energy_mode = LowEnergyMode()
    
    # Генерируем отчет
    report = low_energy_mode.generate_low_energy_report()
    
    print("=== Режим низкой энергии (обновлённый) ===")
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