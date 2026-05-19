
import os
import shutil

src_dir = r"C:\repo\apps\ai_config_manager\src"
pkg_dir = os.path.join(src_dir, "ai_config_manager")

# Создаём папку пакета
os.makedirs(pkg_dir, exist_ok=True)
print(f"Создана папка: {pkg_dir}")

# Файлы для перемещения
files_to_move = [
    "config_manager.py",
    "resource_pool.py",
    "security.py",
    "validators.py",
    "config_integration.py",
    "__init__.py"
]

# Перемещаем файлы
for filename in files_to_move:
    src_file = os.path.join(src_dir, filename)
    dst_file = os.path.join(pkg_dir, filename)
    if os.path.exists(src_file):
        shutil.move(src_file, dst_file)
        print(f"Перемещён: {filename}")
    else:
        print(f"Пропущен (не существует): {filename}")

# Удаляем лишние папки
dirs_to_remove = [
    "__pycache__",
    "__tests__",
    "adapters",
    "components",
    "main",
    "renderer"
]

for dirname in dirs_to_remove:
    dir_path = os.path.join(src_dir, dirname)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        print(f"Удалена папка: {dirname}")

# Удаляем preload.js
preload_path = os.path.join(src_dir, "preload.js")
if os.path.exists(preload_path):
    os.remove(preload_path)
    print("Удалён: preload.js")

print("\nГотово!")
print(f"\nИтоговая структура src/:")
for item in os.listdir(src_dir):
    item_path = os.path.join(src_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR] {item}")
    else:
        print(f"  [FILE] {item}")
