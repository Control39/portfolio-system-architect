"""Unit тесты для модуля async_helpers.
"""

import asyncio

import pytest

from src.common.async_helpers import (
    async_retry,
    async_timeout,
    batch_async_operations,
    fetch_parallel,
    fetch_parallel_safe,
    fetch_with_retry,
    fetch_with_timeout,
)


@pytest.mark.asyncio
async def test_fetch_parallel():
    """Тест параллельного выполнения задач"""
    async def task(n):
        await asyncio.sleep(0.1)
        return n * 2

    results = await fetch_parallel(task(1), task(2), task(3))

    assert results == [2, 4, 6]


@pytest.mark.asyncio
async def test_fetch_parallel_safe_with_errors():
    """Тест параллельного выполнения с обработкой ошибок"""
    async def passing_task():
        return "success"

    async def failing_task():
        raise ValueError("Task failed")

    results = await fetch_parallel_safe(
        passing_task(),
        failing_task(),
        passing_task(),
    )

    assert results[0] == "success"
    assert results[1] is None  # Ошибка обработана
    assert results[2] == "success"


@pytest.mark.asyncio
async def test_fetch_with_timeout_success():
    """Тест успешного выполнения с таймаутом"""
    async def quick_task():
        await asyncio.sleep(0.1)
        return "done"

    result = await fetch_with_timeout(quick_task(), timeout=1)

    assert result == "done"


@pytest.mark.asyncio
async def test_fetch_with_timeout_expired():
    """Тест таймаута"""
    async def slow_task():
        await asyncio.sleep(2)
        return "done"

    result = await fetch_with_timeout(slow_task(), timeout=0.5, default_value="timeout")

    assert result == "timeout"


@pytest.mark.asyncio
async def test_fetch_with_retry_success_first_attempt():
    """Тест retry успешно с первой попытки"""
    call_count = 0

    async def task():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await fetch_with_retry(lambda: task(), max_retries=3)

    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_fetch_with_retry_succeeds_on_second_attempt():
    """Тест retry успешно со второй попытки"""
    call_count = 0

    async def task():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("First attempt fails")
        return "success"

    result = await fetch_with_retry(
        lambda: task(),
        max_retries=3,
        base_delay=0.01,
        jitter=False,
    )

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_fetch_with_retry_exhausted():
    """Тест retry исчерпаны попытки"""
    call_count = 0

    async def task():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        await fetch_with_retry(
            lambda: task(),
            max_retries=3,
            base_delay=0.01,
            jitter=False,
        )

    assert call_count == 3


@pytest.mark.asyncio
async def test_batch_async_operations():
    """Тест batch операции"""
    async def multiply(n):
        await asyncio.sleep(0.05)
        return n * 2

    items = [1, 2, 3, 4, 5]
    results = await batch_async_operations(
        items,
        multiply,
        batch_size=2,
        delay_between_batches=0.01,
    )

    assert results == [2, 4, 6, 8, 10]


def test_async_timeout_decorator():
    """Тест декоратора async_timeout"""
    @async_timeout(1)
    async def quick_task():
        await asyncio.sleep(0.1)
        return "done"

    @async_timeout(0.1)
    async def slow_task():
        await asyncio.sleep(1)
        return "done"

    # Успешное выполнение
    result = asyncio.run(quick_task())
    assert result == "done"

    # Таймаут
    with pytest.raises(asyncio.TimeoutError):
        asyncio.run(slow_task())


def test_async_retry_decorator():
    """Тест декоратора async_retry"""
    call_count = 0

    @async_retry(max_retries=3, delay=0.01)
    async def flaky_task():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("First attempt fails")
        return "success"

    result = asyncio.run(flaky_task())

    assert result == "success"
    assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

