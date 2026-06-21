"""
Memory Module
Модуль управления памятью для Cognitive Agent

Структура:
- memory_core.py: Базовые классы памяти (BaseMemory, ShortTermMemory, LongTermMemory, WorkingMemory)
- memory_strategies.py: Стратегии управления памятью (LRU, FIFO, LFU, Priority)
- memory_validators.py: Валидаторы памяти (Size, Type, Pattern, Custom)
"""

from .memory_core import BaseMemory, LongTermMemory, MemoryEntry, MemoryManager, ShortTermMemory, WorkingMemory
from .memory_strategies import (
    FIFOMemoryStrategy,
    LFUMemoryStrategy,
    LRUMemoryStrategy,
    MemoryStrategy,
    MemoryStrategyFactory,
    PriorityMemoryStrategy,
)
from .memory_validators import (
    CustomValidator,
    MemoryValidator,
    MemoryValidatorChain,
    MemoryValidatorFactory,
    PatternValidator,
    SizeValidator,
    TypeValidator,
)

__all__ = [
    # Core
    "MemoryEntry",
    "BaseMemory",
    "ShortTermMemory",
    "LongTermMemory",
    "WorkingMemory",
    "MemoryManager",
    # Strategies
    "MemoryStrategy",
    "LRUMemoryStrategy",
    "FIFOMemoryStrategy",
    "LFUMemoryStrategy",
    "PriorityMemoryStrategy",
    "MemoryStrategyFactory",
    # Validators
    "MemoryValidator",
    "SizeValidator",
    "TypeValidator",
    "PatternValidator",
    "CustomValidator",
    "MemoryValidatorFactory",
    "MemoryValidatorChain",
]
