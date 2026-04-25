"""Психологическая поддержка для IT Compass (совместимость с предыдущими версиями)
Обеспечивает интерфейс MentalSupport, MoodRecord, SelfHelpPractices,
используя объединённый модуль PsychologicalSupport.
"""

from datetime import date, datetime
from typing import Any

from .mental.psychological_support import PsychologicalSupport as PS


class MoodRecord:
    """Запись психологического состояния пользователя"""

    def __init__(
        self,
        date: date,
        mood_level: int,
        stress_level: int,
        energy_level: int,
        satisfaction_level: int,
        notes: str = "",
        triggers: list[str] | None = None,
        coping_strategies: list[str] | None = None,
    ):
        self.date = date
        self.mood_level = mood_level  # 1-5
        self.stress_level = stress_level  # 1-5
        self.energy_level = energy_level  # 1-5
        self.satisfaction_level = satisfaction_level  # 1-5
        self.notes = notes
        self.triggers = triggers or []
        self.coping_strategies = coping_strategies or []

    def to_dict(self) -> dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "date": self.date.isoformat(),
            "mood_level": self.mood_level,
            "stress_level": self.stress_level,
            "energy_level": self.energy_level,
            "satisfaction_level": self.satisfaction_level,
            "notes": self.notes,
            "triggers": self.triggers,
            "coping_strategies": self.coping_strategies,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MoodRecord":
        """Создание из словаря"""
        return cls(
            date=date.fromisoformat(data["date"]),
            mood_level=data["mood_level"],
            stress_level=data["stress_level"],
            energy_level=data["energy_level"],
            satisfaction_level=data["satisfaction_level"],
            notes=data.get("notes", ""),
            triggers=data.get("triggers", []),
            coping_strategies=data.get("coping_strategies", []),
        )


class SelfHelpPractices:
    """Практики самопомощи"""

    def __init__(self, name: str, description: str, duration_minutes: int):
        self.name = name
        self.description = description
        self.duration_minutes = duration_minutes

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
        }


class MentalSupport:
    """Основной класс психологической поддержки (совместимость)"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.psychological_support = PS()
        self.mood_history: list[MoodRecord] = []

    def record_mood(self, mood_record: MoodRecord) -> None:
        """Запись психологического состояния"""
        self.mood_history.append(mood_record)
        # Также можно сохранять в хранилище, но для совместимости просто храним в памяти

    def get_current_recommendations(self) -> list[dict[str, Any]]:
        """Получение текущих рекомендаций психологической поддержки"""
        # Используем PsychologicalSupport для генерации рекомендаций
        report = self.psychological_support.generate_support_report()
        # Преобразуем в формат, ожидаемый вызывающим кодом
        return [
            {
                "title": "Мотивационная цитата",
                "description": report["motivational_quote"],
                "type": "motivation",
            },
            {
                "title": "Простая активность",
                "description": report["simple_activities"][0] if report["simple_activities"] else "",
                "type": "activity",
            },
            {
                "title": "Поощрение",
                "description": report["gentle_encouragement"],
                "type": "encouragement",
            },
        ]

    def get_mood_summary(self) -> dict[str, Any]:
        """Сводка по психологическому состоянию"""
        if not self.mood_history:
            return {"message": "Нет записей о настроении"}

        latest = self.mood_history[-1]
        avg_mood = sum(m.mood_level for m in self.mood_history) / len(self.mood_history)
        avg_stress = sum(m.stress_level for m in self.mood_history) / len(self.mood_history)

        return {
            "latest_record": latest.to_dict(),
            "average_mood": avg_mood,
            "average_stress": avg_stress,
            "total_records": len(self.mood_history),
            "trend": "stable",  # упрощённо
        }

    def get_low_energy_support(self) -> dict[str, Any]:
        """Получение поддержки для режима низкой энергии"""
        return self.psychological_support.generate_support_report()

    def check_burnout_risk(self, recent_activity: dict[str, Any]) -> bool:
        """Проверка риска выгорания"""
        return self.psychological_support.is_burnout_risk(recent_activity)

    def export_data(self) -> dict[str, Any]:
        """Экспорт данных поддержки"""
        return {
            "user_id": self.user_id,
            "mood_history": [m.to_dict() for m in self.mood_history],
            "psychological_support": self.psychological_support.export_support_data(),
            "exported_at": datetime.now().isoformat(),
        }


# Алиас для обратной совместимости
LowEnergyMode = PS


# Пример использования (для тестирования)
if __name__ == "__main__":
    ms = MentalSupport("test_user")
    print("MentalSupport инициализирован")

    mr = MoodRecord(
        date=date.today(),
        mood_level=4,
        stress_level=2,
        energy_level=3,
        satisfaction_level=4,
        notes="Тестовая запись",
    )
    ms.record_mood(mr)

    recommendations = ms.get_current_recommendations()
    print(f"Рекомендаций: {len(recommendations)}")

    summary = ms.get_mood_summary()
    print(f"Сводка: {summary['total_records']} записей")

    low_energy = LowEnergyMode()
    report = low_energy.generate_support_report()
    print(f"Отчёт низкой энергии: {report['gentle_encouragement']}")

