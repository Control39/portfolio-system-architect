import hashlib
from pathlib import Path


def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# Проверка всех файлов в teacher/ и .agents/teacher/
base_root = Path("teacher")
base_agents = Path(".agents/teacher")

files_checked = 0
identical = 0
different = 0
missing = 0

for file_path in base_root.rglob("*"):
    if file_path.is_file():
        relative_path = file_path.relative_to(base_root)
        agents_path = base_agents / relative_path

        files_checked += 1

        if not agents_path.exists():
            print(f"❌ {relative_path} — отсутствует в .agents/")
            missing += 1
            continue

        hash1 = get_hash(file_path)
        hash2 = get_hash(agents_path)

        if hash1 == hash2:
            identical += 1
        else:
            print(f"⚠️ {relative_path} — РАЗНЫЕ (корень: {hash1[:8]}..., .agents: {hash2[:8]}...)")
            different += 1

print("\n" + "=" * 60)
print(f"Всего файлов проверено: {files_checked}")
print(f"✅ Идентичных: {identical}")
print(f"❌ Разных: {different}")
print(f"⚠️ Отсутствующих в .agents/: {missing}")

if different == 0 and missing == 0:
    print("\n✅ teacher/ — полный дубликат .agents/teacher/")
