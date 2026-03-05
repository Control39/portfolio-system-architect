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
    print("❌ Файл component-config.yaml не найден!")
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"❌ Ошибка парсинга YAML: {e}")
    sys.exit(1)
