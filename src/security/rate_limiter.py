#!/usr/bin/env python3
"""
Rate Limiter module
Rate limiting with multiple strategies
"""

import functools
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum


class RateLimitStrategy(StrEnum):
    """Rate limiting strategies"""

    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    TOKEN_BUCKET = "token_bucket"


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded"""

    pass


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    max_calls: int
    period_seconds: float
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_size: int | None = None  # For token bucket

    def __post_init__(self):
        if self.max_calls <= 0:
            raise ValueError("max_calls must be positive")
        if self.period_seconds <= 0:
            raise ValueError("period_seconds must be positive")

        # Token bucket requires burst_size
        if self.strategy == RateLimitStrategy.TOKEN_BUCKET and self.burst_size is None:
            self.burst_size = self.max_calls


@dataclass
class RateLimitState:
    """Current rate limit state for a key"""

    calls: list = field(default_factory=list)
    tokens: float = 0  # For token bucket

    @property
    def count(self) -> int:
        """Current call count in the window"""
        return len(self.calls)

    @property
    def oldest_call(self) -> float | None:
        """Timestamp of oldest call in window"""
        return min(self.calls) if self.calls else None

    @property
    def newest_call(self) -> float | None:
        """Timestamp of newest call in window"""
        return max(self.calls) if self.calls else None


def rate_limited(limiter: "RateLimiter", key_func: Callable[..., str] | None = None) -> Callable:
    """Decorator to apply rate limiting to a function"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key
            key = key_func(*args, **kwargs) if key_func else func.__name__

            # Check rate limit
            limiter.check_rate_limit(key)

            # Execute function
            return func(*args, **kwargs)

        return wrapper

    return decorator


class RateLimiter:
    """
    Rate limiter with sliding window, fixed window, and token bucket strategies

    Examples:
        >>> limiter = RateLimiter(RateLimitConfig(max_calls=5, period_seconds=2))
        >>> limiter.check_rate_limit("user123")  # First 5 calls succeed
        >>> limiter.check_rate_limit("user123")  # 6th call raises RateLimitExceededError
    """

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._states: dict[str, RateLimitState] = {}

    def _get_state(self, key: str) -> RateLimitState:
        """Get or create state for a key"""
        if key not in self._states:
            self._states[key] = RateLimitState()
        return self._states[key]

    def check_rate_limit(self, key: str, timestamp: float | None = None) -> None:
        """Check if request is allowed, raise if rate limited"""
        if timestamp is None:
            timestamp = time.time()

        state = self._get_state(key)

        if self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            self._check_sliding_window(state, key, timestamp)
        elif self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            self._check_token_bucket(state, key, timestamp)
        else:
            self._check_fixed_window(state, key, timestamp)

    def _check_sliding_window(self, state: RateLimitState, key: str, timestamp: float) -> None:
        """Check rate limit using sliding window strategy"""
        # Remove old calls outside the window
        cutoff = timestamp - self.config.period_seconds
        state.calls = [t for t in state.calls if t > cutoff]

        # Check if limit exceeded
        if state.count >= self.config.max_calls:
            raise RateLimitExceededError(
                f"Rate limit exceeded for key '{key}'. "
                f"Max {self.config.max_calls} calls per {self.config.period_seconds}s"
            )

        # Record this call
        state.calls.append(timestamp)

    def _check_fixed_window(self, state: RateLimitState, key: str, timestamp: float) -> None:
        """Check rate limit using fixed window strategy"""
        # Calculate current window
        window_start = (timestamp // self.config.period_seconds) * self.config.period_seconds
        window_end = window_start + self.config.period_seconds

        # Remove calls from previous windows
        state.calls = [t for t in state.calls if window_start <= t < window_end]

        # Check if limit exceeded
        if state.count >= self.config.max_calls:
            raise RateLimitExceededError(
                f"Rate limit exceeded for key '{key}'. "
                f"Max {self.config.max_calls} calls per {self.config.period_seconds}s"
            )

        # Record this call
        state.calls.append(timestamp)

    def _check_token_bucket(self, state: RateLimitState, key: str, timestamp: float) -> None:
        """Check rate limit using token bucket strategy"""
        burst_size = self.config.burst_size or self.config.max_calls

        # Refill tokens based on time elapsed
        if state.tokens == 0:
            # Initialize with full bucket
            state.tokens = burst_size
        else:
            # Calculate tokens to add based on time
            time_passed = timestamp - (state.calls[-1] if state.calls else timestamp)
            tokens_to_add = time_passed * (self.config.max_calls / self.config.period_seconds)
            state.tokens = min(burst_size, state.tokens + tokens_to_add)

        # Check if we have tokens
        if state.tokens < 1:
            raise RateLimitExceededError(
                f"Rate limit exceeded for key '{key}'. "
                f"Token bucket empty, waiting {1 / (self.config.max_calls / self.config.period_seconds):.2f}s for refill"
            )

        # Consume one token
        state.tokens -= 1
        state.calls.append(timestamp)

    def reset(self, key: str) -> None:
        """Reset rate limit for a key"""
        if key in self._states:
            del self._states[key]

    def get_remaining_calls(self, key: str, timestamp: float | None = None) -> int:
        """Get remaining calls for a key"""
        if timestamp is None:
            timestamp = time.time()

        state = self._get_state(key)

        if self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            cutoff = timestamp - self.config.period_seconds
            valid_calls = [t for t in state.calls if t > cutoff]
            return max(0, self.config.max_calls - len(valid_calls))
        elif self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return int(state.tokens)
        else:
            window_start = (timestamp // self.config.period_seconds) * self.config.period_seconds
            valid_calls = [t for t in state.calls if window_start <= t < window_start + self.config.period_seconds]
            return max(0, self.config.max_calls - len(valid_calls))

    def get_reset_time(self, key: str, timestamp: float | None = None) -> float | None:
        """Get time when rate limit resets for a key"""
        if timestamp is None:
            timestamp = time.time()

        state = self._get_state(key)

        if not state.calls:
            return None

        if self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            oldest = min(state.calls)
            return oldest + self.config.period_seconds
        elif self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            tokens_needed = 1 - state.tokens
            time_per_token = self.config.period_seconds / self.config.max_calls
            return timestamp + (tokens_needed * time_per_token)
        else:
            window_start = (timestamp // self.config.period_seconds) * self.config.period_seconds
            return window_start + self.config.period_seconds


class PredefinedRateLimiters:
    """Predefined rate limiters for common use cases"""

    @staticmethod
    def ai_calls() -> RateLimiter:
        """Rate limiter for AI calls (conservative)"""
        return RateLimiter(
            RateLimitConfig(max_calls=50, period_seconds=3600, strategy=RateLimitStrategy.SLIDING_WINDOW)
        )

    @staticmethod
    def api_calls() -> RateLimiter:
        """Rate limiter for API calls (moderate)"""
        return RateLimiter(RateLimitConfig(max_calls=60, period_seconds=60, strategy=RateLimitStrategy.FIXED_WINDOW))

    @staticmethod
    def aggressive() -> RateLimiter:
        """Rate limiter for aggressive usage (permissive)"""
        return RateLimiter(RateLimitConfig(max_calls=100, period_seconds=10, strategy=RateLimitStrategy.SLIDING_WINDOW))

    @staticmethod
    def file_operations() -> RateLimiter:
        """Rate limiter for file operations (moderate)"""
        return RateLimiter(RateLimitConfig(max_calls=100, period_seconds=60, strategy=RateLimitStrategy.SLIDING_WINDOW))

    @staticmethod
    def scan_operations() -> RateLimiter:
        """Rate limiter for scan operations (conservative)"""
        return RateLimiter(RateLimitConfig(max_calls=10, period_seconds=60, strategy=RateLimitStrategy.SLIDING_WINDOW))

    @staticmethod
    def api_requests() -> RateLimiter:
        """Rate limiter for API requests (high capacity)"""
        return RateLimiter(
            RateLimitConfig(max_calls=1000, period_seconds=3600, strategy=RateLimitStrategy.FIXED_WINDOW)
        )
