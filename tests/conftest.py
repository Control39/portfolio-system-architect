"""
Фикстуры и настройки для всех тестов.
Автоматически добавляет src/ в путь для импортов.
Apps добавляются их собственными conftest.py файлами.
"""

import sys
from pathlib import Path

# Добавляем корень проекта и src/ в путь для импортов
# Это позволяет тестам видеть модули без установки пакета через pip
root = Path(__file__).parent.parent

src_path = root / "src"

# Корень проекта нужен для импортов вида `from src.common...`
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Apps не добавляем сюда - каждый app должен добавлять свой src через свой conftest.py
