#!/usr/bin/env python3
"""Аналитика GitHub-репо: просмотры, клоны, источники.
Требует: pip install requests
GitHub Token с правами: repo
"""
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

OWNER = "Control39"
REPO = "portfolio-system-architect"
TOKEN = os.getenv("GITHUB_TOKEN")
OUT_DIR = Path("analytics")
OUT_DIR.mkdir(exist_ok=True)

def fetch_github(endpoint: str):
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/{endpoint}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    print(f"⚠️ Ошибка {resp.status_code}: {resp.text}")
    return None

def save_csv(data: list, filename: str, fieldnames: list):
    filepath = OUT_DIR / filename
    file_exists = filepath.exists()
    with open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists: writer.writeheader()
        writer.writerows(data)
    print(f"💾 Сохранено: {filepath}")

def main():
    if not TOKEN:
        print("❌ Установи переменную GITHUB_TOKEN")
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")

    # 1. Просмотры
    views = fetch_github("traffic/views")
    if views:
        save_csv(views["views"], f"views_{today}.csv", ["timestamp", "count", "uniques"])
        print(f"👁️ Просмотров за 14 дней: {views['count']} | Уникальных: {views['uniques']}")

    # 2. Клоны
    clones = fetch_github("traffic/clones")
    if clones:
        save_csv(clones["clones"], f"clones_{today}.csv", ["timestamp", "count", "uniques"])
        print(f"📥 Клонов за 14 дней: {clones['count']} | Уникальных: {clones['uniques']}")

    # 3. Источники (referrers)
    refs = fetch_github("traffic/popular/referrers")
    if refs:
        save_csv(refs, f"referrers_{today}.csv", ["referrer", "count", "uniques"])
        print(f"🔗 Топ источники: {[r['referrer'] for r in refs[:3]]}")

    print("✅ Аналитика обновлена. Запускай daily через cron / GitHub Actions.")

if __name__ == "__main__": sys.exit(main())
