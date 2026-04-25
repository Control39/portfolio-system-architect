#!/usr/bin/env python3
"""Пример использования IT Compass
Методология "Объективные маркеры компетенций"
© 2025 Ekaterina Kudelya. CC BY-ND 4.0
"""

from src.core.tracker import CareerTracker


def main():
    print("🧭 IT Compass - Пример использования")
    print("=" * 50)

    tracker = CareerTracker()

    print(f"📊 Загружено навыков: {len(tracker.markers)}")
    for skill_name in tracker.markers.keys():
        print(f"  • {skill_name}")

    print("\n📈 Текущий прогресс:")
    tracker.show_progress()

    print("\n🎯 Рекомендации:")
    tracker.show_recommendations(limit=3)

    print("\n📄 Для создания портфолио запустите:")
    print("  python src/utils/portfolio_gen.py")


if __name__ == "__main__":
    main()


