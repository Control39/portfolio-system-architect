#!/usr/bin/env python3
"""
Скрипт интеграции Reasoning-модели с IT Compass.
Позволяет анализировать заметки/диалоги и автоматически сопоставлять с маркерами.
"""
import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add the project root to the path to allow imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.tracker import CareerTracker
from src.utils.portfolio_gen import PortfolioGenerator


class ReasoningIntegrator:
    def __init__(self, tracker: CareerTracker):
        self.tracker = tracker
        self.reasoning_api_url = os.getenv(
            "REASONING_API_URL", "https://api.openai.com/v1/chat/completions"
        )
        self.reasoning_api_key = os.getenv("REASONING_API_KEY")
        self.reasoning_model = os.getenv("REASONING_MODEL", "gpt-4")

    def analyze_notes_with_reasoning(self, notes_content: str) -> List[Dict]:
        """
        Отправляет содержимое заметок в reasoning-модель для анализа
        и возвращает список найденных маркеров.
        """
        if not self.reasoning_api_key:
            print("⚠️ REASONING_API_KEY не установлен. Используем симуляцию.")
            return self._simulate_reasoning_analysis(notes_content)

        # Подготовка промпта для reasoning-модели
        markers_text = self._get_all_markers_text()

        prompt = f"""
        Ты - аналитик, специализирующийся на оценке IT-компетенций.
        Ниже приведены фрагменты текста (заметки/диалоги), извлеченные из архива пользователя.

        Твоя задача:
        1. Внимательно проанализировать каждый фрагмент текста.
        2. Найти упоминания конкретных действий, решений, анализа, проектирования, написания кода, архитектурных решений и т.д.
        3. Сопоставить найденные действия/знания с маркерами компетенций IT Compass.
        4. Вывести результат в формате JSON: список объектов, где каждый объект имеет следующую структуру:
           - "matched_marker_id": "ID маркера (например, 'python_1_1')",
           - "context_snippet": "Точный фрагмент текста, на котором основано сопоставление",
           - "confidence": "Уверенность в сопоставлении (низкая/средняя/высокая)",
           - "comment": "Краткий комментарий, объясняющий, почему это сопоставление было сделано."

        ВАЖНО: Вывод должен быть строго в формате JSON, без дополнительного текста до или после. Если совпадений не найдено, верни пустой список [].

        Список маркеров IT Compass:
        {markers_text}

        Заметки/диалоги для анализа:
        {notes_content}
        """

        payload = {
            "model": self.reasoning_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Низкая температура для более детерминированного вывода
        }

        headers = {
            "Authorization": f"Bearer {self.reasoning_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.reasoning_api_url, json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            reasoning_output_text = data["choices"][0]["message"]["content"].strip()

            # Попробуем извлечь JSON из ответа
            start_idx = reasoning_output_text.find("[")
            end_idx = reasoning_output_text.rfind("]") + 1
            if start_idx != -1 and end_idx != 0:
                json_str = reasoning_output_text[start_idx:end_idx]
                try:
                    reasoning_output_json = json.loads(json_str)
                    return reasoning_output_json
                except json.JSONDecodeError as e:
                    print(f"Ошибка парсинга JSON из ответа Reasoning API: {e}")
                    print("Ответ API:")
                    print(reasoning_output_text)
                    return []
            else:
                print("Не удалось найти JSON в ответе Reasoning API.")
                print("Ответ API:")
                print(reasoning_output_text)
                return []

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при вызове Reasoning API: {e}")
            return []

    def _simulate_reasoning_analysis(self, notes_content: str) -> List[Dict]:
        """
        Симуляция анализа reasoning-моделью для демонстрации.
        """
        print("Симуляция анализа...")

        # Найдем возможные совпадения в тексте
        found_markers = []

        # Простой поиск по ключевым словам
        if "python" in notes_content.lower() or "script" in notes_content.lower():
            for skill_data in self.tracker.markers.values():
                for level_markers in skill_data.levels.values():
                    for marker in level_markers:
                        if (
                            "python" in marker.marker.lower()
                            or "script" in marker.marker.lower()
                        ):
                            found_markers.append(
                                {
                                    "matched_marker_id": marker.id,
                                    "context_snippet": notes_content[:200] + "...",
                                    "confidence": "средняя",
                                    "comment": "Найдено упоминание Python/скрипта в заметках",
                                }
                            )
                            break  # Добавим только первый найденный маркер для демонстрации

        return found_markers

    def _get_all_markers_text(self) -> str:
        """Возвращает текстовое представление всех маркеров для промпта."""
        markers_text = []
        for skill_name, skill_data in self.tracker.markers.items():
            markers_text.append(f"\n{skill_name}:")
            for level, level_markers in skill_data.levels.items():
                for marker in level_markers:
                    markers_text.append(f"  - {marker.id}: {marker.marker}")

        return "\n".join(markers_text)

    def process_notes_file(self, file_path: str) -> List[Dict]:
        """Обрабатывает один файл с заметками."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return self.analyze_notes_with_reasoning(content)
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")
            return []

    def process_notes_directory(self, directory_path: str) -> List[Dict]:
        """Обрабатывает все файлы в директории с заметками."""
        all_matches = []

        directory = Path(directory_path)
        if not directory.exists():
            print(f"Директория {directory_path} не существует")
            return []

        # Обработка всех текстовых файлов в директории
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [
                ".txt",
                ".md",
                ".json",
                ".py",
                ".js",
                ".html",
                ".css",
            ]:
                print(f"Обработка файла: {file_path}")
                matches = self.process_notes_file(str(file_path))
                all_matches.extend(matches)

        return all_matches

    def apply_matches_to_tracker(self, matches: List[Dict]) -> Dict:
        """Применяет найденные совпадения к трекеру и возвращает статистику."""
        results = {"applied": 0, "skipped": 0, "errors": 0}

        for match in matches:
            marker_id = match.get("matched_marker_id")
            if not marker_id:
                results["errors"] += 1
                continue

            # Проверим, существует ли маркер
            if self._marker_exists(marker_id):
                # Проверим, не отмечен ли он уже
                if marker_id not in self.tracker.progress["completed_markers"]:
                    success = self.tracker.mark_completed(marker_id)
                    if success:
                        results["applied"] += 1
                        print(f"✅ Маркер {marker_id} отмечен как выполненный")
                    else:
                        results["errors"] += 1
                else:
                    results["skipped"] += 1
            else:
                results["errors"] += 1

        return results

    def _marker_exists(self, marker_id: str) -> bool:
        """Проверяет, существует ли маркер в системе."""
        for skill_data in self.tracker.markers.values():
            for level_markers in skill_data.levels.values():
                for marker in level_markers:
                    if marker.id == marker_id:
                        return True
        return False


def main():
    print("🚀 Запуск интеграции Reasoning-модели с IT Compass")
    print("=" * 60)

    # Инициализация трекера
    tracker = CareerTracker()
    integrator = ReasoningIntegrator(tracker)

    # Показать текущий прогресс
    print("\n📊 ТЕКУЩИЙ ПРОГРЕСС:")
    tracker.show_progress()

    print("\n🔍 Введите путь к файлу или директории с заметками для анализа")
    print("Пример: /path/to/notes/directory или /path/to/note.txt")
    print("Для использования примера введите 'demo':")

    user_input = input("Путь: ").strip()

    if user_input.lower() == "demo":
        # Демонстрационный пример
        demo_content = """
        Сегодня я написал скрипт на Python для автоматизации рутинной задачи.
        Также решил несколько задач на Codewars и создал веб-приложение с использованием Flask.
        Работал с Docker для контейнеризации приложения.
        """
        print("\n📝 Анализ демонстрационного контента...")
        matches = integrator.analyze_notes_with_reasoning(demo_content)
    elif Path(user_input).is_file():
        print(f"\n📝 Анализ файла {user_input}...")
        matches = integrator.process_notes_file(user_input)
    elif Path(user_input).is_dir():
        print(f"\n📝 Анализ директории {user_input}...")
        matches = integrator.process_notes_directory(user_input)
    else:
        print("❌ Указанный путь не существует")
        return

    print(f"\n🎯 Найдено {len(matches)} потенциальных совпадений")

    if matches:
        print("\n📋 НАЙДЕННЫЕ СОВПАДЕНИЯ:")
        for i, match in enumerate(matches, 1):
            print(f"{i}. Маркер: {match.get('matched_marker_id', 'N/A')}")
            print(f"   Контекст: {match.get('context_snippet', 'N/A')[:100]}...")
            print(f"   Уверенность: {match.get('confidence', 'N/A')}")
            print(f"   Комментарий: {match.get('comment', 'N/A')}")
            print()

        print("✅ Применение совпадений к трекеру...")
        results = integrator.apply_matches_to_tracker(matches)

        print(f"\n📊 РЕЗУЛЬТАТЫ ПРИМЕНЕНИЯ:")
        print(f"  - Применено: {results['applied']}")
        print(f"  - Пропущено (уже отмечены): {results['skipped']}")
        print(f"  - Ошибок: {results['errors']}")

    # Показать обновленный прогресс
    print("\n📊 ОБНОВЛЕННЫЙ ПРОГРЕСС:")
    tracker.show_progress()

    # Сгенерировать новое портфолио
    print("\n📄 Генерация обновленного портфолио...")
    generator = PortfolioGenerator()
    success = generator.generate_portfolio()

    if success:
        print("✅ Портфолио успешно обновлено!")
    else:
        print("⚠️ Ошибка при генерации портфолио")


if __name__ == "__main__":
    main()
