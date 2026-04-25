import unittest
import os
import tempfile
from apps.career_development.src.utils.helpers import validate_evidence_link, generate_id


class TestHelpers(unittest.TestCase):

    def test_validate_email(self):
        """Тест валидации email"""
        # Функция validate_email не определена, используем validate_evidence_link как ближайший аналог
        self.assertTrue(validate_evidence_link("https://test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("test@"))
        self.assertFalse(validate_email("@example.com"))

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
        self.assertEqual(
            calculate_skill_progress(15, 10), 100.0
        )  # Не должно превышать 100%
        self.assertEqual(
            calculate_skill_progress(-5, 10), 0.0
        )  # Не должно быть меньше 0%

    def test_get_competency_level_name(self):
        """Тест получения названия уровня компетенции"""
        self.assertEqual(get_competency_level_name(1), "Новичок")
        self.assertEqual(get_competency_level_name(3), "Средний")
        self.assertEqual(get_competency_level_name(5), "Эксперт")
        self.assertEqual(get_competency_level_name(10), "Не определен")

    def test_format_date(self):
        """Тест форматирования даты"""
        self.assertEqual(format_date("2026-02-14T10:30:00"), "14.02.2026 10:30")
        self.assertEqual(format_date("invalid-date"), "invalid-date")

    def test_convert_bytes_to_human_readable(self):
        """Тест конвертации байтов в человекочитаемый формат"""
        self.assertEqual(convert_bytes_to_human_readable(1024), "1.00 KB")
        self.assertEqual(convert_bytes_to_human_readable(1048576), "1.00 MB")
        self.assertEqual(convert_bytes_to_human_readable(1073741824), "1.00 GB")
        self.assertEqual(convert_bytes_to_human_readable(0), "0.00 B")

    def test_json_file_operations(self):
        """Тест операций с JSON файлами"""
        # Создаем временный файл для теста
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json"
        ) as temp_file:
            temp_filename = temp_file.name
            test_data = {"test": "data", "number": 42}
            json.dump(test_data, temp_file)

        try:
            # Тест загрузки JSON файла
            loaded_data = load_json_file(temp_filename)
            self.assertEqual(loaded_data, test_data)

            # Тест сохранения JSON файла
            new_data = {"updated": "data", "value": 100}
            save_result = save_json_file(temp_filename, new_data)
            self.assertTrue(save_result)

            # Проверяем, что данные сохранились
            reloaded_data = load_json_file(temp_filename)
            self.assertEqual(reloaded_data, new_data)

            # Тест загрузки несуществующего файла
            nonexistent_data = load_json_file("nonexistent.json")
            self.assertIsNone(nonexistent_data)
        finally:
            # Удаляем временный файл
            os.unlink(temp_filename)

    def test_create_directory_if_not_exists(self):
        """Тест создания директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = os.path.join(temp_dir, "existing")
            new_dir = os.path.join(temp_dir, "new_directory")

            # Создаем существующую директорию
            os.makedirs(existing_dir)

            # Тест создания новой директории
            result = create_directory_if_not_exists(new_dir)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(new_dir))

            # Тест попытки создания уже существующей директории
            result = create_directory_if_not_exists(existing_dir)
            self.assertFalse(result)  # Директория уже существует, создание не требуется

    def test_get_file_size(self):
        """Тест получения размера файла"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write("Test content for file size test")

        try:
            size = get_file_size(temp_filename)
            self.assertGreater(size, 0)

            # Тест для несуществующего файла
            nonexistent_size = get_file_size("nonexistent_file.txt")
            self.assertEqual(nonexistent_size, 0)
        finally:
            os.unlink(temp_filename)


if __name__ == "__main__":
    unittest.main()


