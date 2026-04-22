import sys
from pathlib import Path

# Добавляем корень проекта, src/ и apps/ в путь для импортов
# Это позволяет тестам видеть модули без установки пакета через pip
root = Path(__file__).parent.parent

src_path = root / "src"
apps_path = root / "apps"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(apps_path) not in sys.path:
    sys.path.insert(0, str(apps_path))
