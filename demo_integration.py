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
sys.path.insert(0, str(REPO_ROOT))

from apps.it_compass.src.core.tracker import CareerTracker


def demo_it_compass_scan():
    """1. Сканирование через IT Compass"""
    print("\n" + "="*60)
    print("🧭 STEP 1: IT Compass Scan")
    print("="*60)
    
    tracker = CareerTracker()
    progress = tracker.calculate_progress()
    
    print(f"\n📊 Ваш прогресс по IT Compass:")
    print(f"   Общий: {progress['overall_progress']:.1f}%")
    print(f"   Выполнено маркеров: {progress['total_completed']}/{progress['total_markers']}")
    print(f"\n📈 По доменам:")
    
    for domain, data in progress['domain_breakdown'].items():
        bar = "█" * int(data['percentage'] / 5) + "░" * (20 - int(data['percentage'] / 5))
        print(f"   {domain:<20} {bar} {data['percentage']:.1f}%")
    
    return progress, tracker


def demo_job_search(progress, tracker):
    """2. Поиск вакансий через Job Agent"""
    print("\n" + "="*60)
    print("💼 STEP 2: Job Automation Agent")
    print("="*60)
    
    # Получаем ваши навыки из завершённых маркеров
    completed_markers = tracker.progress.get("completed_markers", [])
    
    # Ключевые навыки для поиска
    key_skills = []
    for skill_name, skill_data in tracker.markers.items():
        for level_markers in skill_data.levels.values():
            for marker in level_markers:
                if marker.id in completed_markers:
                    # Извлекаем навыки из ID маркера
                    skill_lower = skill_name.lower()
                    if 'python' in skill_lower or 'devops' in skill_lower or 'system' in skill_lower:
                        key_skills.append(skill_name)
    
    key_skills = list(set(key_skills))[:5]  # Ограничиваем до 5
    
    print(f"\n🔍 Ваши ключевые навыки:")
    for skill in key_skills:
        print(f"   • {skill}")
    
    # Имитация поиска вакансий (без реального API)
    print(f"\n🔎 Поиск вакансий для профиля:")
    print(f"   Навыки: {', '.join(key_skills)}")
    print(f"   Прогресс: {progress['overall_progress']:.1f}%")
    
    # Пример вакансий (шаблон)
    sample_vacancies = [
        {
            "title": "Cognitive Systems Architect",
            "company": "AI Innovation Lab",
            "level": "Senior",
            "match": "95%",
            "why": "Методология IT Compass + архитектура когнитивных систем"
        },
        {
            "title": "Technical Program Manager (AI/ML)",
            "company": "TechCorp",
            "level": "Senior",
            "match": "88%",
            "why": "Управление микросервисной экосистемой + AI-агенты"
        },
        {
            "title": "Career Technology Product Owner",
            "company": "CareerTech Solutions",
            "level": "Lead",
            "match": "92%",
            "why": "Решение проблемы карьерной неопределённости через методологию"
        },
        {
            "title": "AI Product Methodologist",
            "company": "EdTech Innovations",
            "level": "Middle+",
            "match": "85%",
            "why": "Методология + AI-автоматизация карьерного роста"
        },
        {
            "title": "System Thinking Consultant",
            "company": "Architecture Partners",
            "level": "Senior",
            "match": "90%",
            "why": "Системное мышление + DDD + микросервисы"
        }
    ]
    
    print(f"\n💡 Рекомендованные вакансии:")
    for i, vac in enumerate(sample_vacancies, 1):
        print(f"\n   {i}. {vac['title']} @ {vac['company']}")
        print(f"      Уровень: {vac['level']} | Совпадение: {vac['match']}")
        print(f"      Почему подходит: {vac['why']}")
    
    return sample_vacancies


def demo_next_steps(progress, vacancies):
    """3. Рекомендации по развитию"""
    print("\n" + "="*60)
    print("🎯 STEP 3: Next Steps")
    print("="*60)
    
    # Находим незавершённые high-priority маркеры
    high_priority_pending = []
    for skill_name, skill_data in tracker.markers.items():
        for level_markers in skill_data.levels.values():
            for marker in level_markers:
                if (marker.id not in tracker.progress.get("completed_markers", []) 
                    and marker.priority == "high"):
                    high_priority_pending.append((skill_name, marker))
    
    print(f"\n📚 Что улучшить для повышения match:")
    for i, (skill_name, marker) in enumerate(high_priority_pending[:5], 1):
        print(f"   {i}. {skill_name}: {marker.marker[:60]}...")
    
    print(f"\n🚀 Карьерные рекомендации:")
    print(f"   1. Уделите внимание системному мышлению (+15% к match)")
    print(f"   2. Завершите маркеры DevOps (+10% к match)")
    print(f"   3. Документируйте архитектурные решения (ADR)")
    
    print(f"\n📁 Следующие шаги:")
    print(f"   • Откликнитесь на вакансии с match > 85%")
    print(f"   • Обновите резюме с акцентом на методологию")
    print(f"   • Добавьте портфолио IT Compass")


if __name__ == "__main__":
    print("\n" + "🎬"*30)
    print(" DEMO: IT Compass + Job Automation Agent Integration")
    print("🎬"*30)
    print("\nЭтот демо показывает, как ваша методология работает на практике.")
    print("IT Compass → CareerTracker → Job Agent → Вакансии")
    
    # Запуск демо
    tracker = None  # Для доступа в demo_next_steps
    progress, tracker = demo_it_compass_scan()
    vacancies = demo_job_search(progress, tracker)
    demo_next_steps(progress, vacancies)
    
    print("\n" + "="*60)
    print("✅ DEMO ЗАВЕРШЁН")
    print("="*60)
    print("\n📊 Итоги:")
    print(f"   • Прогресс по IT Compass: {progress['overall_progress']:.1f}%")
    print(f"   • Выполнено маркеров: {progress['total_completed']}")
    print(f"   • Рекомендовано вакансий: {len(vacancies)}")
    print(f"   • Лучшее совпадение: {max(v['match'] for v in vacancies)}")
    
    print(f"\n💡 Вывод:")
    print(f"   Ваша методология IT Compass работает! Вы можете:")
    print(f"   1. Объективно оценивать свои навыки")
    print(f"   2. Находить подходящие вакансии")
    print(f"   3. Видеть путь развития")
    print(f"\n🎯 Следующий шаг: запустить Job Automation Agent для реального поиска")
    print("="*60 + "\n")
