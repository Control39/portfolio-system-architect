import hashlib
from pathlib import Path

def get_hash(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

files_to_check = [
    ("teacher/scripts/git_automation.py", ".agents/teacher/scripts/git_automation.py"),
    ("teacher/guides/README.md", ".agents/teacher/guides/README.md"),
    ("skills/caa-audit/SKILL.md", ".agents/skills/caa-audit/SKILL.md"),
    ("rules/ignore-patterns.md", ".agents/rules/ignore-patterns.md"),
]

print("Сравнение хэшей файлов (MD5):")
print("=" * 60)

for root_path, agents_path in files_to_check:
    try:
        hash1 = get_hash(root_path)
        hash2 = get_hash(agents_path)
        status = "✅ ИДЕНТИЧНЫ" if hash1 == hash2 else "❌ РАЗНЫЕ"
        print(f"{root_path:40} | {status}")
    except FileNotFoundError as e:
        print(f"{root_path:40} | ⚠️ Ошибка: {e}")
