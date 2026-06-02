import shutil
from pathlib import Path

dirs_to_delete = ["skills", "teacher", "rules"]

for dir_name in dirs_to_delete:
    path = Path(dir_name)
    if path.exists():
        print(f"Удаление {dir_name}...")
        shutil.rmtree(path)
        print(f"✅ {dir_name} удалён")
    else:
        print(f"⚠️ {dir_name} не найден")

print("\nГотово!")
