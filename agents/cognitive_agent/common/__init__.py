"""
Модуль общих компонентов для Cognitive Agent
"""

# Импорты модуля utils (новая структура)
try:
    from .utils import calculate_file_hash, find_files_by_extension, format_bytes, load_json_file
except ImportError:
    # Заглушки для обратной совместимости
    def calculate_file_hash(*args, **kwargs):
        raise NotImplementedError("utils module not available")

    def load_json_file(*args, **kwargs):
        raise NotImplementedError("utils module not available")

    def find_files_by_extension(*args, **kwargs):
        raise NotImplementedError("utils module not available")

    def format_bytes(*args, **kwargs):
        raise NotImplementedError("utils module not available")


from .base_agent_extensions import BaseAgentExtensions
from .base_logger import BaseLogger, setup_logging
from .base_scanner import BaseProjectScanner
from .base_security import BaseSecurityChecker
from .exceptions import (
    AgentStateError,
    AIServiceError,
    AuditLogError,
    CacheError,
    CognitiveAgentError,
    ConfigurationError,
    DataProcessingError,
    ErrorHandler,
    FileOperationError,
    IntegrationError,
    NetworkError,
    ResourceExhaustionError,
    SecurityViolationError,
    TaskExecutionError,
    ValidationError,
    handle_errors,
    register_error_handler,
)

# Импорты кэширования (обратная совместимость)
try:
    from .cache import (
        BaseCache,
        CacheEntry,
        CacheStrategy,
        CacheStrategyFactory,
        CacheValidator,
        CacheValidatorFactory,
        CustomValidator,
        FIFOStrategy,
        FileCache,
        FileValidator,
        HashValidator,
        LFUStrategy,
        LRUCache,
        LRUStrategy,
        MemoryAwareCache,
        PatternValidator,
        SizeValidator,
        TTLCache,
        TTLStrategy,
        TypeValidator,
        cached,
        default_validator,
        global_cache,
    )

    # Импорты для обратной совместимости
    from .cache_manager import CacheManager, get_cache_manager, with_cache
except ImportError:
    # Если cache модуль не доступен, создать заглушки
    class CacheEntry:
        pass

    class BaseCache:
        pass

    class FileCache:
        pass

    class TTLCache:
        pass

    class MemoryAwareCache:
        pass

    class CacheManager:
        pass

    def get_cache_manager():
        return CacheManager()

    def with_cache(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


from .memory_manager import LazyLoader, MemoryManager, MemoryMonitor, get_memory_manager, with_memory_limit
from .pattern_analyzer import AdaptiveLearningSystem, PatternAnalyzer

# Импортировать компоненты графа знаний, если они доступны
try:
    from ..knowledge_graph import (
        KnowledgeGraphEdge,
        KnowledgeGraphIntegrator,
        KnowledgeGraphManager,
        KnowledgeGraphNode,
    )
except ImportError:
    # Если модуль knowledge_graph не доступен, создать заглушки
    class KnowledgeGraphNode:
        pass

    class KnowledgeGraphEdge:
        pass

    class KnowledgeGraphManager:
        pass

    class KnowledgeGraphIntegrator:
        pass


__all__ = [
    # Базовый логгер
    "BaseLogger",
    "setup_logging",
    # Базовый проверяльщик безопасности
    "BaseSecurityChecker",
    # Базовый сканер проекта
    "BaseProjectScanner",
    # Базовые расширения агента
    "BaseAgentExtensions",
    # Утилиты
    "calculate_file_hash",
    "load_json_file",
    "find_files_by_extension",
    "format_bytes",
    # Исключения и обработчик ошибок
    "CognitiveAgentError",
    "ConfigurationError",
    "SecurityViolationError",
    "ResourceExhaustionError",
    "AIServiceError",
    "FileOperationError",
    "NetworkError",
    "ValidationError",
    "TaskExecutionError",
    "IntegrationError",
    "AgentStateError",
    "DataProcessingError",
    "CacheError",
    "AuditLogError",
    "ErrorHandler",
    "handle_errors",
    "register_error_handler",
    # Компоненты кэширования
    "CacheEntry",
    "BaseCache",
    "FileCache",
    "TTLCache",
    "MemoryAwareCache",
    "LRUCache",
    "cached",
    "global_cache",
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
    "CacheManager",
    "get_cache_manager",
    "with_cache",
    # Компоненты управления памятью
    "MemoryMonitor",
    "MemoryManager",
    "LazyLoader",
    "get_memory_manager",
    "with_memory_limit",
    # Компоненты анализа паттернов и адаптивного обучения
    "PatternAnalyzer",
    "AdaptiveLearningSystem",
    # Компоненты графа знаний
    "KnowledgeGraphNode",
    "KnowledgeGraphEdge",
    "KnowledgeGraphManager",
    "KnowledgeGraphIntegrator",
]
