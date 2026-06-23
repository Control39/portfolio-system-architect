"""
Cache Module
Модуль кэширования для Cognitive Agent
"""

from .cache_core import (
    CacheEntry,
    BaseCache,
    FileCache,
    TTLCache,
    MemoryAwareCache,
    LRUCache,
    cached,
    global_cache,
    with_cache
)

from .cache_strategies import (
    CacheStrategy,
    LRUStrategy,
    FIFOStrategy,
    LFUStrategy,
    TTLStrategy,
    CacheStrategyFactory
)

from .cache_validators import (
    CacheValidator,
    SizeValidator,
    TypeValidator,
    HashValidator,
    PatternValidator,
    FileValidator,
    CustomValidator,
    CacheValidatorFactory,
    default_validator
)

__all__ = [
    'CacheEntry',
    'BaseCache',
    'FileCache',
    'TTLCache',
    'MemoryAwareCache',
    'LRUCache',
    'cached',
    'global_cache',
    'with_cache',
    'CacheStrategy',
    'LRUStrategy',
    'FIFOStrategy',
    'LFUStrategy',
    'TTLStrategy',
    'CacheStrategyFactory',
    'CacheValidator',
    'SizeValidator',
    'TypeValidator',
    'HashValidator',
    'PatternValidator',
    'FileValidator',
    'CustomValidator',
    'CacheValidatorFactory',
    'default_validator'
]
