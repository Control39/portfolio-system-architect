"""
Базовые проверки безопасности для Cognitive Agent
"""

import re
from pathlib import Path


class BaseSecurityChecker:
    """
    Базовый класс проверки безопасности для Cognitive Agent
    """

    def __init__(self):
        """
        Инициализировать базовые проверки безопасности
        """
        # Опасные паттерны для валидации команд
        self.dangerous_command_patterns = [
            r"\brm\s+-rf\b",  # Удаление файлов
            r"\bmv\s+\S+\s+/\b",  # Перемещение в корень
            r"\bchmod\s+777\b",  # Установка максимальных прав
            r"\bchown\s+root\b",  # Смена владельца на root
            r"\bnc\s+.*-e\b",  # Netcat с выполнением команд
            r"\bwget\s+.*-O\s+/dev/null\b",  # Wget с подозрительным выводом
            r"\bcurl\s+.*|.*sh\b",  # Curl с передачей в shell
        ]

        # Опасные паттерны для валидации путей
        self.dangerous_path_patterns = [
            r"\.\./",  # Попытка выхода из директории
            r"\.\.\\",  # Та же проверка для Windows
            r"^/etc/",  # Доступ к системным файлам Linux
            r"^C:\\Windows\\",  # Доступ к системным файлам Windows
            r"\.ssh/",  # Доступ к SSH ключам
            r"\.aws/",  # Доступ к AWS конфигурации
        ]

        # Опасные паттерны для валидации кода
        self.dangerous_code_patterns = [
            r"\beval\s*\(",  # Вызов eval
            r"\bexec\s*\(",  # Вызов exec
            r"\bos\.system\s*\(",  # Системные вызовы
            r"\bsubprocess\.call\s*\(",  # Вызов subprocess
            r"\bopen\s*\([^)]*/etc/",  # Открытие системных файлов
            r"\bimportlib\.import_module\s*\(",  # Динамический импорт
        ]

        # Критические файлы для проверки
        self.critical_files = [
            "requirements.txt",
            "setup.py",
            "Dockerfile",
            "docker-compose.yml",
            "package.json",
            "webpack.config.js",
            ".env",
            "config.json",
            "settings.py",
            "__init__.py",
        ]

    def validate_command(self, command: str) -> tuple[bool, str]:
        """
        Проверить команду на безопасность

        Args:
            command: Команда для проверки

        Returns:
            Кортеж (безопасно ли, сообщение об ошибке)
        """
        for pattern in self.dangerous_command_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Обнаружен опасный паттерн в команде: {pattern}"

        return True, "Команда безопасна"

    def validate_path(self, path: str) -> tuple[bool, str]:
        """
        Проверить путь к файлу на безопасность

        Args:
            path: Путь для проверки

        Returns:
            Кортеж (безопасно ли, сообщение об ошибке)
        """
        path_obj = Path(path).resolve()

        # Проверить на опасные паттерны
        for pattern in self.dangerous_path_patterns:
            if re.search(pattern, str(path_obj), re.IGNORECASE):
                return False, f"Обнаружен опасный паттерн в пути: {pattern}"

        # Проверить, что путь находится в пределах разрешенной директории
        # (обычно это рабочая директория проекта)
        try:
            # Получить абсолютный путь к рабочей директории
            project_root = Path.cwd().resolve()

            # Попробовать получить относительный путь - если невозможно, значит путь вне проекта
            path_obj.relative_to(project_root)
        except ValueError:
            return False, f"Путь {path} находится вне разрешенной директории проекта"

        return True, "Путь безопасен"

    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        Проверить код на безопасность

        Args:
            code: Код для проверки

        Returns:
            Кортеж (безопасно ли, сообщение об ошибке)
        """
        for pattern in self.dangerous_code_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Обнаружен опасный паттерн в коде: {pattern}"

        return True, "Код безопасен"

    def is_critical_file(self, file_path: str) -> bool:
        """
        Проверить, является ли файл критическим

        Args:
            file_path: Путь к файлу

        Returns:
            Является ли файл критическим
        """
        file_name = Path(file_path).name
        return file_name in self.critical_files

    def validate_file_modification(self, file_path: str, modification_type: str) -> tuple[bool, str]:
        """
        Проверить разрешение на изменение файла

        Args:
            file_path: Путь к файлу
            modification_type: Тип изменения ('read', 'write', 'delete', 'execute')

        Returns:
            Кортеж (разрешено ли, сообщение)
        """
        if self.is_critical_file(file_path) and modification_type in ["write", "delete"]:
            return False, f"Изменение критического файла {file_path} требует подтверждения"

        # Проверить путь на безопасность
        is_safe, message = self.validate_path(file_path)
        if not is_safe:
            return False, message

        return True, "Изменение файла разрешено"

    def sanitize_input(self, input_str: str) -> str:
        """
        Санитизировать входные данные

        Args:
            input_str: Входная строка

        Returns:
            Очищенная строка
        """
        # Удалить потенциально опасные символы
        sanitized = input_str.replace("\0", "")  # Удалить null-байты
        sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")  # Нормализовать переносы строк

        return sanitized
