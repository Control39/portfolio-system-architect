"""
Cache Validators Module
Валидаторы кэширования для Cognitive Agent
"""

import hashlib
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CacheValidator:
    """Базовый класс валидатора кэша"""

    def __init__(self, name: str = "base_validator"):
        """
        Инициализация валидатора

        Args:
            name: Имя валидатора
        """
        self.name = name

    def validate(self, key: str, value: Any) -> bool:
        """
        Валидировать запись кэша

        Args:
            key: Ключ записи
            value: Значение записи

        Returns:
            True, если валидация успешна, False иначе
        """
        return True

    def get_name(self) -> str:
        """Получить имя валидатора"""
        return self.name


class SizeValidator(CacheValidator):
    """Валидатор размера значения"""

    def __init__(self, max_size: int = 1024 * 1024, name: str = "size_validator"):
        """
        Инициализация валидатора размера

        Args:
            max_size: Максимальный размер в байтах (1 MB по умолчанию)
            name: Имя валидатора
        """
        super().__init__(name)
        self.max_size = max_size

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать размер значения"""
        try:
            size = len(str(value).encode("utf-8"))
            if size > self.max_size:
                logger.warning(f"Cache value too large: {key} ({size} bytes)")
                return False
            return True
        except Exception as e:
            logger.error(f"Error validating size for {key}: {e}")
            return False


class TypeValidator(CacheValidator):
    """Валидатор типа значения"""

    def __init__(self, allowed_types: list, name: str = "type_validator"):
        """
        Инициализация валидатора типа

        Args:
            allowed_types: Список разрешенных типов
            name: Имя валидатора
        """
        super().__init__(name)
        self.allowed_types = allowed_types

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать тип значения"""
        if any(isinstance(value, t) for t in self.allowed_types):
            return True
        logger.warning(f"Cache value has invalid type for {key}: {type(value)}")
        return False


class HashValidator(CacheValidator):
    """Валидатор целостности значения через хэш"""

    def __init__(self, name: str = "hash_validator"):
        """
        Инициализация валидатора хэша

        Args:
            name: Имя валидатора
        """
        super().__init__(name)
        self._hashes: dict[str, str] = {}

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать целостность значения"""
        value_hash = self._compute_hash(value)

        if key in self._hashes:
            if self._hashes[key] != value_hash:
                logger.warning(f"Cache value corrupted for {key}")
                return False

        self._hashes[key] = value_hash
        return True

    def _compute_hash(self, value: Any) -> str:
        """Вычислить хэш значения"""
        try:
            value_str = str(value)
            return hashlib.md5(value_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash: {e}")
            return ""

    def clear_hashes(self) -> None:
        """Очистить хэши"""
        self._hashes.clear()


class PatternValidator(CacheValidator):
    """Валидатор по паттерну"""

    def __init__(self, pattern: str, name: str = "pattern_validator"):
        """
        Инициализация валидатора паттерна

        Args:
            pattern: Регулярное выражение для валидации
            name: Имя валидатора
        """
        super().__init__(name)
        self.pattern = pattern
        self._compiled_pattern = None

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать значение по паттерну"""
        import re

        value_str = str(value)
        if self._compiled_pattern is None:
            try:
                self._compiled_pattern = re.compile(self.pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern: {e}")
                return False

        if self._compiled_pattern.match(value_str):
            return True
        logger.warning(f"Cache value doesn't match pattern for {key}")
        return False


class FileValidator(CacheValidator):
    """Валидатор файлов"""

    def __init__(self, allowed_extensions: list = None, name: str = "file_validator"):
        """
        Инициализация валидатора файлов

        Args:
            allowed_extensions: Список разрешенных расширений (None = все)
            name: Имя валидатора
        """
        super().__init__(name)
        self.allowed_extensions = allowed_extensions or []

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать значение как путь к файлу"""
        if not isinstance(value, (str, Path)):
            logger.warning(f"Cache value is not a path for {key}")
            return False

        file_path = Path(value)

        if not file_path.exists():
            logger.warning(f"Cache file doesn't exist: {file_path}")
            return False

        if self.allowed_extensions:
            if file_path.suffix.lower() not in [ext.lower() for ext in self.allowed_extensions]:
                logger.warning(f"Cache file has invalid extension: {file_path}")
                return False

        return True


class CustomValidator(CacheValidator):
    """Пользовательский валидатор"""

    def __init__(self, validator_func: Callable[[str, Any], bool], name: str = "custom_validator"):
        """
        Инициализация пользовательского валидатора

        Args:
            validator_func: Функция валидации (key, value) -> bool
            name: Имя валидатора
        """
        super().__init__(name)
        self.validator_func = validator_func

    def validate(self, key: str, value: Any) -> bool:
        """Валидировать с помощью пользовательской функции"""
        try:
            return self.validator_func(key, value)
        except Exception as e:
            logger.error(f"Error in custom validator for {key}: {e}")
            return False


# Фабрика валидаторов
class CacheValidatorFactory:
    """Фабрика для создания валидаторов"""

    @staticmethod
    def create(validator_type: str, **kwargs) -> CacheValidator:
        """
        Создать валидатор по типу

        Args:
            validator_type: Тип валидатора
            **kwargs: Параметры валидатора

        Returns:
            Экземпляр валидатора
        """
        validators = {
            "size": SizeValidator,
            "type": TypeValidator,
            "hash": HashValidator,
            "pattern": PatternValidator,
            "file": FileValidator,
            "custom": CustomValidator,
        }

        validator_class = validators.get(validator_type.lower())
        if validator_class is None:
            raise ValueError(f"Unknown validator type: {validator_type}")

        return validator_class(**kwargs)

    @staticmethod
    def get_available_validators() -> list:
        """Получить список доступных валидаторов"""
        return ["size", "type", "hash", "pattern", "file", "custom"]


# Глобальный валидатор по умолчанию
default_validator = SizeValidator(max_size=1024 * 1024)  # 1 MB
