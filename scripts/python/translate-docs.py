#!/usr/bin/env python3
"""AI-powered documentation translation using DeepSeek.
Translates Russian .md files from docs/ to en/ subdirectory.
Preserves structure, creates PR-ready changes.
"""

import argparse
import re
from pathlib import Path

import requests

GIGACHAT_URL = "https://gigachat.api.sber.ru/chat/completions"
PROMPT = """
Переведи следующий Markdown документ с русского на английский. 
Сохрани всю Markdown структуру, кодовые блоки, ссылки, таблицы точно как есть.
Переведи только русский текст, оставь английский неизменным.
Если текст смешанный или уже на английском - сделай полный профессиональный английский перевод.
Выводи ТОЛЬКО переведенный Markdown без дополнительных комментариев.

Документ:
{ content }
"""

def translate_text(content: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "GigaChat:latest",
        "messages": [{"role": "user", "content": PROMPT.format(content=content)}],
        "temperature": 0.1,
        "max_tokens": 16000,
    }
    response = requests.post(GIGACHAT_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def is_russian(text: str) -> bool:
    """Detect if text is primarily Russian."""
    russian_chars = len(re.findall(r"[а-яё]", text, re.IGNORECASE))
    total_chars = len(text)
    return russian_chars / total_chars > 0.1  # >10% Russian chars

def process_file(file_path: Path, api_key: str):
    content = file_path.read_text(encoding="utf-8")
    if not is_russian(content):
        print(f"Skipping {file_path} (not primarily Russian)")
        return

    print(f"Translating {file_path}...")
    translated = translate_text(content, api_key)

    en_path = Path("05_DOCUMENTATION/mkdocs-site/docs/en") / file_path.relative_to("05_DOCUMENTATION/mkdocs-site/docs").with_suffix(".en.md")
    en_path.parent.mkdir(parents=True, exist_ok=True)

    en_path.write_text(translated, encoding="utf-8")
    print(f"✓ Translated: {en_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True, help="GigaChat API key")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--exclude-website", action="store_true", help="Exclude website folder")
    args = parser.parse_args()

    docs_dir = Path("05_DOCUMENTATION/docs")
    mkdocs_en_dir = Path("05_DOCUMENTATION/mkdocs-site/docs/en")
    md_files = []
    for md in docs_dir.rglob("*.md"):
        if args.exclude_website and "website" in str(md):
            print(f"Skipping website file: {md}")
            continue
        md_files.append(md)
    print(f"Found {len(md_files)} files to potentially translate")

    if args.dry_run:
        print(f"Found {len(md_files)} .md files")
        return

    for md_file in md_files:
        process_file(md_file, args.api_key)

    print("Translation complete. Commit en/ changes and create PR.")

if __name__ == "__main__":
    main()


