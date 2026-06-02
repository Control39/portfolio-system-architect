#!/usr/bin/env python3
"""
Анализатор логов когнитивного агента
Цель: Найти все логи, проанализировать маршрут, показать содержимое
"""
import os
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\repo")

print("=" * 70)
print("🔍 Анализатор логов когнитивного агента")
print("=" * 70)

# 1. Поиск всех директорий с логами
print("\n📂 Поиск директорий с логами...")
log_dirs = []
for name in ["logs", "log", "Logging"]:
    for dir_path in ROOT.rglob(name):
        if dir_path.is_dir():
            log_dirs.append(dir_path)
            print(f"   ✅ Найдено: {dir_path.relative_to(ROOT)}")

# 2. Поиск всех .log файлов
print("\n📄 Поиск .log файлов...")
log_files = list(ROOT.rglob("*.log"))
print(f"   Найдено {len(log_files)} .log файлов")

# 3. Поиск CSV файлов (метрики)
print("\n📊 Поиск CSV файлов (метрики)...")
csv_files = list(ROOT.rglob("*.csv"))
print(f"   Найдено {len(csv_files)} CSV файлов")

# 4. Детальный анализ директорий
print("\n" + "=" * 70)
print("📋 Детальный анализ директорий с логами")
print("=" * 70)

for log_dir in log_dirs[:10]:  # Первые 10
    print(f"\n📁 {log_dir.relative_to(ROOT)}")
    items = list(log_dir.iterdir())
    print(f"   Содержимое ({len(items)} элементов):")
    for item in items[:15]:  # Первые 15 элементов
        size = item.stat().st_size if item.is_file() else "-"
        item_type = "📄" if item.is_file() else "📁"
        print(f"   {item_type} {item.name:40s} {size:>10} байт")
    
    # Если файлов много, показать только последние
    if len(items) > 15:
        print(f"   ... и ещё {len(items) - 15} файлов")

# 5. Анализ .log файлов
print("\n" + "=" * 70)
print("📋 Детальный анализ .log файлов")
print("=" * 70)

for log_file in log_files[:20]:  # Первые 20
    print(f"\n📄 {log_file.relative_to(ROOT)}")
    try:
        size = log_file.stat().st_size
        print(f"   Размер: {size:,} байт")
        
        # Попробовать прочитать первые строки
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines(2000)  # Первые ~2KB
            print(f"   Первые 10 строк:")
            for i, line in enumerate(lines[:10], 1):
                print(f"     {i:2d}. {line.strip()[:80]}")
            if len(lines) > 10:
                print(f"     ... ({len(lines) - 10} строк не показано)")
    except Exception as e:
        print(f"   ❌ Ошибка чтения: {e}")

# 6. Анализ CSV файлов (метрики)
print("\n" + "=" * 70)
print("📊 Анализ CSV файлов (метрики)")
print("=" * 70)

for csv_file in csv_files[:10]:  # Первые 10
    print(f"\n📊 {csv_file.relative_to(ROOT)}")
    try:
        size = csv_file.stat().st_size
        print(f"   Размер: {size:,} байт")
        
        with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            print(f"   Строк: {len(lines)}")
            if lines:
                print(f"   Заголовок: {lines[0].strip()}")
                if len(lines) > 1:
                    print(f"   Пример данных:")
                    for line in lines[1:min(4, len(lines))]:
                        print(f"     {line.strip()[:100]}")
    except Exception as e:
        print(f"   ❌ Ошибка чтения: {e}")

# 7. Маршрут логов (куда они идут дальше)
print("\n" + "=" * 70)
print("🛣️ Маршрут логов (предполагаемый)")
print("=" * 70)

print("""
📝 Предположительный поток логов:

1. Генерация логов:
   apps/cognitive_agent/ → логи в консоль (stdout/stderr)
   .agents/ → логи в файлы (.agents/logs/)

2. Сбор метрик:
   .agents/logs/performance.csv → агрегация метрик (каждые 5 минут)

3. Загрузка в GitHub Actions:
   .agents/logs/ → upload-artifact → GitHub (retention: 7 дней)

4. Возможные дальнейшие пути:
   - Логи сохраняются в артефакты GitHub (7 дней хранения)
   - Метрики могут отправляться в мониторинг (если настроено)
   - Логи могут ротироваться/архивироваться

🔍 Где искать конфигурацию логирования:
   - .agents/config/*.yaml
   - apps/cognitive_agent/config/*.yaml
   - apps/cognitive_agent/src/logging_config.py
   - .koda/rules/logging.md
""")

# 8. Поиск конфигов логирования
print("\n🔍 Поиск конфигов логирования...")
config_files = []
for pattern in ["**/logging*.yaml", "**/logging*.yml", "**/logging*.json", "**/log_config*.py"]:
    config_files.extend(ROOT.rglob(pattern))

for config in config_files[:10]:
    print(f"   📄 {config.relative_to(ROOT)}")
    try:
        with open(config, "r", encoding="utf-8") as f:
            content = f.read(500)
            print(f"     {content[:200]}...")
    except Exception as e:
        print(f"     ❌ Ошибка чтения: {e}")

print("\n" + "=" * 70)
print("✅ Анализ завершён!")
print("=" * 70)
print("\n💡 Рекомендации:")
print("   1. Проверить .agents/logs/ для текущих логов")
print("   2. Проверить артефакты GitHub Actions (7 дней хранения)")
print("   3. Добавить детализированное логирование в коде агента (если нужно)")
print("   4. Настроить экспорт логов во внешнюю систему (если требуется)")
