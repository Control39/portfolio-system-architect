import os
import sys

# Добавляем корневой каталог в PYTHONPATH для импортов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Теперь можно импортировать job_agent после добавления пути
from job_agent import (
    INTEGRATION_ENABLED,
    analyze_requirements,
    career_tracker,
    process_request_sync,
)


def test_integration():
    """Тестовая функция для проверки интеграции системы отслеживания карьеры с анализом вакансий."""

    if not INTEGRATION_ENABLED:
        print("❌ Интеграция с системой отслеживания карьеры не активирована")
        return False

    print("🔍 Тестирование интеграции Job Agent с CareerTracker\n")

    # Сохраняем текущий прогресс для восстановления
    original_completed = career_tracker.progress["completed_markers"][:]
    print(f"Базовый прогресс: {len(original_completed)} выполненных маркеров\n")

    # Очищаем прогресс для тестирования
    career_tracker.progress["completed_markers"] = []
    career_tracker._save_progress()
    print("🧹 Прогресс очищен для тестирования")

    try:
        # Тест 1: Анализ вакансии с Python
        print("1. Анализ вакансии Python разработчика...")
        job_description_python = """
        Требуется Senior Python Developer. Необходимые навыки: Python, FastAPI, PostgreSQL, Docker, Git.
        Опыт работы: 3+ года. Ответственности: разработка REST API, оптимизация запросов к БД, написание unit-тестов.
        """

        result = analyze_requirements(job_description_python)

        if "career_integration" in result:
            print("✅ Интеграция успешна")
            print(
                f"   Найдено соответствий: {result['career_integration']['matched_markers_count']}"
            )
            print(
                f"   Проставлено отметок: {result['career_integration']['marked_as_completed']}"
            )

            if result["career_integration"]["matched_markers_count"] > 0:
                print("   ID найденных маркеров:")
                for marker_id in result["career_integration"]["matched_marker_ids"][:5]:
                    print(f"   - {marker_id}")
                if len(result["career_integration"]["matched_marker_ids"]) > 5:
                    print(
                        f"   ... и ещё {len(result['career_integration']['matched_marker_ids']) - 5}"
                    )

            # Проверяем, что прогресс обновился
            new_completed = career_tracker.progress["completed_markers"]
            new_markers = len(new_completed) - len(original_completed)
            print(f"\n   Новых выполненных маркеров: {new_markers}")

            if new_markers != result["career_integration"]["marked_as_completed"]:
                print(
                    f"⚠️ Количество новых маркеров ({new_markers}) не совпадает с отчетом интеграции ({result['career_integration']['marked_as_completed']})"
                )
            else:
                print(
                    f"✅ Количество новых маркеров ({new_markers}) совпадает с отчетом интеграции"
                )

        else:
            print(
                "❌ Интеграция не сработала - отсутствует career_integration в результате"
            )
            return False

        print("\n")

        # Тест 2: Анализ вакансии без соответствий
        print("2. Анализ вакансии с несуществующими навыками...")
        job_description_unknown = """
        Требуется специалист по квантовым вычислениям на MarsLang.
        Навыки: MarsLang, Quantum Computing, Mars Database.
        """

        result_unknown = analyze_requirements(job_description_unknown)

        if "career_integration" in result_unknown:
            if result_unknown["career_integration"]["matched_markers_count"] == 0:
                print("✅ Корректно обработана вакансия без соответствий")
            else:
                print(
                    f"⚠️ Найдены ложные соответствия: {result_unknown['career_integration']['matched_markers_count']}"
                )
                return False
        else:
            print("❌ Интеграция не сработала для вакансии без навыков")
            return False

        print("\n")

        # Тест 3: Проверка через process_request_sync
        print("3. Проверка через основной интерфейс агента...")
        agent_result = process_request_sync(
            "Проанализируй требования для Python разработчика"
        )

        if agent_result["success"]:
            print("✅ Агент успешно обработал запрос")
            if (
                isinstance(agent_result["result"], dict)
                and "career_integration" in agent_result["result"]
            ):
                print("✅ Интеграция доступна через основной интерфейс")
            else:
                print("⚠️ Интеграция недоступна через основной интерфейс")
        else:
            print(f"❌ Ошибка агента: {agent_result['error']}")
            return False

        print("\n")

        # Восстановление исходного прогресса
        print("🔄 Восстановление исходного прогресса...")
        career_tracker.progress["completed_markers"] = original_completed
        career_tracker._save_progress()
        print("✅ Прогресс восстановлен")

        print("\n🎉 Все тесты пройдены успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        # Попытка восстановления прогресса в случае ошибки
        try:
            career_tracker.progress["completed_markers"] = original_completed
            career_tracker._save_progress()
            print("✅ Прогресс восстановлен после ошибки")
        except:
            print("❌ Не удалось восстановить прогресс")
        return False


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
