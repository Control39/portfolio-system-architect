#!/usr/bin/env python3
"""
Автоматическое обновление токена GigaCode
Запускается каждые 25 минут через Task Scheduler
"""

import base64
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

# Определяем пути относительно корня проекта (scripts/ находится в корне)
project_root = Path(__file__).parent.parent

# Загружаем .env из корня проекта
load_dotenv(project_root / ".env", override=True)

# Путь к файлам
gigacode_dir = project_root / ".devtools" / ".gigacode"
env_file = gigacode_dir / "personal.env"
fallback_env_file = project_root / ".env"
token_cache_file = gigacode_dir / ".token_cache.json"
vscode_settings = project_root / ".vscode" / "settings.json"


def resolve_auth_key(env: dict) -> str:
    """Определяет OAuth auth key из нескольких источников"""
    auth_key = env.get("GIGACODE_AUTH_KEY")
    if auth_key:
        return auth_key
    auth_key = env.get("GIGACHAT_CREDENTIALS")
    if auth_key:
        print("⚠️  Используется GIGACHAT_CREDENTIALS вместо GIGACODE_AUTH_KEY")
        return auth_key
    client_id = env.get("GIGACODE_CLIENT_ID")
    client_secret = env.get("GIGACODE_CLIENT_SECRET")
    if client_id and client_secret:
        auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        print("⚠️  Сгенерирован GIGACODE_AUTH_KEY из CLIENT_ID + CLIENT_SECRET")
        return auth_key
    print(
        "❌ Не найден OAuth ключ. Укажите GIGACODE_AUTH_KEY, GIGACHAT_CREDENTIALS или GIGACODE_CLIENT_ID + GIGACODE_CLIENT_SECRET"
    )
    sys.exit(1)


# 1. Загрузка env (personal.env → .env → os.environ/dotenv)
env = {}
source_file = env_file if env_file.exists() else fallback_env_file

if source_file.exists():
    with open(source_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
elif any(k.startswith(("GIGACODE_", "GIGACHAT_")) for k in os.environ):
    # Переменные уже загружены dotenv или заданы в системе
    env = dict(os.environ)
    print("⚠️  .env файлы не найдены, используется os.environ")
else:
    print(f"❌ Не найден файл с настройками: ни {env_file}, ни {fallback_env_file}, ни переменные окружения")
    sys.exit(1)

# 2. Получение нового токена
auth_key = resolve_auth_key(env)
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": str(uuid.uuid4()),
    "Authorization": f"Basic {auth_key}",
}
data = {"scope": env.get("GIGACODE_SCOPE", "GIGACHAT_API_PERS")}

try:
    response = requests.post(url, headers=headers, data=data, timeout=30, verify=False)  # nosec B501
    response.raise_for_status()
    result = response.json()
    access_token = result["access_token"]
except Exception as e:
    print(f"❌ Ошибка получения токена: {e}")
    sys.exit(1)

# 3. Кэширование токена
expires_at = datetime.now() + timedelta(seconds=1800 - 300)  # 25 минут
cache = {
    "access_token": access_token,
    "expires_at": expires_at.isoformat(),
    "created_at": datetime.now().isoformat(),
}
with open(token_cache_file, "w", encoding="utf-8") as f:
    json.dump(cache, f, indent=2, ensure_ascii=False)

# 4. Обновление .vscode/settings.json
import json5

with open(vscode_settings, encoding="utf-8") as f:
    settings = json5.load(f)

settings["gigacode.accessToken"] = access_token

with open(vscode_settings, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print(f"✅ Токен обновлён (истекает: {expires_at.strftime('%H:%M:%S')})")
