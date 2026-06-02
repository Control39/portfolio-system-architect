# apps/context_builder/tests/test_token_counter.py
from apps.context_builder.core.token_counter import TokenCounter


def test_token_count_gpt4():
    counter = TokenCounter(model="gpt-4")
    text = "Hello, how are you?"
    tokens = counter.count(text)
    assert isinstance(tokens, int)
    assert tokens > 0


def test_token_count_deepseek():
    counter = TokenCounter(model="deepseek")
    text = "Привет, как дела?"
    tokens = counter.count(text)
    assert tokens > 0


def test_token_count_fallback():
    # Симуляция отсутствия tiktoken
    counter = TokenCounter(model="unknown")
    counter.has_tiktoken = False
    text = "Test text for fallback"
    tokens = counter.count(text)
    assert tokens == len(text) // 3


def test_estimate_for_text():
    counter = TokenCounter(model="gpt-4")
    result = counter.estimate_for_text("Hello world!")
    assert "exact_tokens" in result
    assert "approx_chars" in result
    assert "approx_ratio" in result
    assert result["warning"] is None
