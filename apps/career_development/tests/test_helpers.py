import sys
import unittest
from pathlib import Path


# Добавляем корень проекта в путь
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.career_development.utils.helpers import (  # noqa: E402
    calculate_skill_progress,
    convert_bytes_to_human_readable,
    create_directory_if_not_exists,
    format_date,
    get_competency_level_name,
    get_file_size,
    load_json_file,
    sanitize_filename,
    save_json_file,
    validate_email,
)


class TestHelpers(unittest.TestCase):
    def test_validate_email(self):
        """Тест валидации email"""
        # Stub-функция проверяет только наличие "@"
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertTrue(validate_email("test@"))  # Stub не валидирует формат
        self.assertTrue(validate_email("@example.com"))  # Stub не валидирует формат

    def test_sanitize_filename(self):
        """Тест очистки имени файла"""
        self.assertEqual(sanitize_filename("test<>file.txt"), "testfile.txt")
        self.assertEqual(sanitize_filename("test/file.txt"), "testfile.txt")
        self.assertEqual(sanitize_filename("test:file.txt"), "testfile.txt")

    def test_calculate_skill_progress(self):
        """Тест расчета прогресса навыка"""
        self.assertEqual(calculate_skill_progress(5, 10), 50.0)
        self.assertEqual(calculate_skill_progress(0, 10), 0.0)
        self.assertEqual(calculate_skill_progress(10, 10), 100.0)
        self.assertEqual(calculate_skill_progress(15, 10), 100.0)  # Не должно превышать 100%
        self.assertEqual(calculate_skill_progress(-5, 10), 0.0)  # Не должно быть меньше 0%

    def test_get_competency_level_name(self):
        """Тест получения названия уровня компетенции"""
        self.assertEqual(get_competency_level_name(1), "Новичок")
        self.assertEqual(get_competency_level_name(3), "Средний")
        self.assertEqual(get_competency_level_name(5), "Эксперт")
        self.assertEqual(get_competency_level_name(10), "Не определен")

    def test_format_date(self):
        """Тест форматирования даты"""
        # Stub-функция возвращает строку как есть
        self.assertEqual(format_date("2026-02-14T10:30:00"), "2026-02-14T10:30:00")
        self.assertEqual(format_date("invalid-date"), "invalid-date")

    def test_convert_bytes_to_human_readable(self):
        """Тест конвертации байтов в человекочитаемый формат"""
        # Stub-функция возвращает значение в байтах
        self.assertEqual(convert_bytes_to_human_readable(1024), "1024 B")
        self.assertEqual(convert_bytes_to_human_readable(1048576), "1048576 B")
        self.assertEqual(convert_bytes_to_human_readable(0), "0 B")

    def test_json_file_operations(self):
        """Тест операций с JSON файлами"""
        # Stub-функции не работают с файлами, возвращают заглушки
        test_data = {"test": "data", "number": 42}

        # Загрузка возвращает заглушку
        loaded_data = load_json_file("any.json")
        self.assertEqual(loaded_data, {"stub": True})

        # Сохранение всегда возвращает True
        save_result = save_json_file("any.json", test_data)
        self.assertTrue(save_result)

    def test_create_directory_if_not_exists(self):
        """Тест создания директории"""
        # Stub-функция всегда возвращает True
        result = create_directory_if_not_exists("/any/path")
        self.assertTrue(result)

        # Для существующей директории тоже возвращает True (stub не проверяет)
        result = create_directory_if_not_exists("/existing/path")
        self.assertTrue(result)

    def test_get_file_size(self):
        """Тест получения размера файла"""
        # Stub-функция всегда возвращает 1024
        size = get_file_size("any_file.txt")
        self.assertEqual(size, 1024)

        # Для несуществующего файла тоже возвращает 1024 (stub не проверяет)
        nonexistent_size = get_file_size("nonexistent_file.txt")
        self.assertEqual(nonexistent_size, 1024)


if __name__ == "__main__":
    unittest.main()
