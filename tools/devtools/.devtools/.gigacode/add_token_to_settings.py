#!/usr/bin/env python3
"""
Добавляет Bearer токен в settings.json
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import commentjson
except ImportError:
    print("Устанавливаю commentjson...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "commentjson", "-q"])
    import commentjson

TOKEN_CACHE = Path(__file__).parent / ".token_cache.json"
SETTINGS = Path(__file__).parent.parent.parent / ".vscode" / "settings.json"

if not TOKEN_CACHE.exists():
    print("❌ Файл токена не найден. Сначала запустите get_token.py")
    sys.exit(1)

import json
token_data = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
access_token = token_data.get("access_token")

if not access_token:
    print("❌ Токен не найден в кэше")
    sys.exit(1)

if not SETTINGS.exists():
    print(f"❌ Файл настроек не найден: {SETTINGS}")
    sys.exit(1)

content = SETTINGS.read_text(encoding="utf-8")
data = commentjson.loads(content)

data["gigacode.bearerToken"] = access_token

SETTINGS.write_text(commentjson.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("✅ Токен добавлен в .vscode/settings.json")
print(f"   Действителен до: {token_data.get('expires_at')}")
print("\n🔄 Перезагрузите VS Code:")
print("   Ctrl+Shift+P → 'Developer: Reload Window'")
