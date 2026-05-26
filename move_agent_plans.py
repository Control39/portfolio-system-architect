import os
import shutil
from pathlib import Path

ROOT = Path(r"C:\repo")

# Целевая папка
DEST_DIR = ROOT / ".codeassistant" / "plans"
DEST_DIR.mkdir(parents=True, exist_ok=True)

# Файлы для переноса (агент-планы, не проект-планы)
FILES_TO_MOVE = [
    "AGENT_QUICK_START.md",
    "INTEGRATION_PLAN_FOR_AGENT.md",  # Если существует
]

print("🚀 Перенос планов агентов в .codeassistant/plans/")

for filename in FILES_TO_MOVE:
    src = ROOT / filename
    if src.exists():
        dst = DEST_DIR / filename
        shutil.move(str(src), str(dst))
        print(f"✅ {filename} → .codeassistant/plans/")
    else:
        print(f"⚠️  Не найдено: {filename}")

# Проверка
print("\n📁 Содержимое .codeassistant/plans/:")
for f in DEST_DIR.iterdir():
    print(f"   - {f.name}")

print("\n✅ Готово!")
