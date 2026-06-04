import os
import shutil

# Путь к исходной папке
source_dir = r"C:\Users\Z\my-ecosystem-FINAL"

# Получаем путь к рабочему столу (работает для разных версий Windows)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# Имя целевой папки
target_folder_name = "markdown_files_from_ecosystem"
# Полный путь к целевой папке
target_dir = os.path.join(desktop_path, target_folder_name)


# Создаём целевую папку на рабочем столе, если её нет
os.makedirs(target_dir, exist_ok=True)


# Счётчик скопированных файлов
copied_count = 0

print("Начинаю поиск и копирование Markdown‑файлов...")
print(f"Исходная папка: {source_dir}")
print(f"Целевая папка: {target_dir}")

# Рекурсивный обход исходной папки
for root, dirs, files in os.walk(source_dir):
    for file in files:
        # Проверяем, заканчивается ли файл на .md (регистронезависимо)
        if file.lower().endswith(".md"):
            # Полный путь к исходному файлу
            src_path = os.path.join(root, file)
            # Генерируем уникальное имя для целевого файла, если такой уже есть
            target_filename = file
            counter = 1
            while os.path.exists(os.path.join(target_dir, target_filename)):
                name, ext = os.path.splitext(file)
                target_filename = f"{name}_{counter}{ext}"
                counter += 1

            # Полный путь к целевому файлу
            dest_path = os.path.join(target_dir, target_filename)

            try:
                # Копируем файл
                shutil.copy2(src_path, dest_path)
                copied_count += 1
                print(f"Скопирован: {src_path} → {dest_path}")
            except Exception as e:
                print(f"Ошибка при копировании {src_path}: {e}")

print(f"\nГотово! Скопировано файлов: {copied_count}")
