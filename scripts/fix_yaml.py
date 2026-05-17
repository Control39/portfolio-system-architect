#!/usr/bin/env python3
"""Исправление YAML конфигурации"""

from pathlib import Path


config_file = Path("config/ai-config.yaml")
content = config_file.read_text(encoding="utf-8")

# Заменяем CRLF на LF
content = content.replace("\r\n", "\n")

# Добавляем document start если нет
if not content.startswith("---"):
    content = "---\n" + content

# Фиксим комментарии (добавляем пробел после #)
import re


content = re.sub(r"^( *)(#\S)", r"\1 \2", content, flags=re.MULTILINE)

config_file.write_text(content, encoding="utf-8")
print("✅ config/ai-config.yaml исправлен")
