#!/usr/bin/env python3
"""
DEMO: IT Compass + Job Automation Agent Integration

Показывает, как:
1. IT Compass сканирует проект и собирает данные
2. Передаёт их в Job Automation Agent
3. Job Agent ищет подходящие вакансии

Запуск: python demo_integration.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

from apps.it_compass.src.core.tracker import CareerTracker


def demo_it_compass_scan():
    """1. Сканирование через IT Compass"""
    print("\n" + "=" * 60)
    print("🧭 STEP 1: IT Compass Scan")
    print("=" * 60)

    tracker = CareerTracker()
    progress = tracker.calculate_progress()

    print("\n📊 Ваш прогресс по IT Compass:")
    print(f"   Общий: {progress['overall_progress']:.1f}%")
    print(f"   Выполнено маркеров: {progress['total_completed']}/{progress['total_markers']}")
    print("\n📈 По доменам:")

    for domain, data in progress["domain_breakdown"].items():
        bar = "█" * int(data["percentage"] / 5) + "░" * (20 - int(data["percentage"] / 5))
        print(f"   {domain:<20} {bar} {data['percentage']:.1f}%")

    return progress, tracker


def demo_job_search(progress, tracker):
    """2. Поиск вакансий через реальные сервисы"""
    print("\n" + "=" * 60)
    print("💼 STEP 2: Job Automation Agent (REAL SEARCH)")
    print("=" * 60)

    # Получаем ваши навыки из завершённых маркеров
    completed_markers = tracker.progress.get("completed_markers", [])

    # Ключевые навыки для поиска
    key_skills = []
    for skill_name, skill_data in tracker.markers.items():
        for level_markers in skill_data.levels.values():
            for marker in level_markers:
                if marker.id in completed_markers:
                    skill_lower = skill_name.lower()
                    if any(
                        x in skill_lower for x in ["python", "devops", "system", "docker", "git"]
                    ):
                        key_skills.append(skill_name)

    key_skills = list(set(key_skills))[:5]

    print("\n🔍 Ваши ключевые навыки:")
    for skill in key_skills:
        print(f"   • {skill}")

    # Формируем поисковый запрос
    search_query = f"{', '.join(key_skills)} архитектор системное мышление методология"
    print("\n🔎 Поиск вакансий по запросу:")
    print(f'   "{search_query}"')

    # Имитация реального поиска (раскомментируйте для работы)
    try:
        from apps.job_automation_agent.src.job_search import search_all_jobs
        import asyncio

        print("\n   ⏳ Поиск на hh.ru и Habr Career...")
        vacancies = asyncio.run(search_all_jobs(search_query, area="113"))

        if vacancies:
            print(f"\n   ✅ Найдено {len(vacancies)} вакансий!")
        else:
            print("\n   ⚠️  Вакансий не найдено. Используем шаблон.")
            vacancies = []

    except Exception as e:
        print(f"\n   ⚠️  Ошибка поиска: {e}")
        print("   Используем шаблон вакансий...")
        vacancies = []

    # Если поиск не дал результатов или для демо, используем шаблон
    if not vacancies:
        vacancies = [
            {
                "title": "Cognitive Systems Architect",
                "company": "AI Innovation Lab",
                "level": "Senior",
                "match": "95%",
                "why": "Методология IT Compass + архитектура когнитивных систем",
                "source": "Шаблон",
            },
            {
                "title": "Technical Program Manager (AI/ML)",
                "company": "TechCorp",
                "level": "Senior",
                "match": "88%",
                "why": "Управление микросервисной экосистемой + AI-агенты",
                "source": "Шаблон",
            },
            {
                "title": "Career Technology Product Owner",
                "company": "CareerTech Solutions",
                "level": "Lead",
                "match": "92%",
                "why": "Решение проблемы карьерной неопределённости через методологию",
                "source": "Шаблон",
            },
        ]

    print("\n💡 Рекомендованные вакансии:")
    for i, vac in enumerate(vacancies[:5], 1):
        print(f"\n   {i}. {vac['title']} @ {vac['company']}")
        print(f"      Уровень: {vac['level']} | Совпадение: {vac['match']}")
        print(f"      Почему подходит: {vac['why']}")
        print(f"      Источник: {vac.get('source', 'hh.ru/Habr Career')}")

    return vacancies


def demo_next_steps(progress, vacancies):
    """3. Рекомендации по развитию"""
    print("\n" + "=" * 60)
    print("🎯 STEP 3: Next Steps")
    print("=" * 60)

    # Находим незавершённые high-priority маркеры
    high_priority_pending = []
    for skill_name, skill_data in tracker.markers.items():
        for level_markers in skill_data.levels.values():
            for marker in level_markers:
                if (
                    marker.id not in tracker.progress.get("completed_markers", [])
                    and marker.priority == "high"
                ):
                    high_priority_pending.append((skill_name, marker))

    print("\n📚 Что улучшить для повышения match:")
    for i, (skill_name, marker) in enumerate(high_priority_pending[:5], 1):
        print(f"   {i}. {skill_name}: {marker.marker[:60]}...")

    print("\n🚀 Карьерные рекомендации:")
    print("   1. Уделите внимание системному мышлению (+15% к match)")
    print("   2. Завершите маркеры DevOps (+10% к match)")
    print("   3. Документируйте архитектурные решения (ADR)")

    print("\n📁 Следующие шаги:")
    print("   • Откликнитесь на вакансии с match > 85%")
    print("   • Обновите резюме с акцентом на методологию")
    print("   • Добавьте портфолио IT Compass")


if __name__ == "__main__":
    print("\n" + "🎬" * 30)
    print(" DEMO: IT Compass + Job Automation Agent Integration")
    print("🎬" * 30)
    print("\nЭтот демо показывает, как ваша методология работает на практике.")
    print("IT Compass → CareerTracker → Job Agent → Вакансии")

    # Запуск демо
    tracker = None  # Для доступа в demo_next_steps
    progress, tracker = demo_it_compass_scan()
    vacancies = demo_job_search(progress, tracker)
    demo_next_steps(progress, vacancies)

    print("\n" + "=" * 60)
    print("✅ DEMO ЗАВЕРШЁН")
    print("=" * 60)
    print("\n📊 Итоги:")
    print(f"   • Прогресс по IT Compass: {progress['overall_progress']:.1f}%")
    print(f"   • Выполнено маркеров: {progress['total_completed']}")
    print(f"   • Рекомендовано вакансий: {len(vacancies)}")
    print(f"   • Лучшее совпадение: {max(v['match'] for v in vacancies)}")

    print("\n💡 Вывод:")
    print("   Ваша методология IT Compass работает! Вы можете:")
    print("   1. Объективно оценивать свои навыки")
    print("   2. Находить подходящие вакансии")
    print("   3. Видеть путь развития")
    print("\n🎯 Следующий шаг: запустить Job Automation Agent для реального поиска")
    print("=" * 60 + "\n")
