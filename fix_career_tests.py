import shutil
from pathlib import Path


src_tests = Path("apps/career_development/src/tests")
dest_tests = Path("apps/career_development/tests")

if src_tests.exists():
    for file in src_tests.glob("*"):
        if file.is_file():
            dest = dest_tests / file.name
            if dest.exists():
                print(f"⚠️  Файл {dest} уже существует, пропускаем")
            else:
                shutil.move(str(file), str(dest))
                print(f"✅ Перенесен: {file.name}")

    # Удалить пустую папку
    try:
        src_tests.rmdir()
        print("✅ Папка src/tests/ удалена")
    except OSError as e:
        print(f"⚠️  Не удалось удалить папку src/tests/: {e}")
else:
    print("Папка src/tests/ не найдена (уже перенесена?)")
