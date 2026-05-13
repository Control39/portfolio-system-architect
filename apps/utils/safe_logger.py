def mask_sensitive(value: str, visible: int = 4) -> str:
    """Маскирует чувствительную строку, оставляя видимыми первые и последние символы."""
    if not value or len(value) <= visible:
        return "****"
    return f"{value[:visible]}****{value[-4:]}"
