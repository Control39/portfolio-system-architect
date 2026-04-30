#!/usr/bin/env python3
"""
Полная проверка всех ссылок в README файлах.
Проверяет внутренние ссылки на существование файлов/директорий,
внешние ссылки на доступность (HTTP статус).
"""

import concurrent.futures
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests

# Настройки
README_FILES = ["README.md", "README.ru.md"]
EXTERNAL_TIMEOUT = 10
MAX_WORKERS = 5
IGNORE_DOMAINS = {"shields.io", "img.shields.io"}


def extract_all_links(file_path: Path) -> List[Dict[str, str]]:
    """Извлекает все ссылки из markdown файла."""
    links = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Ошибка чтения файла {file_path}: {e}")
        return links

    # Регулярные выражения для всех типов ссылок в markdown
    patterns = [
        (r"\[([^\]]+)\]\(([^)]+)\)", "link"),  # [текст](URL)
        (r"!\[([^\]]*)\]\(([^)]+)\)", "image"),  # ![alt](URL)
        (r"<([^>]+)>", "autolink"),  # <URL>
    ]

    for pattern, link_type in patterns:
        for match in re.finditer(pattern, content):
            if link_type == "link" or link_type == "image":
                text, url = match.groups()
            else:  # autolink
                url = match.group(1)
                text = ""
                # Пропускаем email адреса
                if "@" in url and "." in url:
                    continue

            links.append(
                {
                    "type": link_type,
                    "url": url.strip(),
                    "text": text.strip(),
                    "line": content[: match.start()].count("\n") + 1,
                    "file": str(file_path.name),
                }
            )

    return links


def is_internal_link(url: str) -> bool:
    """Определяет, является ли ссылка внутренней (относительный путь)."""
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.netloc


def check_external_link(url: str) -> Tuple[bool, int, str]:
    """Проверяет доступность внешней ссылки."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Для GitHub API используем GET
        if "api.github.com" in url:
            response = requests.get(url, headers=headers, timeout=EXTERNAL_TIMEOUT)
        else:
            response = requests.head(
                url, headers=headers, timeout=EXTERNAL_TIMEOUT, allow_redirects=True
            )

        status = response.status_code
        success = 200 <= status < 400
        return success, status, ""
    except requests.exceptions.Timeout:
        return False, 0, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, 0, "Connection Error"
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)
    except Exception as e:
        return False, 0, f"Unexpected error: {e}"


def check_internal_link(url: str, base_dir: Path) -> Tuple[bool, str]:
    """Проверяет существование внутреннего файла или директории."""
    # Убираем якоря (#) и query параметры
    clean_url = url.split("#")[0].split("?")[0]

    if not clean_url:
        return False, "Empty URL"

    # Если ссылка начинается с /, относим к корню проекта
    if clean_url.startswith("/"):
        target_path = base_dir / clean_url[1:]
    else:
        target_path = base_dir / clean_url

    # Проверяем существование
    if target_path.exists():
        return True, ""
    else:
        return False, f"File not found: {target_path}"


def main():
    """Основная функция."""
    base_dir = Path.cwd()
    all_links = []

    print("🔍 Извлечение ссылок из README файлов...")

    # Собираем все ссылки
    for readme_file in README_FILES:
        file_path = base_dir / readme_file
        if not file_path.exists():
            print(f"⚠️  Файл {readme_file} не найден, пропускаем")
            continue

        links = extract_all_links(file_path)
        all_links.extend(links)
        print(f"📄 {readme_file}: найдено {len(links)} ссылок")

    if not all_links:
        print("❌ Ссылки не найдены")
        return

    print(f"\n📊 Всего ссылок: {len(all_links)}")

    # Разделяем на внутренние и внешние
    internal_links = []
    external_links = []

    for link in all_links:
        url = link["url"]
        if is_internal_link(url):
            link["category"] = "internal"
            internal_links.append(link)
        else:
            link["category"] = "external"
            external_links.append(link)

    print(f"🔗 Внутренние ссылки: {len(internal_links)}")
    print(f"🌐 Внешние ссылки: {len(external_links)}")

    # Проверяем внутренние ссылки
    print("\n🔍 Проверка внутренних ссылок...")
    internal_broken = []

    for link in internal_links:
        url = link["url"]
        ok, error = check_internal_link(url, base_dir)
        link["status"] = "ok" if ok else "broken"
        link["error"] = error if not ok else ""

        if not ok:
            internal_broken.append(link)
            print(f"❌ {link['file']}:{link['line']} - {url} - {error}")
        else:
            print(f"✅ {link['file']}:{link['line']} - {url}")

    # Проверяем внешние ссылки
    print("\n🔍 Проверка внешних ссылок...")
    external_broken = []

    # Фильтруем игнорируемые домены
    filtered_external = []
    for link in external_links:
        parsed = urlparse(link["url"])
        if parsed.netloc in IGNORE_DOMAINS:
            link["status"] = "ignored"
            link["error"] = "Ignored domain"
            print(f"⏭️  {link['file']}:{link['line']} - {link['url']} (игнорируется)")
        else:
            filtered_external.append(link)

    # Проверяем остальные внешние ссылки
    def check_link(link):
        url = link["url"]
        ok, status, error = check_external_link(url)
        link["status"] = "ok" if ok else "broken"
        link["http_status"] = status
        link["error"] = error
        return link

    print(f"Проверяем {len(filtered_external)} внешних ссылок...")

    # Используем многопоточность для ускорения
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_link = {
            executor.submit(check_link, link): link for link in filtered_external
        }

        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            try:
                link = future.result()
                if link["status"] == "ok":
                    print(
                        f"✅ {link['file']}:{link['line']} - {link['url']} ({link['http_status']})"
                    )
                else:
                    external_broken.append(link)
                    print(
                        f"❌ {link['file']}:{link['line']} - {link['url']} - {link['error']}"
                    )
            except Exception as e:
                print(f"⚠️  Ошибка при проверке {link['url']}: {e}")

    # Сводный отчёт
    print("\n" + "=" * 60)
    print("📊 СВОДНЫЙ ОТЧЁТ")
    print("=" * 60)

    total_broken = len(internal_broken) + len(external_broken)

    if total_broken == 0:
        print("🎉 Все ссылки работают корректно!")
    else:
        print(f"⚠️  Найдено битых ссылок: {total_broken}")

        if internal_broken:
            print(f"\n🔗 Битые внутренние ссылки ({len(internal_broken)}):")
            for link in internal_broken:
                print(f"  • {link['file']}:{link['line']} - {link['url']}")
                print(f"    Текст: {link['text']}")
                print(f"    Ошибка: {link['error']}")

        if external_broken:
            print(f"\n🌐 Битые внешние ссылки ({len(external_broken)}):")
            for link in external_broken:
                print(f"  • {link['file']}:{link['line']} - {link['url']}")
                print(f"    Текст: {link['text']}")
                if link.get("http_status"):
                    print(f"    HTTP статус: {link['http_status']}")
                print(f"    Ошибка: {link['error']}")

    # Сохраняем отчёт в файл
    report_file = base_dir / "README_LINKS_REPORT.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Отчёт о проверке ссылок в README\n\n")
        f.write(f"Дата проверки: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Статистика\n")
        f.write(f"- Всего ссылок: {len(all_links)}\n")
        f.write(f"- Внутренние ссылки: {len(internal_links)}\n")
        f.write(f"- Внешние ссылки: {len(external_links)}\n")
        f.write(f"- Битые внутренние ссылки: {len(internal_broken)}\n")
        f.write(f"- Битые внешние ссылки: {len(external_broken)}\n")
        f.write(f"- **Всего битых: {total_broken}**\n\n")

        if internal_broken:
            f.write("## Битые внутренние ссылки\n\n")
            for link in internal_broken:
                f.write(f"### {link['file']}:{link['line']}\n")
                f.write(f"- **URL**: `{link['url']}`\n")
                f.write(f"- **Текст**: {link['text']}\n")
                f.write(f"- **Ошибка**: {link['error']}\n\n")

        if external_broken:
            f.write("## Битые внешние ссылки\n\n")
            for link in external_broken:
                f.write(f"### {link['file']}:{link['line']}\n")
                f.write(f"- **URL**: `{link['url']}`\n")
                f.write(f"- **Текст**: {link['text']}\n")
                if link.get("http_status"):
                    f.write(f"- **HTTP статус**: {link['http_status']}\n")
                f.write(f"- **Ошибка**: {link['error']}\n\n")

    print(f"\n📄 Подробный отчёт сохранён в {report_file}")

    # Возвращаем код выхода
    if total_broken > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
