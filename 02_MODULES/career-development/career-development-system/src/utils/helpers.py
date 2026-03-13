import json
import os
from datetime import datetime


def load_json_file(filepath):
    """Загрузить данные из JSON файла"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {filepath} не найден")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filepath}")
        return None


def save_json_file(filepath, data):
    """Сохранить данные в JSON файл"""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения файла {filepath}: {e}")
        return False


def format_date(date_string):
    """Форматировать дату в читаемый формат"""
    try:
        date_obj = datetime.fromisoformat(date_string)
        return date_obj.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return date_string


def calculate_skill_progress(level, max_level=10):
    """Рассчитать процент прогресса навыка"""
    return min(100, max(0, (level / max_level) * 100))


def get_competency_level_name(level):
    """Получить название уровня компетенции"""
    levels = {1: "Новичок", 2: "Базовый", 3: "Средний", 4: "Продвинутый", 5: "Эксперт"}
    return levels.get(level, "Не определен")


def generate_unique_id():
    """Сгенерировать уникальный идентификатор"""
    import uuid

    return str(uuid.uuid4())


def validate_email(email):
    """Проверить валидность email"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def sanitize_filename(filename):
    """Очистить имя файла от недопустимых символов"""
    import re

    # Удаляем недопустимые символы
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Ограничиваем длину имени файла
    return sanitized[:255]


def create_directory_if_not_exists(directory_path):
    """Создать директорию, если она не существует"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return True
    return False


def get_file_size(filepath):
    """Получить размер файла в байтах"""
    try:
        return os.path.getsize(filepath)
    except FileNotFoundError:
        return 0


def convert_bytes_to_human_readable(bytes_size):
    """Конвертировать размер в байтах в человекочитаемый формат"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
