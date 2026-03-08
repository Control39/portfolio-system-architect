# Пример использования IT Compass
# -*- coding: utf-8 -*-

"""
Пример использования IT Compass для отслеживания профессионального развития.

Этот пример демонстрирует:
1. Инициализацию системы отслеживания компетенций
2. Работу с маркерами технологий
3. Запись прогресса пользователя
4. Генерацию рекомендаций
5. Интеграцию с внешними API
6. Психологическую поддержку
7. Генерацию портфолио
"""

import json
import datetime
from pathlib import Path
import sys
import os

# Добавляем путь к модулям IT Compass
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.tracker import CompetencyTracker, TechnologyMarker, UserProgress
from core.api_integration import IntegrationManager, GitHubIntegration, LearningPlatformIntegration
from core.mental_support import MentalSupport, MoodRecord, SelfHelpPractices
from utils.portfolio_gen import PortfolioGenerator, PortfolioSection

def main():
    """Основная функция примера использования"""
    print("=== Пример использования IT Compass ===\n")
    
    # 1. Инициализация системы отслеживания компетенций
    print("1. Инициализация системы отслеживания компетенций")
    tracker = CompetencyTracker("user_001")
    
    # Добавление маркеров технологий
    python_marker = TechnologyMarker(
        id="python_001",
        name="Python",
        category="backend",
        description="Язык программирования Python",
        learning_resources=[
            "https://docs.python.org/3/",
            "https://realpython.com/"
        ],
        assessment_criteria=[
            "Знание синтаксиса",
            "Работа с коллекциями",
            "ООП",
            "Работа с файлами",
            "Использование библиотек"
        ]
    )
    
    django_marker = TechnologyMarker(
        id="django_001",
        name="Django",
        category="backend",
        description="Веб-фреймворк для Python",
        learning_resources=[
            "https://docs.djangoproject.com/",
            "https://djangogirls.org/"
        ],
        assessment_criteria=[
            "Создание проекта",
            "Работа с моделями",
            "Создание представлений",
            "Работа с формами",
            "Аутентификация"
        ]
    )
    
    tracker.add_marker(python_marker)
    tracker.add_marker(django_marker)
    
    print(f"Добавлено маркеров: {len(tracker.markers)}")
    print()
    
    # 2. Работа с прогрессом пользователя
    print("2. Работа с прогрессом пользователя")
    
    # Запись прогресса по Python
    python_progress = UserProgress(
        marker_id="python_001",
        user_id="user_001",
        level=3,  # Средний уровень
        confidence=4,  # Высокая уверенность
        last_assessment=datetime.date.today(),
        achievements=[
            "Завершен курс Python для начинающих",
            "Создан веб-скрапер",
            "Реализован REST API"
        ],
        projects=[
            {
                "name": "Веб-скрапер новостей",
                "description": "Скрапер для сбора новостей с нескольких источников",
                "technologies": ["Python", "BeautifulSoup", "Requests"],
                "github_url": "https://github.com/user/news-scraper"
            }
        ]
    )
    
    tracker.record_progress(python_progress)
    
    # Запись прогресса по Django
    django_progress = UserProgress(
        marker_id="django_001",
        user_id="user_001",
        level=2,  # Начальный уровень
        confidence=3,  # Средняя уверенность
        last_assessment=datetime.date.today(),
        achievements=[
            "Создан блог на Django",
            "Реализована система аутентификации"
        ],
        projects=[
            {
                "name": "Блог на Django",
                "description": "Персональный блог с системой комментариев",
                "technologies": ["Python", "Django", "HTML", "CSS"],
                "github_url": "https://github.com/user/django-blog"
            }
        ]
    )
    
    tracker.record_progress(django_progress)
    
    print(f"Записано прогрессов: {len(tracker.progress_history)}")
    print()
    
    # 3. Генерация рекомендаций
    print("3. Генерация рекомендаций")
    recommendations = tracker.generate_recommendations()
    
    print(f"Сгенерировано рекомендаций: {len(recommendations)}")
    for i, rec in enumerate(recommendations[:3], 1):  # Показываем первые 3 рекомендации
        print(f"{i}. {rec.title}")
        print(f"   Приоритет: {rec.priority}")
        print(f"   Тип: {rec.type}")
        print(f"   {rec.description}")
        print()
    
    # 4. Интеграция с внешними API
    print("4. Интеграция с внешними API")
    
    # Создание менеджера интеграций
    # В реальном использовании конфигурация будет загружена из файла
    integration_manager = IntegrationManager("./config/api_settings.json")
    
    # Для примера создаем тестовые интеграции
    github_integration = GitHubIntegration("test_github_token")
    coursera_integration = LearningPlatformIntegration("Coursera", "https://api.coursera.org/api", "test_coursera_key")
    
    integration_manager.add_integration("github", github_integration)
    integration_manager.add_integration("coursera", coursera_integration)
    
    print(f"Интеграций добавлено: {len(integration_manager.integrations)}")
    
    # Синхронизация данных (в реальном использовании замените "test_user" на реальный ID)
    sync_result = integration_manager.sync_user_data("test_user")
    print(f"Синхронизировано активностей: {sync_result['summary']['total_activities']}")
    print(f"Синхронизировано ресурсов: {sync_result['summary']['total_resources']}")
    print()
    
    # 5. Психологическая поддержка
    print("5. Психологическая поддержка")
    
    mental_support = MentalSupport("user_001")
    
    # Запись психологического состояния
    mood_record = MoodRecord(
        date=datetime.date.today(),
        mood_level=4,  # Хорошее настроение
        stress_level=2,  # Низкий стресс
        energy_level=3,  # Умеренный уровень энергии
        satisfaction_level=4,  # Высокая удовлетворенность
        notes="Чувствую прогресс в изучении Django",
        triggers=["успешное завершение проекта", "позитивная обратная связь"],
        coping_strategies=["перерыв на прогулку", "общение с коллегами"]
    )
    
    mental_support.record_mood(mood_record)
    
    # Получение рекомендаций психологической поддержки
    mental_recommendations = mental_support.get_current_recommendations()
    print(f"Рекомендаций психологической поддержки: {len(mental_recommendations)}")
    
    if mental_recommendations:
        rec = mental_recommendations[0]
        print(f"Пример рекомендации: {rec.title}")
        print(f"Описание: {rec.description}")
    print()
    
    # 6. Генерация портфолио
    print("6. Генерация портфолио")
    
    portfolio_gen = PortfolioGenerator("user_001")
    
    # Добавление секций в портфолио
    portfolio_gen.add_section(PortfolioSection(
        id="about",
        title="Обо мне",
        content="Стремлюсь стать опытным Python разработчиком с фокусом на веб-технологии.",
        order=1
    ))
    
    portfolio_gen.add_section(PortfolioSection(
        id="skills",
        title="Навыки",
        content="Python, Django, REST API, Git, Docker",
        order=2
    ))
    
    portfolio_gen.add_section(PortfolioSection(
        id="projects",
        title="Проекты",
        content=json.dumps([
            {
                "name": "Веб-скрапер новостей",
                "description": "Скрапер для сбора новостей с нескольких источников",
                "technologies": ["Python", "BeautifulSoup", "Requests"],
                "github_url": "https://github.com/user/news-scraper"
            },
            {
                "name": "Блог на Django",
                "description": "Персональный блог с системой комментариев",
                "technologies": ["Python", "Django", "HTML", "CSS"],
                "github_url": "https://github.com/user/django-blog"
            }
        ], ensure_ascii=False, indent=2),
        order=3
    ))
    
    # Генерация портфолио
    portfolio_content = portfolio_gen.generate_portfolio()
    print("Портфолио сгенерировано успешно!")
    print(f"Секций в портфолио: {len(portfolio_gen.sections)}")
    print()
    
    # 7. Получение сводки
    print("7. Сводка по системе")
    
    # Сводка по компетенциям
    competency_summary = tracker.get_competency_summary()
    print("Сводка по компетенциям:")
    print(f"- Всего маркеров: {competency_summary['total_markers']}")
    print(f"- Записей прогресса: {competency_summary['total_progress_records']}")
    print(f"- Средний уровень: {competency_summary['average_level']:.1f}")
    print(f"- Средняя уверенность: {competency_summary['average_confidence']:.1f}")
    print()
    
    # Сводка по психологическому состоянию
    mood_summary = mental_support.get_mood_summary()
    print("Сводка по психологическому состоянию:")
    if "latest_record" in mood_summary:
        print(f"- Дата последней записи: {mood_summary['latest_record']['date']}")
        print(f"- Уровень настроения: {mood_summary['latest_record']['mood_level']}")
        print(f"- Уровень стресса: {mood_summary['latest_record']['stress_level']}")
    print()
    
    print("=== Пример завершен ===")

if __name__ == "__main__":
    main()