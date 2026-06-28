#!/usr/bin/env python3
"""Диагностика токена в .vscode/settings.json"""

import re

settings_path = ".vscode/settings.json"

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

print("Original content (first 500 chars):")
print(repr(content[:500]))
print()

# Пытаемся найти токен
patterns = [
    (r'"gigacode\.bearerToken"\s*:\s*"([^"]*)"', "Simple pattern"),
    (r'"gigacode\.bearerToken"\s*:\s*"([^"]*)"\s*/\*', "With comment"),
    (r'"gigacode\.bearerToken"\s*:\s*([\s\S]*?)(?="|$)', "Multi-line"),
]

for pattern, name in patterns:
    matches = re.findall(pattern, content)
    print(f"\n{name}:")
    print(f"  Pattern: {pattern}")
    print(f"  Matches: {len(matches)}")
    for i, m in enumerate(matches):
        if m:
            print(f"    Match {i}: {m[:50]}... (len={len(m)})")
        else:
            print(f"    Match {i}: EMPTY")

# Пытаемся найти любой JWT токен
jwt_pattern = r"([A-Za-z0-9_-]{70,}\.[A-Za-z0-9_-]{70,}\.[A-Za-z0-9_-]{70,})"
jwt_matches = re.findall(jwt_pattern, content)
print(f"\nJWT tokens found: {len(jwt_matches)}")
for i, token in enumerate(jwt_matches):
    print(f"  Token {i}: {token[:50]}... (len={len(token)})")

# Пытаемся найти любой токен, похожий на JWT
token_pattern = r'"([^"]{100,})"'
all_tokens = re.findall(token_pattern, content)
print(f"\nLong strings (100+ chars) found: {len(all_tokens)}")
for i, token in enumerate(all_tokens[:5]):  # Показываем первые 5
    print(f"  Token {i}: {token[:50]}... (len={len(token)})")
