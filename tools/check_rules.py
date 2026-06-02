import hashlib
from pathlib import Path

def get_hash(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

file1 = "rules/ignore-patterns.md"
file2 = ".agents/rules/ignore-patterns.md"

hash1 = get_hash(file1)
hash2 = get_hash(file2)

print(f"rules/ignore-patterns.md:         {hash1}")
print(f".agents/rules/ignore-patterns.md: {hash2}")
print("✅ ИДЕНТИЧНЫ" if hash1 == hash2 else "❌ РАЗНЫЕ")
