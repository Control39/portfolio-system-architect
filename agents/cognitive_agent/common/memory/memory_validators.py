"""
Memory Validators Module
Валидаторы памяти для Cognitive Agent
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class MemoryValidator(ABC):
    """Базовый класс валидатора памяти"""

    @abstractmethod
    def name(self) -> str:
        """Название валидатора"""
        pass

    @abstractmethod
    def validate(self, key: str, value: Any) -> bool:
        """
        Валидировать запись

        Args:
            key: Ключ
            value: Значение

        Returns:
            True, если валидно
        """
        pass

    @abstractmethod
    def get_error_message(self) -> str:
        """Получить сообщение об ошибке"""
        pass


class SizeValidator(MemoryValidator):
    """Валидатор размера значения"""

    def __init__(self, max_size: int = 1024 * 1024, min_size: int = 0):
        """
        Инициализация валидатора размера

        Args:
            max_size: Максимальный размер в байтах
            min_size: Минимальный размер в байтах
        """
        self.max_size = max_size
        self.min_size = min_size
        self._error_message = ""

    def name(self) -> str:
        return "size"

    def validate(self, key: str, value: Any) -> bool:
        try:
            size = len(str(value))
            if self.min_size <= size <= self.max_size:
                return True
            self._error_message = f"Size {size} out of range [{self.min_size}, {self.max_size}]"
            return False
        except TypeError:
            self._error_message = f"Value cannot be measured: {type(value)}"
            return False

    def get_error_message(self) -> str:
        return self._error_message


class TypeValidator(MemoryValidator):
    """Валидатор типа значения"""

    def __init__(self, allowed_types: list[type] = None):
        """
        Инициализация валидатора типа

        Args:
            allowed_types: Список разрешенных типов
        """
        self.allowed_types = allowed_types or [str, int, float, bool, dict, list]
        self._error_message = ""

    def name(self) -> str:
        return "type"

    def validate(self, key: str, value: Any) -> bool:
        if any(isinstance(value, t) for t in self.allowed_types):
            return True
        self._error_message = (
            f"Type {type(value).__name__} not in allowed types: {[t.__name__ for t in self.allowed_types]}"
        )
        return False

    def get_error_message(self) -> str:
        return self._error_message


class PatternValidator(MemoryValidator):
    """Валидатор ключа по паттерну"""

    def __init__(self, pattern: str = r"^[a-zA-Z][a-zA-Z0-9_]*$"):
        """
        Инициализация валидатора паттерна

        Args:
            pattern: Регулярное выражение для ключа
        """
        self.pattern = re.compile(pattern)
        self._error_message = ""

    def name(self) -> str:
        return "pattern"

    def validate(self, key: str, value: Any) -> bool:
        if self.pattern.match(key):
            return True
        self._error_message = f"Key '{key}' does not match pattern '{self.pattern.pattern}'"
        return False

    def get_error_message(self) -> str:
        return self._error_message


class CustomValidator(MemoryValidator):
    """Пользовательский валидатор"""

    def __init__(self, validate_func: Callable[[str, Any], bool], name: str = "custom"):
        """
        Инициализация пользовательского валидатора

        Args:
            validate_func: Функция валидации
            name: Имя валидатора
        """
        self.validate_func = validate_func
        self._name = name
        self._error_message = ""

    def name(self) -> str:
        return self._name

    def validate(self, key: str, value: Any) -> bool:
        try:
            result = self.validate_func(key, value)
            if result:
                return True
            self._error_message = "Custom validation failed"
            return False
        except Exception as e:
            self._error_message = f"Custom validation error: {e}"
            return False

    def get_error_message(self) -> str:
        return self._error_message


class MemoryValidatorFactory:
    """Фабрика валидаторов памяти"""

    _validators: dict[str, type] = {
        "size": SizeValidator,
        "type": TypeValidator,
        "pattern": PatternValidator,
        "custom": CustomValidator,
    }

    @classmethod
    def create(cls, validator_name: str, **kwargs) -> MemoryValidator:
        """
        Создать валидатор по имени

        Args:
            validator_name: Имя валидатора
            **kwargs: Аргументы для конструктора

        Returns:
            Экземпляр валидатора

        Raises:
            ValueError: Если валидатор не найден
        """
        validator_name = validator_name.lower()

        if validator_name not in cls._validators:
            raise ValueError(
                f"Unknown memory validator: {validator_name}. " f"Available: {list(cls._validators.keys())}"
            )

        return cls._validators[validator_name](**kwargs)

    @classmethod
    def get_available_validators(cls) -> list[str]:
        """Получить список доступных валидаторов"""
        return list(cls._validators.keys())

    @classmethod
    def register_validator(cls, name: str, validator_class: type) -> None:
        """
        Зарегистрировать новый валидатор

        Args:
            name: Имя валидатора
            validator_class: Класс валидатора
        """
        cls._validators[name.lower()] = validator_class


class MemoryValidatorChain:
    """Цепочка валидаторов"""

    def __init__(self):
        """Инициализация цепочки валидаторов"""
        self._validators: list[MemoryValidator] = []

    def add(self, validator: MemoryValidator) -> "MemoryValidatorChain":
        """
        Добавить валидатор в цепочку

        Args:
            validator: Валидатор

        Returns:
            self для цепочки вызовов
        """
        self._validators.append(validator)
        return self

    def validate(self, key: str, value: Any) -> bool:
        """
        Валидировать через цепочку

        Args:
            key: Ключ
            value: Значение

        Returns:
            True, если все валидаторы прошли
        """
        return all(validator.validate(key, value) for validator in self._validators)

    def get_first_error(self) -> str | None:
        """
        Получить первое сообщение об ошибке

        Returns:
            Сообщение об ошибке или None
        """
        for validator in self._validators:
            if not validator.validate("", None):  # Пробная валидация
                return validator.get_error_message()
        return None

    def validate_all(self, entries: dict[str, Any]) -> dict[str, bool]:
        """
        Валидировать несколько записей

        Args:
            entries: Словарь ключ-значение

        Returns:
            Словарь ключ-валидность
        """
        return {key: self.validate(key, value) for key, value in entries.items()}


__all__ = [
    "MemoryValidator",
    "SizeValidator",
    "TypeValidator",
    "PatternValidator",
    "CustomValidator",
    "MemoryValidatorFactory",
    "MemoryValidatorChain",
]
