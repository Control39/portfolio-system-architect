import json


with open(".gigacode/.token_cache.json", encoding="utf-8") as f:
    data = json.load(f)
    token = data["access_token"]

# Обновляем settings.json
with open(".vscode/settings.json", encoding="utf-8") as f:
    lines = f.readlines()

# Ищем строку с gigacode.authorizationHeader и заменяем
found = False
for i, line in enumerate(lines):
    if "gigacode.authorizationHeader" in line:
        lines[i] = f'  "gigacode.authorizationHeader": "Bearer {token}",\n'
        found = True
        break

if not found:
    # Добавляем после gigacode.apiEndpoint
    for i, line in enumerate(lines):
        if "gigacode.apiEndpoint" in line:
            lines.insert(i + 1, f'  "gigacode.authorizationHeader": "Bearer {token}",\n')
            break

with open(".vscode/settings.json", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ Токен обновлен в .vscode/settings.json")
print(f"   Токен действителен до: {data['expires_at']}")
