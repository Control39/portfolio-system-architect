#!/bin/bash
# agent_menu.sh - Главное меню агента

cd /c/repo
source .venv/Scripts/activate

show_menu() {
    echo ""
    echo "=================================================="
    echo "  🤖 ПОЛНОМЕЧИЯ АГЕНТА - Главное меню"
    echo "=================================================="
    echo ""
    echo "  АНАЛИЗ:"
    echo "  1. 📊 Полный анализ репозитория (DDD)"
    echo "  2. 📊 Быстрый анализ проекта"
    echo "  3. 🔍 Проверка зависимостей"
    echo ""
    echo "  САМОАНАЛИЗ:"
    echo "  30. 🪞 Анализ самого агента"
    echo "  31. 📊 Показать отчет самоанализа"
    echo "  32. ⚡ Быстрый самоанализ"
    echo ""
    echo "  DDD АНАЛИЗ:"
    echo "  20. 🏗️  Полный DDD анализ репозитория"
    echo "  21. 🔗 Показать зависимости между сервисами"
    echo "  22. 🐛 Показать архитектурные проблемы"
    echo "  23. 📂 Анализ конкретного домена"
    echo ""
    echo "  ДРУГИЕ:"
    echo "  99. 🔄 Обновить списки файлов"
    echo "  0. 🚪 Выход"
    echo ""
}

show_menu

while true; do
    echo ""
    read -p "Выберите действие (0-32): " choice

    case $choice in
        1)
            echo ""
            echo "📊 Запуск полного анализа репозитория..."
            echo "=================================================="
            python scripts/analyze_dependencies.py
            ;;
        2)
            echo ""
            echo "📊 Запуск быстрого анализа..."
            echo "=================================================="
            python scripts/run_project_scanner.py
            ;;
        3)
            echo ""
            echo "🔍 Проверка зависимостей..."
            echo "=================================================="
            python scripts/analyze_dependencies.py --quick
            ;;
        30)
            echo ""
            echo "🪞 Запуск самоанализа агента..."
            echo "=================================================="
            python scripts/agent_self_analyze.py
            ;;
        31)
            echo ""
            echo "📊 Показ отчета самоанализа..."
            echo "=================================================="
            if [ -f "agent_self_analysis_report.txt" ]; then
                cat agent_self_analysis_report.txt
            else
                echo "❌ Отчет не найден. Запустите самоанализ (пункт 30)"
            fi
            ;;
        32)
            echo ""
            echo "⚡ Быстрый самоанализ агента..."
            echo "=================================================="
            python scripts/agent_self_analyze_quick.py
            ;;
        20)
            echo ""
            echo "🏗️  Запуск полного DDD анализа..."
            echo "=================================================="
            python scripts/ddd_analyzer.py .
            ;;
        21)
            echo ""
            echo "🔗 Показ зависимостей..."
            echo "=================================================="
            python scripts/ddd_show_dependencies.py
            ;;
        22)
            echo ""
            echo "🐛 Показ архитектурных проблем..."
            echo "=================================================="
            python scripts/ddd_show_issues.py
            ;;
        23)
            echo ""
            echo "🏗️  Анализ конкретного домена..."
            echo "=================================================="
            echo ""
            echo "Доступные домены:"
            ls -la apps/ | grep ^d | awk '{print "   - " $9}'
            echo ""
            read -p "Введите имя домена: " domain
            python scripts/ddd_analyze_context.py "$domain"
            ;;
        99)
            echo ""
            echo "🔄 Обновление списков файлов..."
            echo "=================================================="
            echo "Done"
            ;;
        0)
            echo ""
            echo "👋 До свидания!"
            echo "=================================================="
            break
            ;;
        *)
            echo ""
            echo "❌ Неверный выбор. Попробуйте снова."
            ;;
    esac
done
