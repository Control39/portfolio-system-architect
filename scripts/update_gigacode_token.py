#!/usr/bin/env python3
"""
Автоматическое обновление токена GigaCode
Запускается каждые 25 минут через Task Scheduler
"""
import json
from pathlib import Path
import requests
import uuid
from datetime import datetime, timedelta
import sys

sys.path.insert(0, r'C:\repo')

# Путь к файлам
gigacode_dir = Path(r'C:\repo\.devtools\.gigacode')
env_file = gigacode_dir / "personal.env"
token_cache_file = gigacode_dir / ".token_cache.json"
vscode_settings = Path(r'C:\repo\.vscode\settings.json')

# 1. Загрузка personal.env
env = {}
with open(env_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()

# 2. Получение нового токена
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": str(uuid.uuid4()),
    "Authorization": f"Basic {env['GIGACODE_AUTH_KEY']}",
}
data = {"scope": env.get('GIGACODE_SCOPE', 'GIGACHAT_API_PERS')}

try:
    response = requests.post(url, headers=headers, data=data, timeout=30, verify=False)
    response.raise_for_status()
    result = response.json()
    access_token = result['access_token']
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
with open(vscode_settings, encoding='utf-8') as f:
    settings = json5.load(f)

settings['gigacode.accessToken'] = access_token

with open(vscode_settings, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print(f"✅ Токен обновлён (истекает: {expires_at.strftime('%H:%M:%S')})")
