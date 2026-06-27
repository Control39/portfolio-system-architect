#!/usr/bin/env python3
"""
Tests for RateLimiter module
Тесты для модуля rate limiting
"""

import sys
import time
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_rate_limiter_sliding_window():
    """Тест rate limiter со sliding window стратегией"""
    print("\n🧪 Тест 1: Sliding Window Rate Limiter")
    print("=" * 50)

    from agents.cognitive_agent.security.rate_limiter import (
        RateLimiter,
        RateLimitConfig,
        RateLimitStrategy,
        RateLimitExceededError,
    )

    # Конфигурация: 5 вызовов за 2 секунды
    limiter = RateLimiter(
        RateLimitConfig(
            max_calls=5,
            period_seconds=2,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )
    )

    # Тест 1.1: Первые 5 вызовов должны пройти
    for i in range(5):
        limiter.check_rate_limit("test_key")
        print(f"  ✅ Call {i+1} allowed")

    # Тест 1.2: 6-й вызов должен быть заблокирован
    try:
        limiter.check_rate_limit("test_key")
        print("  ❌ 6th call not blocked!")
        assert False, "Should have raised RateLimitExceededError"
    except RateLimitExceededError as e:
        print(f"  ✅ 6th call blocked: {e}")

    # Тест 1.3: После ожидания окно должно сдвинуться
    print("  ⏳ Waiting 2.5 seconds...")
    time.sleep(2.5)

    try:
        limiter.check_rate_limit("test_key")
        print("  ✅ Call allowed after window reset")
    except RateLimitExceededError:
        print("  ❌ Call not allowed after window reset!")

    # Тест 1.4: get_remaining_calls
    limiter.reset("test_key")
    remaining = limiter.get_remaining_calls("test_key")
    assert remaining == 5, f"Expected 5 remaining, got {remaining}"
    print(f"  ✅ Remaining calls after reset: {remaining}")

    print("  ✅ Тест 1 пройден\n")


def test_rate_limiter_fixed_window():
    """Тест rate limiter с fixed window стратегией"""
    print("\n🧪 Тест 2: Fixed Window Rate Limiter")
    print("=" * 50)

    from agents.cognitive_agent.security.rate_limiter import (
        RateLimiter,
        RateLimitConfig,
        RateLimitStrategy,
        RateLimitExceededError,
    )

    # Конфигурация: 3 вызова за 2 секунды
    limiter = RateLimiter(
        RateLimitConfig(
            max_calls=3,
            period_seconds=2,
            strategy=RateLimitStrategy.FIXED_WINDOW,
        )
    )

    # Тест 2.1: Первые 3 вызова
    for i in range(3):
        limiter.check_rate_limit("fixed_test")
        print(f"  ✅ Call {i+1} allowed")

    # Тест 2.2: 4-й вызов заблокирован
    try:
        limiter.check_rate_limit("fixed_test")
        print("  ❌ 4th call not blocked!")
    except RateLimitExceededError:
        print("  ✅ 4th call blocked")

    print("  ✅ Тест 2 пройден\n")


def test_rate_limiter_token_bucket():
    """Тест rate limiter с token bucket стратегией"""
    print("\n🧪 Тест 3: Token Bucket Rate Limiter")
    print("=" * 50)

    from agents.cognitive_agent.security.rate_limiter import (
        RateLimiter,
        RateLimitConfig,
        RateLimitStrategy,
        RateLimitExceededError,
    )

    # Конфигурация: bucket на 5 токенов, пополнение 1 токен в секунду
    limiter = RateLimiter(
        RateLimitConfig(
            max_calls=5,
            period_seconds=5,
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            burst_size=5,
        )
    )

    # Тест 3.1: Burst - первые 5 вызовов
    for i in range(5):
        limiter.check_rate_limit("burst_test")
        print(f"  ✅ Burst call {i+1} allowed")

    # Тест 3.2: 6-й вызов заблокирован
    try:
        limiter.check_rate_limit("burst_test")
        print("  ❌ 6th burst call not blocked!")
    except RateLimitExceededError:
        print("  ✅ 6th burst call blocked")

    # Тест 3.3: После ожидания токены должны пополниться
    print("  ⏳ Waiting 2 seconds for token refill...")
    time.sleep(2)

    try:
        limiter.check_rate_limit("burst_test")
        print("  ✅ Call allowed after token refill")
    except RateLimitExceededError:
        print("  ❌ Call not allowed after token refill!")

    print("  ✅ Тест 3 пройден\n")


def test_predefined_rate_limiters():
    """Тест предустановленных rate limiter конфигураций"""
    print("\n🧪 Тест 4: Predefined Rate Limiters")
    print("=" * 50)

    from agents.cognitive_agent.security.rate_limiter import PredefinedRateLimiters

    # Тест 4.1: AI calls limiter
    ai_limiter = PredefinedRateLimiters.ai_calls()
    assert ai_limiter.config.max_calls == 50
    assert ai_limiter.config.period_seconds == 3600
    print(f"  ✅ AI calls limiter: {ai_limiter.config.max_calls} calls / {ai_limiter.config.period_seconds}s")

    # Тест 4.2: File operations limiter
    file_limiter = PredefinedRateLimiters.file_operations()
    assert file_limiter.config.max_calls == 100
    assert file_limiter.config.period_seconds == 60
    print(f"  ✅ File ops limiter: {file_limiter.config.max_calls} calls / {file_limiter.config.period_seconds}s")

    # Тест 4.3: Scan operations limiter
    scan_limiter = PredefinedRateLimiters.scan_operations()
    assert scan_limiter.config.max_calls == 10
    assert scan_limiter.config.period_seconds == 60
    print(f"  ✅ Scan ops limiter: {scan_limiter.config.max_calls} calls / {scan_limiter.config.period_seconds}s")

    # Тест 4.4: API requests limiter
    api_limiter = PredefinedRateLimiters.api_requests()
    assert api_limiter.config.max_calls == 1000
    assert api_limiter.config.period_seconds == 3600
    print(f"  ✅ API requests limiter: {api_limiter.config.max_calls} calls / {api_limiter.config.period_seconds}s")

    print("  ✅ Тест 4 пройден\n")


def test_rate_limit_decorator():
    """Тест декоратора rate_limited"""
    print("\n🧪 Тест 5: Rate Limit Decorator")
    print("=" * 50)

    from agents.cognitive_agent.security.rate_limiter import (
        RateLimiter,
        RateLimitConfig,
        RateLimitStrategy,
        rate_limited,
        RateLimitExceededError,
    )

    # Конфигурация: 3 вызова за 10 секунд
    limiter = RateLimiter(
        RateLimitConfig(
            max_calls=3,
            period_seconds=10,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )
    )

    # Декорированная функция
    @rate_limited(limiter, key_func=lambda user_id: f"user:{user_id}")
    def decorated_function(user_id: str):
        return f"Hello from {user_id}"

    # Тест 5.1: Первые 3 вызова
    for i in range(3):
        result = decorated_function("user1")
        print(f"  ✅ Call {i+1}: {result}")

    # Тест 5.2: 4-й вызов заблокирован
    try:
        decorated_function("user1")
        print("  ❌ 4th call not blocked!")
    except RateLimitExceededError:
        print("  ✅ 4th call blocked by decorator")

    # Тест 5.3: Другой ключ (user2) должен иметь свой лимит
    result = decorated_function("user2")
    print(f"  ✅ Different key (user2) allowed: {result}")

    print("  ✅ Тест 5 пройден\n")


def test_rate_limiter_reset():
    """Тест сброса rate limiter"""
    print("\n🧪 Тест 6: Rate Limiter Reset")
    print("=" * 50)

    from agents.cognitive_agent.security.rate_limiter import (
        RateLimiter,
        RateLimitConfig,
        RateLimitStrategy,
    )

    limiter = RateLimiter(
        RateLimitConfig(
            max_calls=3,
            period_seconds=60,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )
    )

    # Исчерпать лимит
    for i in range(3):
        limiter.check_rate_limit("reset_test")

    # Проверить что лимит исчерпан
    remaining = limiter.get_remaining_calls("reset_test")
    assert remaining == 0, f"Expected 0 remaining, got {remaining}"
    print(f"  ✅ Limiter exhausted: {remaining} remaining")

    # Сбросить
    limiter.reset("reset_test")
    remaining = limiter.get_remaining_calls("reset_test")
    assert remaining == 3, f"Expected 3 remaining after reset, got {remaining}"
    print(f"  ✅ Limiter reset: {remaining} remaining")

    print("  ✅ Тест 6 пройден\n")


def main():
    """Запуск всех тестов"""
    print("\n🚀 Запуск тестов RateLimiter модуля")
    print("=" * 70)

    try:
        test_rate_limiter_sliding_window()
        test_rate_limiter_fixed_window()
        test_rate_limiter_token_bucket()
        test_predefined_rate_limiters()
        test_rate_limit_decorator()
        test_rate_limiter_reset()

        print("\n" + "=" * 70)
        print("✅ ВСЕ ТЕСТЫ RateLimiter ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
