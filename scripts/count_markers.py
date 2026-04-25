import json
from pathlib import Path

# Определяем путь к директории с маркерами
markers_dir = Path("apps/it-compass/src/data/markers")

# Счетчики
total_files = 0
total_markers = 0

print("Анализ файлов маркеров IT-Compass...")
print("=" * 50)

# Проходим по всем JSON файлам в директории
for file_path in markers_dir.glob("*.json"):
    total_files += 1

    try:
        with open(file_path, encoding="utf-8-sig") as f:
            data = json.load(f)

        skill_name = data.get("skill_name", "Unknown")
        levels = data.get("levels", {})

        # Считаем маркеры в каждом уровне
        skill_marker_count = 0
        for level_num, level_markers in levels.items():
            skill_marker_count += len(level_markers)

        total_markers += skill_marker_count

        print(f"{skill_name:20} | Уровни: {len(levels):2} | Маркеры: {skill_marker_count:2}")

    except Exception as e:
        print(f"Ошибка при чтении {file_path}: {e}")

print("=" * 50)
print("ИТОГО:")
print(f"Файлов (доменов):     {total_files}")
print(f"Всего маркеров:       {total_markers}")
print(f"Среднее на домен:     {total_markers/total_files:.1f}")
