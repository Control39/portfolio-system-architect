#!/usr/bin/env python3
"""Сравнение сервисов между docker-compose.yml и README.md"""

import re
import yaml

# Читаем docker-compose
with open("docker-compose.yml", encoding="utf-8") as f:
    compose = yaml.safe_load(f)
compose_services = set(compose.get("services", {}).keys())

# Читаем README
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

# Извлекаем сервисы из README (таблица)
readme_services = set(re.findall(r"\| (\S+) \|", readme))

# Сравниваем
print("=== АРХИТЕКТУРНОЕ ВЫРАВНИВАНИЕ ===")
print("")
print(f"📁 docker-compose.yml: {len(compose_services)} сервисов")
print(f"📄 README.md: {len(readme_services)} сервисов в таблице")
print("")

# Сервисы только в docker-compose
only_in_compose = compose_services - readme_services
if only_in_compose:
    print(f"⚠️ Только в docker-compose.yml ({len(only_in_compose)}):")
    for s in sorted(only_in_compose):
        print(f"   - {s}")

# Сервисы только в README
only_in_readme = readme_services - compose_services
if only_in_readme:
    print("")
    print(f"⚠️ Только в README.md ({len(only_in_readme)}):")
    for s in sorted(only_in_readme):
        print(f"   - {s}")

# Имена с _ vs -
underscore = [s for s in compose_services if "_" in s]
dash = [s for s in compose_services if "-" in s]
print("")
print("📊 Именование сервисов:")
print(f"   С подчёркиванием (_): {len(underscore)}")
for s in underscore:
    print(f"      - {s}")
print(f"   С тире (-): {len(dash)}")
for s in dash:
    print(f"      - {s}")

print("")
print("=== ИТОГ ===")
if only_in_readme or only_in_compose:
    print("⚠️ Требуется синхронизация")
else:
    print("✅ Сервисы синхронизированы")
