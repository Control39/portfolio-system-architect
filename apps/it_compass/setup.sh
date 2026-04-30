#!/bin/bash

# IT Compass - Automated Setup Script
# Методология "Объективные маркеры компетенций"
# © 2025 Ekaterina Kudelya. CC BY-ND 4.0

set -e

echo "🧭 IT Compass - начата установка..."
echo "Методология: © 2025 Ekaterina Kudelya, CC BY-ND 4.0"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Найден Python $python_version"

echo "📦 Создание виртуального окружения..."
python3 -m venv compass_venv
source compass_venv/bin/activate

echo "🔄 Обновление pip..."
pip install --upgrade pip

echo "📚 Установка зависимостей..."
pip install -r requirements.txt

echo "📁 Создание структуры..."
mkdir -p src/data/markers docs tests examples

cat > src/data/user_progress.json << 'EOF'
{
  "completed_markers": [],
  "in_progress_markers": []
}
EOF

echo "✅ Установка завершена!"
echo "🚀 Запуск: python src/main.py"
echo "🧭 Добро пожаловать в IT Compass!"
