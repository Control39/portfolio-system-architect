"""
Тесты для трекера компетенций IT Compass
"""

import unittest
import json
import os
import tempfile
import sys
from datetime import datetime
from unittest.mock import patch, mock_open

# Добавляем путь к модулям IT Compass
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ..src.core.tracker import CompetencyTracker


class TestCompetencyTracker(unittest.TestCase):
    """Тесты для трекера компетенций"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временный файл для данных
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, 'test_user_progress.json')
        
        # Создаем тестовые данные
        self.test_data = {
            "user_id": "test_user",
            "completed_markers": ["python_basics", "git_fundamentals"],
            "last_updated": datetime.now().isoformat()
        }
        
        # Сохраняем тестовые данные
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=2)
        
        # Создаем трекер с временным файлом
        self.tracker = CompetencyTracker(self.data_file)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временные файлы
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_load_markers(self):
        """Тест загрузки маркеров навыков"""
        markers = self.tracker.load_markers()
        
        # Проверяем, что маркеры загружены
        self.assertIsInstance(markers, dict)
        self.assertGreater(len(markers), 0)
        
        # Проверяем структуру первого маркера
        first_marker_id = list(markers.keys())[0]
        first_marker = markers[first_marker_id]
        
        self.assertIn('name', first_marker)
        self.assertIn('description', first_marker)
        self.assertIn('category', first_marker)
        self.assertIn('difficulty', first_marker)
        self.assertIn('estimated_time', first_marker)
    
    def test_mark_completed(self):
        """Тест отметки маркера как выполненного"""
        marker_id = "python_basics"
        
        # Отмечаем маркер как выполненный
        result = self.tracker.mark_completed(marker_id)
        
        # Проверяем результат
        self.assertTrue(result)
        
        # Проверяем, что маркер добавлен в выполненные
        self.assertIn(marker_id, self.tracker.user_progress["completed_markers"])
        
        # Проверяем, что дата обновления обновлена
        self.assertIn("last_updated", self.tracker.user_progress)
    
    def test_is_completed(self):
        """Тест проверки выполнения маркера"""
        completed_marker = "python_basics"
        not_completed_marker = "advanced_algorithms"
        
        # Отмечаем один маркер как выполненный
        self.tracker.mark_completed(completed_marker)
        
        # Проверяем статус маркеров
        self.assertTrue(self.tracker.is_completed(completed_marker))
        self.assertFalse(self.tracker.is_completed(not_completed_marker))
    
    def test_get_statistics(self):
        """Тест получения статистики"""
        # Отмечаем несколько маркеров как выполненные
        self.tracker.mark_completed("python_basics")
        self.tracker.mark_completed("javascript_basics")
        self.tracker.mark_completed("docker_fundamentals")
        
        # Получаем статистику
        stats = self.tracker.get_statistics()
        
        # Проверяем структуру статистики
        self.assertIn("total_markers", stats)
        self.assertIn("completed_markers", stats)
        self.assertIn("completion_percentage", stats)
        self.assertIn("directions", stats)
        self.assertIn("last_updated", stats)
        
        # Проверяем значения
        self.assertGreater(stats["total_markers"], 0)
        self.assertEqual(stats["completed_markers"], 3)
        self.assertGreaterEqual(stats["completion_percentage"], 0)
        self.assertLessEqual(stats["completion_percentage"], 100)
    
    def test_get_direction_statistics(self):
        """Тест получения статистики по направлениям"""
        # Отмечаем маркеры из разных направлений
        self.tracker.mark_completed("python_basics")  # backend
        self.tracker.mark_completed("javascript_basics")  # frontend
        self.tracker.mark_completed("docker_fundamentals")  # devops
        
        # Получаем статистику по направлениям
        direction_stats = self.tracker.get_direction_statistics()
        
        # Проверяем структуру
        self.assertIsInstance(direction_stats, dict)
        self.assertGreater(len(direction_stats), 0)
        
        # Проверяем наличие ключевых направлений
        expected_directions = ["backend_development", "frontend_development", "devops"]
        for direction in expected_directions:
            self.assertIn(direction, direction_stats)
    
    def test_get_next_recommended_markers(self):
        """Тест получения рекомендованных маркеров"""
        # Отмечаем несколько маркеров как выполненные
        self.tracker.mark_completed("python_basics")
        self.tracker.mark_completed("git_fundamentals")
        
        # Получаем рекомендованные маркеры
        recommended = self.tracker.get_next_recommended_markers(count=5)
        
        # Проверяем структуру
        self.assertIsInstance(recommended, list)
        self.assertLessEqual(len(recommended), 5)
        
        # Проверяем, что рекомендованные маркеры не выполнены
        for marker_id in recommended:
            self.assertFalse(self.tracker.is_completed(marker_id))
    
    def test_get_skill_progress(self):
        """Тест получения прогресса по навыкам"""
        # Отмечаем несколько маркеров как выполненные
        self.tracker.mark_completed("python_basics")
        self.tracker.mark_completed("python_intermediate")
        
        # Получаем прогресс по навыку Python
        python_progress = self.tracker.get_skill_progress("Python")
        
        # Проверяем структуру
        self.assertIn("skill", python_progress)
        self.assertIn("completed_count", python_progress)
        self.assertIn("total_count", python_progress)
        self.assertIn("percentage", python_progress)
        self.assertIn("markers", python_progress)
        
        # Проверяем значения
        self.assertEqual(python_progress["skill"], "Python")
        self.assertGreaterEqual(python_progress["completed_count"], 0)
        self.assertGreater(python_progress["total_count"], 0)
    
    def test_save_progress(self):
        """Тест сохранения прогресса"""
        # Отмечаем несколько маркеров
        self.tracker.mark_completed("python_basics")
        self.tracker.mark_completed("javascript_basics")
        
        # Сохраняем прогресс
        result = self.tracker.save_progress()
        
        # Проверяем результат
        self.assertTrue(result)
        
        # Проверяем, что файл существует
        self.assertTrue(os.path.exists(self.data_file))
        
        # Загружаем данные и проверяем
        with open(self.data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertIn("completed_markers", saved_data)
        self.assertIn("python_basics", saved_data["completed_markers"])
        self.assertIn("last_updated", saved_data)
    
    def test_load_progress(self):
        """Тест загрузки прогресса"""
        # Создаем новые тестовые данные
        new_data = {
            "user_id": "test_user_2",
            "completed_markers": ["advanced_python", "machine_learning_basics"],
            "last_updated": datetime.now().isoformat()
        }
        
        # Сохраняем новые данные
        new_data_file = os.path.join(self.temp_dir, 'new_test_data.json')
        with open(new_data_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        # Загружаем прогресс
        self.tracker.load_progress(new_data_file)
        
        # Проверяем, что данные загружены
        self.assertIn("advanced_python", self.tracker.user_progress["completed_markers"])
        self.assertIn("machine_learning_basics", self.tracker.user_progress["completed_markers"])
    
    def test_get_completion_timeline(self):
        """Тест получения временной шкалы выполнения"""
        # Отмечаем маркеры в разное время (имитация)
        self.tracker.mark_completed("python_basics")
        self.tracker.mark_completed("javascript_basics")
        self.tracker.mark_completed("docker_fundamentals")
        
        # Получаем временную шкалу
        timeline = self.tracker.get_completion_timeline()
        
        # Проверяем структуру
        self.assertIsInstance(timeline, list)
        self.assertGreaterEqual(len(timeline), 3)
        
        # Проверяем структуру первого элемента
        if timeline:
            first_entry = timeline[0]
            self.assertIn("marker_id", first_entry)
            self.assertIn("completed_at", first_entry)
            self.assertIn("skill", first_entry)
    
    def test_get_skill_recommendations(self):
        """Тест получения рекомендаций по навыкам"""
        # Отмечаем несколько маркеров
        self.tracker.mark_completed("python_basics")
        self.tracker.mark_completed("git_fundamentals")
        
        # Получаем рекомендации
        recommendations = self.tracker.get_skill_recommendations()
        
        # Проверяем структуру
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Проверяем структуру первой рекомендации
        first_rec = recommendations[0]
        self.assertIn("skill", first_rec)
        self.assertIn("reason", first_rec)
        self.assertIn("next_steps", first_rec)
        self.assertIn("resources", first_rec)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)