#!/usr/bin/env python3
"""Скрипт для проверки URL бейджей в README.md
"""

import re

import requests


def extract_badge_urls(readme_content):
    """Извлечь все URL бейджей из README"""
    # Ищем все img src с URL
    img_pattern = r'<img\s+src="([^"]+)"'
    urls = re.findall(img_pattern, readme_content)

    # Также ищем в markdown формате ![alt](url)
    md_pattern = r"!\[[^\]]*\]\(([^)]+)\)"
    urls.extend(re.findall(md_pattern, readme_content))

    return list(set(urls))  # Убираем дубликаты


def check_url(url):
    """Проверить доступность URL"""
    try:
        # Для shields.io добавляем User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "image" in content_type or "svg" in content_type:
                return True, f"OK (200, {content_type})"
            return False, f"Not an image (200, {content_type})"
        return False, f"HTTP {response.status_code}"

    except requests.exceptions.RequestException as e:
        return False, f"Error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main():
    # Читаем README.md
    with open("README.md", encoding="utf-8") as f:
        content = f.read()

    urls = extract_badge_urls(content)

    print(f"Найдено {len(urls)} URL бейджей:")
    print("=" * 80)

    broken_badges = []

    for i, url in enumerate(urls[:20], 1):  # Проверяем первые 20
        print(f"{i:2}. {url[:80]}...")
        is_ok, message = check_url(url)

        if is_ok:
            print(f"     ✓ {message}")
        else:
            print(f"     ✗ {message}")
            broken_badges.append((url, message))

    print("=" * 80)

    if broken_badges:
        print(f"\nНайдено {len(broken_badges)} сломанных бейджей:")
        for url, message in broken_badges:
            print(f"  - {url[:60]}...: {message}")
    else:
        print("\nВсе бейджи работают корректно!")


if __name__ == "__main__":
    main()
