"""
Cache Module
Модуль кэширования для Cognitive Agent
"""

from .cache_core import (
    BaseCache,
    CacheEntry,
    FileCache,
    LRUCache,
    MemoryAwareCache,
    TTLCache,
    cached,
    global_cache,
    with_cache,
)
from .cache_strategies import CacheStrategy, CacheStrategyFactory, FIFOStrategy, LFUStrategy, LRUStrategy, TTLStrategy
from .cache_validators import (
    CacheValidator,
    CacheValidatorFactory,
    CustomValidator,
    FileValidator,
    HashValidator,
    PatternValidator,
    SizeValidator,
    TypeValidator,
    default_validator,
)

__all__ = [
    "CacheEntry",
    "BaseCache",
    "FileCache",
    "TTLCache",
    "MemoryAwareCache",
    "LRUCache",
    "cached",
    "global_cache",
    "with_cache",
    "CacheStrategy",
    "LRUStrategy",
    "FIFOStrategy",
    "LFUStrategy",
    "TTLStrategy",
    "CacheStrategyFactory",
    "CacheValidator",
    "SizeValidator",
    "TypeValidator",
    "HashValidator",
    "PatternValidator",
    "FileValidator",
    "CustomValidator",
    "CacheValidatorFactory",
    "default_validator",
]
