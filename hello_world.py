"""
Hello World приложение
"""

def greet(name: str = "World") -> str:
    """Возвращает приветственное сообщение.
    
    Args:
        name: Имя для приветствия. По умолчанию "World".
    
    Returns:
        Приветственное сообщение.
    """
    return f"Hello, {name}!"

def main() -> None:
    """Точка входа в приложение."""
    print(greet())


if __name__ == "__main__":
    main()