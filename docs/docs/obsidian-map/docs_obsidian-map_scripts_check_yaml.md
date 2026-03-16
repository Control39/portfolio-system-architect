# Scripts Check Yaml

- **Путь**: `docs\obsidian-map\scripts_check_yaml.md`
- **Тип**: .MD
- **Размер**: 798 байт
- **Последнее изменение**: 2026-03-12 11:24:56

## Превью

```
# Check Yaml

- **Путь**: `scripts\check_yaml.py`
- **Тип**: .PY
- **Размер**: 589 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
# check_yaml.py
import yaml
import sys

try:
    with open('component-config.yaml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    print("✅ YAML успешно загружен!")
    print(f"Версия конфигурации: {data.get('version', 'N/A')}")
    print(f"Название проекта: {data.get('name', 'N/A')}")
except FileNotFoundError:
    print("
... (файл продолжается)
```
