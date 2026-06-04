#!/usr/bin/env python3
"""
Быстрое обновление токена в settings.json
"""

import json
from pathlib import Path

TOKEN_CACHE = Path(__file__).parent / ".token_cache.json"
SETTINGS = Path(__file__).parent.parent.parent / ".vscode" / "settings.json"

if not TOKEN_CACHE.exists():
    print("❌ Файл токена не найден. Сначала запустите get_token.py")
    exit(1)

token_data = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
access_token = token_data.get("access_token")

if not access_token:
    print("❌ Токен не найден в кэше")
    exit(1)

if not SETTINGS.exists():
    print(f"❌ Файл настроек не найден: {SETTINGS}")
    exit(1)

settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
settings["gigacode.bearerToken"] = access_token

SETTINGS.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("✅ Токен обновлён в .vscode/settings.json")
print(f"   Действителен до: {token_data.get('expires_at')}")
print("\nПерезагрузите VS Code: Ctrl+Shift+P → 'Developer: Reload Window'")
