"""
IT Compass - система объективного отслеживания карьерного роста в IT
Основное консольное приложение
"""

import os
import sys
from core.tracker import SkillTracker
from utils.portfolio_gen import PortfolioGenerator


def show_directions(tracker):
    """Показать список направлений"""
    directions = tracker.get_directions()
    print("\n🎯 Доступные направления:")
    for i, direction in enumerate(directions, 1):
        print(f"{i}. {direction}")


def show_markers_for_direction(tracker, direction):
    """Показать маркеры для выбранного направления"""
    markers = tracker.get_markers_by_direction(direction)
    print(f"\n📋 Маркеры для направления '{direction}':")
    
    for i, (marker_id, marker) in enumerate(markers.items(), 1):
        status = "✅" if marker_id in tracker.progress.get('completed', {}) else "⏳" if marker_id in tracker.progress.get('in_progress', set()) else "⭕"
        print(f"{status} {i}. [{marker.get('level', 'Неизвестный уровень')}] {marker.get('title', marker_id)}")


def mark_marker_completed(tracker):
    """Отметить маркер как выполненный"""
    directions = tracker.get_directions()
    print("\n🎯 Выберите направление:")
    for i, direction in enumerate(directions, 1):
        print(f"{i}. {direction}")
    
    try:
        choice = int(input("\nВведите номер направления: ")) - 1
        if 0 <= choice < len(directions):
            direction = directions[choice]
            markers = tracker.get_markers_by_direction(direction)
            
            print(f"\n📋 Маркеры для направления '{direction}':")
            marker_list = list(markers.items())
            for i, (marker_id, marker) in enumerate(marker_list, 1):
                status = "✅" if marker_id in tracker.progress.get('completed', {}) else "⏳" if marker_id in tracker.progress.get('in_progress', set()) else "⭕"
                print(f"{status} {i}. [{marker.get('level', 'Неизвестный уровень')}] {marker.get('title', marker_id)}")
            
            marker_choice = int(input("\nВведите номер маркера для отметки как выполненного: ")) - 1
            if 0 <= marker_choice < len(marker_list):
                marker_id = marker_list[marker_choice][0]
                artifact = input("Введите путь к артефакту (опционально): ").strip()
                if not artifact:
                    artifact = None
                
                tracker.mark_completed(marker_id, artifact)
                print(f"✅ Маркер '{marker_id}' отмечен как выполненный!")
            else:
                print("❌ Неверный номер маркера")
        else:
            print("❌ Неверный номер направления")
    except ValueError:
        print("❌ Пожалуйста, введите корректный номер")


def show_progress(tracker):
    """Показать статистику прогресса"""
    stats = tracker.get_progress_stats()
    print("\n📊 Статистика прогресса:")
    print(f"Выполнено: {stats['completed']}")
    print(f"В процессе: {stats['in_progress']}")
    print(f"Всего: {stats['total']}")
    print(f"Процент завершения: {stats['completion_rate']}%")


def generate_portfolio(tracker):
    """Сгенерировать портфолио"""
    generator = PortfolioGenerator(tracker)
    
    print("\n📄 Генерация портфолио")
    print("Выберите формат:")
    print("1. Markdown")
    print("2. JSON")
    print("3. HTML")
    
    try:
        choice = int(input("Введите номер формата: "))
        format_map = {1: "markdown", 2: "json", 3: "html"}
        
        if choice in format_map:
            portfolio = generator.generate_portfolio(format_map[choice])
            
            # Сохраняем портфолио в файл
            format_ext = {1: "md", 2: "json", 3: "html"}
            filename = f"portfolio.{format_ext[choice]}"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(portfolio)
            
            print(f"✅ Портфолио сохранено в файл '{filename}'")
        else:
            print("❌ Неверный номер формата")
    except ValueError:
        print("❌ Пожалуйста, введите корректный номер")


def show_menu():
    """Показать меню"""
    print("\n" + "="*50)
    print("🧭 IT Compass - система отслеживания карьерного роста")
    print("="*50)
    print("1. Просмотр направлений")
    print("2. Просмотр маркеров по направлению")
    print("3. Отметить маркер как выполненный")
    print("4. Просмотр статистики")
    print("5. Сгенерировать портфолио")
    print("0. Выход")
    print("="*50)


def main():
    """Основная функция приложения"""
    print("🚀 Запуск IT Compass...")
    
    # Создаем трекер
    tracker = SkillTracker()
    
    # Основной цикл приложения
    while True:
        show_menu()
        try:
            choice = int(input("\nВыберите действие: "))
            
            if choice == 1:
                show_directions(tracker)
            elif choice == 2:
                directions = tracker.get_directions()
                print("\n🎯 Выберите направление:")
                for i, direction in enumerate(directions, 1):
                    print(f"{i}. {direction}")
                
                try:
                    dir_choice = int(input("Введите номер направления: ")) - 1
                    if 0 <= dir_choice < len(directions):
                        show_markers_for_direction(tracker, directions[dir_choice])
                    else:
                        print("❌ Неверный номер направления")
                except ValueError:
                    print("❌ Пожалуйста, введите корректный номер")
                    
            elif choice == 3:
                mark_marker_completed(tracker)
            elif choice == 4:
                show_progress(tracker)
            elif choice == 5:
                generate_portfolio(tracker)
            elif choice == 0:
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Пожалуйста, введите корректный номер")
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")


if __name__ == "__main__":
    main()