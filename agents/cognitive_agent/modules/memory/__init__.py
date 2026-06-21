"""
Модуль памяти для когнитивного агента
Долговременная и кратковременная память
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class MemoryManager:
    """Менеджер памяти"""

    def __init__(self, autonomous_agent):
        self.autonomous_agent = autonomous_agent
        self.project_path = autonomous_agent.project_path
        self.memory_path = self.project_path / ".agents" / "memory"

        # Создаем директории
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # Инициализация памяти
        self.long_term = LongTermMemory(self)
        self.short_term = ShortTermMemory(self)


class LongTermMemory:
    """Долговременная память"""

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.project_path = memory_manager.project_path
        self.long_term_path = self.project_path / ".agents" / "memory" / "long_term"

        # Создаем директории
        self.long_term_path.mkdir(parents=True, exist_ok=True)

        # Загружаем существующую память
        self.memory = self._load_memory()

    def _load_memory(self) -> dict[str, Any]:
        """Загрузка существующей памяти"""
        memory = {}
        memory_file = self.long_term_path / "memory.json"

        if memory_file.exists():
            try:
                with open(memory_file, encoding="utf-8") as f:
                    memory = json.load(f)
            except Exception:
                pass

        return memory

    def save_memory(self, key: str, value: dict[str, Any]) -> dict[str, Any]:
        """
        Сохранение памяти
        :param key: Ключ
        :param value: Значение
        :return: Результат сохранения
        """
        # Добавляем метаданные
        entry = {"key": key, "value": value, "timestamp": datetime.now().isoformat(), "version": 1}

        # Сохраняем
        self.memory[key] = entry

        # Сохраняем в файл
        memory_file = self.long_term_path / "memory.json"
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

        return {"saved": True, "key": key, "timestamp": entry["timestamp"]}

    def get_memory(self, key: str) -> dict[str, Any]:
        """
        Получение памяти по ключу
        :param key: Ключ
        :return: Значение
        """
        if key in self.memory:
            return self.memory[key]["value"]
        return {"error": f"Память {key} не найдена"}

    def delete_memory(self, key: str) -> dict[str, Any]:
        """
        Удаление памяти по ключу
        :param key: Ключ
        :return: Результат удаления
        """
        if key in self.memory:
            del self.memory[key]

            # Сохраняем изменения
            memory_file = self.long_term_path / "memory.json"
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)

            return {"deleted": True, "key": key}
        return {"deleted": False, "key": key, "error": "Память не найдена"}

    def get_all_memories(self) -> dict[str, Any]:
        """Получение всех памятей"""
        return self.memory

    def get_memories_by_pattern(self, pattern: str) -> list[dict[str, Any]]:
        """Получение памяти по шаблону ключа"""
        result = []
        for key, entry in self.memory.items():
            if pattern.lower() in key.lower():
                result.append({"key": key, "value": entry["value"], "timestamp": entry["timestamp"]})
        return result


class ShortTermMemory:
    """Кратковременная память"""

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.context = {}
        self.max_size = 100  # Максимальный размер

    def save_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Сохранение контекста
        :param context: Контекст
        :return: Результат сохранения
        """
        context_id = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Ограничиваем размер
        if len(self.context) >= self.max_size:
            self._evict_oldest()

        self.context[context_id] = {"id": context_id, "data": context, "timestamp": datetime.now().isoformat()}

        return {"saved": True, "context_id": context_id, "timestamp": self.context[context_id]["timestamp"]}

    def _evict_oldest(self) -> None:
        """Удаление самой старой записи"""
        if not self.context:
            return

        oldest_id = min(self.context.keys(), key=lambda k: self.context[k]["timestamp"])
        del self.context[oldest_id]

    def get_context(self) -> dict[str, Any]:
        """Получение текущего контекста"""
        return self.context

    def get_context_by_id(self, context_id: str) -> dict[str, Any]:
        """Получение контекста по ID"""
        if context_id in self.context:
            return self.context[context_id]["data"]
        return {"error": f"Контекст {context_id} не найден"}

    def clear_context(self) -> dict[str, Any]:
        """Очистка контекста"""
        self.context = {}
        return {"cleared": True, "previous_size": 0}

    def get_recent_contexts(self, count: int = 10) -> list[dict[str, Any]]:
        """Получение последних контекстов"""
        # Сортируем по времени и берем последние
        sorted_contexts = sorted(self.context.values(), key=lambda x: x["timestamp"], reverse=True)

        return [ctx["data"] for ctx in sorted_contexts[:count]]

    def update_context(self, context_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Обновление контекста"""
        if context_id in self.context:
            self.context[context_id]["data"].update(updates)
            self.context[context_id]["timestamp"] = datetime.now().isoformat()

            return {"updated": True, "context_id": context_id}
        return {"updated": False, "context_id": context_id, "error": "Контекст не найден"}


# Алиасы для удобства
Memory = LongTermMemory
Context = ShortTermMemory
