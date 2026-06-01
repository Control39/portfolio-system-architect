#!/bin/bash
# Настройка Ollama для локальных AI моделей

echo "🚀 Настройка Ollama для локальных AI моделей"
echo "============================================"

# Проверка установки Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama не установлен. Устанавливаю..."

    # Установка Ollama (Linux/macOS)
    curl -fsSL https://ollama.com/install.sh | sh

    echo "✅ Ollama установлен"
else
    echo "✅ Ollama уже установлен"
fi

# Запуск Ollama
echo "🔄 Запуск Ollama..."
ollama serve &

sleep 3

# Проверка доступности
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama запущен"
else
    echo "❌ Не удалось запустить Ollama"
    exit 1
fi

# Список доступных моделей
echo ""
echo "📦 Проверка доступных моделей..."
ollama list

# Если нет моделей, скачиваем
MODELS=$(ollama list | wc -l)
if [ "$MODELS" -lt 2 ]; then
    echo ""
    echo "📥 Скачивание локальных моделей..."

    echo "  • llama3.2 (7B, быстрый)"
    ollama pull llama3.2

    echo "  • mistral (7B, сбалансированный)"
    ollama pull mistral

    echo "  • codellama (7B, для кода)"
    ollama pull codellama

    echo "✅ Модели скачаны"
else
    echo "✅ Модели уже скачаны"
fi

# Проверка
echo ""
echo "📊 Итоговые модели:"
ollama list

echo ""
echo "✅ Ollama готов к работе!"
echo ""
echo "Команды:"
echo "  ollama run llama3.2     - Запустить модель"
echo "  ollama list             - Список моделей"
echo "  ollama pull <model>     - Скачать модель"
echo "  ollama rm <model>       - Удалить модель"
echo ""
echo "API эндпоинт: http://localhost:11434"
