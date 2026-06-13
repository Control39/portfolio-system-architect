import os
import sys
from pathlib import Path

# Путь к .gigacode
gigacode_dir = Path(__file__).parent.parent.parent / "tools" / "devtools" / ".devtools" / ".gigacode"
repo_root = Path(__file__).parent.parent

# Добавляем оба пути в sys.path

# Меняем директорию работы
os.chdir(gigacode_dir)

# Теперь импортируем
import get_token
import update_vscode_token

if __name__ == "__main__":
    try:
        print("🔄 Получение нового токена...")
        token = get_token.get_valid_token()
        print("✅ Токен получен")

        print("🔄 Обновление настроек VS Code...")
        update_vscode_token.update_vscode_settings(token)
        print("✅ Настройки обновлены")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
