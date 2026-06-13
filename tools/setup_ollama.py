#!/usr/bin/env python3
"""
Запуск Ollama сервера и скачивание модели
"""

import subprocess
import sys
import time

print("=" * 60)
print("🤖 Подключение Cognitive Agent к Ollama")
print("=" * 60)

# 1. Запуск Ollama сервера
print("\n🚀 Запуск Ollama сервера...")
try:
    # Запуск в фоне
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("   ✅ Ollama сервер запущен")
except FileNotFoundError:
    print("   ❌ Ollama не найдена. Установите через: winget install ollama")
    sys.exit(1)

# Ждём 5 секунд для запуска сервера
print("   ⏳ Ожидание запуска сервера (5 сек)...")
time.sleep(5)

# 2. Проверка доступности
print("\n🔍 Проверка доступности Ollama...")
try:
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("   ✅ Ollama доступна")
    else:
        print("   ⚠️  Ошибка: ", result.stderr[:100])
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    sys.exit(1)

# 3. Скачивание модели
print("\n📥 Скачивание модели llama3:8b (около 4.7 ГБ)...")
print("   ⚠️  Это может занять 5-15 минут в зависимости от скорости интернета")
print("   💡 Можно использовать альтернативу: gemma:7b (меньше, но слабее)")

choice = input("\nКакую модель скачать? (llama3/gemma): ").strip().lower()
model = "llama3:8b" if choice in ["llama3", "llama3:8b", ""] else "gemma:7b"

print(f"\n📦 Скачивание {model}...")
try:
    result = subprocess.run(["ollama", "pull", model], check=True, text=True)
    print(f"   ✅ Модель {model} успешно скачана!")
except subprocess.CalledProcessError as e:
    print(f"   ❌ Ошибка скачивания: {e}")
    sys.exit(1)

# 4. Проверка
print("\n🔍 Проверка установленной модели...")
result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
print("\nУстановленные модели:")
print(result.stdout)

# 5. Тестовый запрос
print("\n🧪 Тестовый запрос к модели...")
prompt = "Привет! Ты локальная LLM. Кратко ответь: что такое Cognitive Agent?"
print(f"   Вопрос: {prompt}")

try:
    result = subprocess.run(["ollama", "run", model, prompt], capture_output=True, text=True, timeout=30)
    print(f"   Ответ:\n{result.stdout[:500]}")
except Exception as e:
    print(f"   ⚠️  Ошибка теста: {e}")

print("\n" + "=" * 60)
print("✅ Ollama подключена и готова к работе!")
print("=" * 60)
print("\n💡 Теперь Cognitive Agent может использовать:")
print("   - Основную модель: GigaChat (если настроен)")
print(f"   - Fallback: {model} (локальная)")
print("\nСледующий шаг: Закоммитить изменения и протестировать агент")
