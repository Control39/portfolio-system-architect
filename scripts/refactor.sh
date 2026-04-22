#!/bin/bash
# refactor.sh - Автоматическая реорганизация структуры проекта
# Автор: System Architect
# Версия: 2.0

set -e  # Останавливаем скрипт при любой ошибке
set -u  # Останавливаем при использовании неопределенной переменной

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- [НАСТРОЙКИ] ---
BACKUP_BRANCH="backup/before-refactor-$(date +%Y%m%d-%H%M%S)"
KEEP_APPS_CLOUD_REASON=true  # true - оставляем apps, false - оставляем src

# --- [ФУНКЦИИ] ---
log() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

confirm() {
    read -r -p "$1 [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Не найден Git репозиторий"
    fi
}

create_backup() {
    log "Создание резервной ветки: $BACKUP_BRANCH"
    git checkout -b "$BACKUP_BRANCH"
    success "Резервная ветка создана"
    git checkout main 2>/dev/null || git checkout master 2>/dev/null || true
}

run_tests() {
    log "Запуск базовых проверок"
    
    # Проверяем синтаксис Python файлов
    local py_errors=0
    while IFS= read -r file; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            warning "Синтаксическая ошибка в $file"
            ((py_errors++))
        fi
    done < <(find . -name "*.py" -not -path "./.venv/*" -not -path "./.git/*" -not -path "./.archive/*" | head -20)
    
    if [ $py_errors -eq 0 ]; then
        success "Синтаксис Python корректен (выборочная проверка)"
    else
        warning "Найдено $py_errors потенциальных проблем"
    fi
}

# --- [ОСНОВНАЯ ЛОГИКА] ---

main() {
    echo -e "${GREEN}🚀 Начинаем рефакторинг структуры проекта${NC}"
    echo "Время: $(date)"
    echo "Резервная ветка: $BACKUP_BRANCH"
    echo ""
    
    check_git_repo
    
    if ! confirm "Создать резервную ветку перед началом?"; then
        warning "Продолжаем без резервной ветки"
    else
        create_backup
    fi
    
    # --- ШАГ 1: ОЧИСТКА CLOUD-REASON ---
    log "ШАГ 1: Работа с дубликатами cloud_reason"
    
    # Проверяем существование обеих версий
    if [ ! -d "src/cloud_reason" ] && [ ! -d "apps/cloud-reason/cloud_reason" ]; then
        warning "Папки cloud_reason не найдены, пропускаем шаг"
    else
        if [ "$KEEP_APPS_CLOUD_REASON" = true ]; then
            log "Выбрано: Основной код в apps/cloud-reason"
            
            if [ -d "src/cloud_reason" ]; then
                # Создаем архив
                mkdir -p .archive/src_cloud_reason_$(date +%Y%m%d)
                
                # Копируем уникальные файлы
                if [ -f "src/cloud_reason/api/reasoning_api.py" ] && [ ! -f "apps/cloud-reason/cloud_reason/api/reasoning_api.py" ]; then
                    cp -n src/cloud_reason/api/reasoning_api.py apps/cloud-reason/cloud_reason/api/ 2>/dev/null && success "Добавлен reasoning_api.py"
                fi
                
                if [ -f "src/cloud_reason/configs/api-gateway.yaml" ] && [ ! -f "apps/cloud-reason/cloud_reason/configs/api-gateway.yaml" ]; then
                    cp -n src/cloud_reason/configs/api-gateway.yaml apps/cloud-reason/cloud_reason/configs/ 2>/dev/null && success "Добавлен api-gateway.yaml"
                fi
                
                if [ -f "src/cloud_reason/utils/logger.py" ] && [ ! -f "apps/cloud-reason/cloud_reason/utils/logger.py" ]; then
                    cp -n src/cloud_reason/utils/logger.py apps/cloud-reason/cloud_reason/utils/ 2>/dev/null && success "Добавлен logger.py"
                fi
                
                # Перемещаем остальное в архив
                warning "Перемещение src/cloud_reason в архив..."
                git mv src/cloud_reason/* .archive/src_cloud_reason_$(date +%Y%m%d)/ 2>/dev/null || mv src/cloud_reason/* .archive/src_cloud_reason_$(date +%Y%m%d)/
                rmdir src/cloud_reason 2>/dev/null || true
                
                success "src/cloud_reason очищен"
            else
                warning "src/cloud_reason не существует"
            fi
        else
            log "Выбрано: Основной код в src/cloud_reason"
            # Аналогичная логика для обратного варианта
            if [ -d "apps/cloud-reason" ]; then
                mkdir -p .archive/apps_cloud_reason_$(date +%Y%m%d)
                git mv apps/cloud-reason/* .archive/apps_cloud_reason_$(date +%Y%m%d)/ 2>/dev/null || true
                success "apps/cloud-reason перемещен в архив"
            fi
        fi
    fi
    
    # --- ШАГ 2: РАСПРЯМЛЕНИЕ SCRIPTS ---
    log "ШАГ 2: Устранение вложенности tools/scripts"
    
    # Находим все проблемные вложенности
    find tools -type d -name "scripts" -mindepth 2 2>/dev/null | while read -r nested_scripts; do
        warning "Найдена вложенность: $nested_scripts"
        
        if confirm "Обработать $nested_scripts?"; then
            parent_dir=$(dirname "$nested_scripts")
            # Перемещаем содержимое на уровень выше
            for item in "$nested_scripts"/*; do
                if [ -e "$item" ]; then
                    git mv "$item" "$parent_dir/" 2>/dev/null || mv "$item" "$parent_dir/"
                fi
            done
            rmdir "$nested_scripts" 2>/dev/null || true
            success "Обработано: $nested_scripts"
        fi
    done
    
    # Специальная обработка embedding_agent
    if [ -d "tools/scripts/scripts/python scripts/src/embedding_agent" ]; then
        log "Перемещение embedding_agent..."
        mkdir -p tools/ai_integration/embedding_agent
        git mv "tools/scripts/scripts/python scripts/src/embedding_agent"/* tools/ai_integration/embedding_agent/ 2>/dev/null || \
            mv "tools/scripts/scripts/python scripts/src/embedding_agent"/* tools/ai_integration/embedding_agent/
        
        # Очистка пустых папок
        rm -rf "tools/scripts/scripts/python scripts" 2>/dev/null || true
        rmdir "tools/scripts/scripts" 2>/dev/null || true
        
        success "embedding_agent перемещен в tools/ai_integration/"
    fi
    
    # --- ШАГ 3: СТАНДАРТИЗАЦИЯ APPS ---
    log "ШАГ 3: Унификация структуры приложений"
    
    for app_dir in apps/*/; do
        if [ -d "$app_dir" ]; then
            app_name=$(basename "$app_dir")
            log "Проверка: $app_name"
            
            # Проверка на дублирующийся src/src
            if [ -d "$app_dir/src/src" ]; then
                warning "$app_name: найдена вложенность src/src"
                if confirm "  Исправить структуру $app_name?"; then
                    mv "$app_dir/src/src/"* "$app_dir/src/" 2>/dev/null || true
                    rmdir "$app_dir/src/src"
                    success "$app_name: структура исправлена"
                fi
            fi
            
            # Проверка на отсутствие вложенной папки с именем приложения
            if [ ! -d "$app_dir/$app_name" ] && [ -d "$app_dir/src" ]; then
                warning "$app_name: нет стандартной структуры (нет $app_name/$app_name)"
                if confirm "  Создать структуру $app_name/$app_name?"; then
                    mkdir -p "$app_dir/$app_name"
                    mv "$app_dir/src/"* "$app_dir/$app_name/" 2>/dev/null || true
                    rmdir "$app_dir/src" 2>/dev/null || true
                    success "$app_name: стандартная структура создана"
                fi
            fi
            
            # Создаем недостающие стандартные папки
            for standard_dir in api utils models services; do
                if [ ! -d "$app_dir/$app_name/$standard_dir" ] && [ -d "$app_dir/$app_name" ]; then
                    if [ -d "$app_dir/$standard_dir" ]; then
                        # Папка есть на неправильном уровне
                        warning "$app_name: $standard_dir находится не на своем месте"
                        mv "$app_dir/$standard_dir" "$app_dir/$app_name/" 2>/dev/null || true
                        success "$app_name: $standard_dir перемещен"
                    else
                        # Создаем пустую папку как напоминание
                        mkdir -p "$app_dir/$app_name/$standard_dir"
                        echo "# $standard_dir for $app_name" > "$app_dir/$app_name/$standard_dir/__init__.py"
                        warning "$app_name: создана пустая папка $standard_dir (требуется наполнение)"
                    fi
                fi
            done
        fi
    done
    
    # --- ФИНАЛЬНЫЕ ПРОВЕРКИ ---
    log "Финальные проверки"
    run_tests
    
    # --- ИТОГО ---
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Рефакторинг успешно завершен!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "📊 Статистика изменений:"
    git status --short | wc -l | xargs echo "   Измененных файлов:"
    echo ""
    echo "💡 Следующие шаги:"
    echo "   1. Проверьте изменения: git diff"
    echo "   2. Запустите тесты: pytest"
    echo "   3. Если все хорошо: git add . && git commit -m 'refactor: restructure project'"
    echo "   4. Если проблемы: git checkout $BACKUP_BRANCH"
    echo ""
    
    if confirm "Показать git status?"; then
        git status
    fi
}

# --- ЗАПУСК ---
main "$@"