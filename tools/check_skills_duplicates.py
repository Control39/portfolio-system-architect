import hashlib
from pathlib import Path


def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(usedforsecurity=False)f.read()).hexdigest()


# Проверка всех файлов в skills/ и .agents/skills/
base_root = Path("skills")
base_agents = Path(".agents/skills")

print("Сравнение папки skills/ и .agents/skills/")
print("=" * 60)

files_checked = 0
identical = 0
different = 0
missing_in_agents = 0
only_in_root = []

for file_path in base_root.rglob("*"):
    if file_path.is_file():
        relative_path = file_path.relative_to(base_root)
        agents_path = base_agents / relative_path

        files_checked += 1

        if not agents_path.exists():
            print(f"❌ {relative_path} — отсутствует в .agents/skills/")
            missing_in_agents += 1
            only_in_root.append(str(relative_path))
            continue

        hash1 = get_hash(file_path)
        hash2 = get_hash(agents_path)

        if hash1 == hash2:
            identical += 1
        else:
            print(f"⚠️ {relative_path} — РАЗНЫЕ файлы!")
            different += 1

# Проверка что есть в .agents/skills/ но нет в skills/
only_in_agents = []
for file_path in base_agents.rglob("*"):
    if file_path.is_file():
        relative_path = file_path.relative_to(base_agents)
        root_path = base_root / relative_path
        if not root_path.exists():
            only_in_agents.append(str(relative_path))

print("\n" + "=" * 60)
print(f"Всего файлов в skills/ проверено: {files_checked}")
print(f"✅ Идентичных: {identical}")
print(f"❌ Разных: {different}")
print(f"⚠️ Только в skills/ (отсутствуют в .agents/): {missing_in_agents}")
print(f"ℹ️ Только в .agents/skills/ (новые): {len(only_in_agents)}")

if only_in_agents:
    print("\nНовые скиллы только в .agents/skills/:")
    for skill in set([p.split("/")[0] for p in only_in_agents]):
        print(f"  - {skill}")

if different == 0 and missing_in_agents == 0:
    print("\n✅ skills/ — полный дубликат .agents/skills/")
elif missing_in_agents == 0:
    print("\n✅ skills/ — дубликат (все файлы есть в .agents/)")
