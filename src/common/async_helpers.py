"""
Асинхронные утилиты для оптимизации асинхронного кода.

Предоставляет функции для:
- Параллельного выполнения задач
- Управления таймаутами
- Retry логики с exponential backoff
- Batch обработки
"""

import asyncio
import logging
from typing import List, Callable, Any, Optional, TypeVar, Coroutine
import random
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def fetch_parallel(*tasks: Coroutine) -> List[Any]:
    """
    Выполнить несколько async задач параллельно.
    
    Args:
        *tasks: Async функции или coroutines
    
    Returns:
        Список результатов в том же порядке
    
    Example:
        results = await fetch_parallel(
            fetch_user(1),
            fetch_user(2),
            fetch_user(3)
        )
    """
    try:
        return await asyncio.gather(*tasks, return_exceptions=False)
    except Exception as e:
        logger.error(f"Error in parallel execution: {e}")
        raise


async def fetch_parallel_safe(*tasks: Coroutine) -> List[Optional[Any]]:
    """
    Выполнить несколько async задач параллельно с обработкой ошибок.
    
    Отличие от fetch_parallel: не выбрасывает исключение при ошибке в одной из задач.
    Возвращает None для задач, которые выбросили исключение.
    
    Returns:
        Список результатов, где None указывает на ошибку
    """
    results = await asyncio.gather(*tasks, return_exceptions=True)
    processed = []
    
    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Task failed with error: {result}")
            processed.append(None)
        else:
            processed.append(result)
    
    return processed


async def fetch_with_timeout(
    coro: Coroutine,
    timeout: int = 30,
    default_value: Optional[Any] = None
) -> Any:
    """
    Выполнить async задачу с таймаутом.
    
    Args:
        coro: Coroutine для выполнения
        timeout: Таймаут в секундах
        default_value: Значение по умолчанию если таймаут истёк
    
    Returns:
        Результат выполнения или default_value при таймауте
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Task timed out after {timeout}s")
        return default_value


async def fetch_with_retry(
    coro_fn: Callable[[], Coroutine],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Any:
    """
    Выполнить async функцию с retry логикой (exponential backoff).
    
    Args:
        coro_fn: Функция, которая возвращает coroutine
        max_retries: Максимальное количество попыток
        base_delay: Базовая задержка в секундах
        max_delay: Максимальная задержка в секундах
        exponential_base: База для экспоненциального увеличения задержки
        jitter: Добавлять ли случайный jitter к задержке
    
    Returns:
        Результат успешного выполнения
    
    Raises:
        Последнее исключение если все попытки привели к ошибке
    
    Example:
        async def fetch_data():
            return await fetch_with_retry(
                lambda: http_client.get(url),
                max_retries=3
            )
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await coro_fn()
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise
            
            # Рассчитать задержку
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            
            # Добавить jitter (случайное отклонение)
            if jitter:
                delay *= (0.5 + random.random())
            
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            await asyncio.sleep(delay)
    
    raise last_exception


async def batch_async_operations(
    items: List[T],
    async_fn: Callable[[T], Coroutine],
    batch_size: int = 10,
    delay_between_batches: float = 0.1
) -> List[Any]:
    """
    Выполнить async операцию для списка элементов батчами.
    
    Полезно для rate-limited API или сервисов что требуют 
    ограничения количества одновременных запросов.
    
    Args:
        items: Список элементов для обработки
        async_fn: Async функция (принимает 1 элемент, возвращает результат)
        batch_size: Размер одного батча
        delay_between_batches: Задержка между батчами в секундах
    
    Returns:
        Список результатов в том же порядке что и items
    
    Example:
        users = await batch_async_operations(
            user_ids,
            fetch_user,
            batch_size=10,
            delay_between_batches=0.5
        )
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} items)")
        
        batch_results = await fetch_parallel(*[async_fn(item) for item in batch])
        results.extend(batch_results)
        
        # Добавить задержку между батчами (кроме последнего)
        if i + batch_size < len(items):
            await asyncio.sleep(delay_between_batches)
    
    return results


def async_timeout(seconds: int):
    """
    Декоратор для установки таймаута на async функции.
    
    Args:
        seconds: Таймаут в секундах
    
    Example:
        @async_timeout(30)
        async def fetch_data():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=seconds
            )
        return wrapper
    return decorator


def async_retry(max_retries: int = 3, delay: float = 1.0):
    """
    Декоратор для retry логики на async функциях.
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Задержка между попытками в секундах
    
    Example:
        @async_retry(max_retries=3, delay=2.0)
        async def fetch_data():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
