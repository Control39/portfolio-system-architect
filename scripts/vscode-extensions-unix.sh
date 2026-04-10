#!/bin/bash
# Bash скрипт для управления расширениями VS Code на Linux/macOS
# Автоматическая установка, проверка и синхронизация расширений

set -euo pipefail

# Настройки
CONFIG_PATH="${1:-config/vscode/vscode-extensions.json}"
DRY_RUN=false
ACTION="check"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции логирования
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message"
}

log_info() {
    log "INFO" "$1"
}

log_warn() {
    log "WARNING" "${YELLOW}$1${NC}"
}

log_error() {
    log "ERROR" "${RED}$1${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$1${NC}"
}

# Проверка наличия VS Code
check_vscode_installed() {
    if command -v code &> /dev/null; then
        local version=$(code --version 2>/dev/null | head -1)
        log_info "VS Code обнаружен: $version"
        return 0
    else
        # Проверяем альтернативные пути
        local possible_paths=(
            "/usr/local/bin/code"
            "/usr/bin/code"
            "/opt/vscode/bin/code"
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        )
        
        for path in "${possible_paths[@]}"; do
            if [[ -f "$path" ]]; then
                log_info "VS Code найден по пути: $path"
                export CODE_CMD="$path"
                return 0
            fi
        done
        
        log_error "VS Code не найден. Установите VS Code и добавьте в PATH"
        return 1
    fi
}

# Получение команды VS Code
get_code_cmd() {
    if [[ -n "${CODE_CMD:-}" ]]; then
        echo "$CODE_CMD"
    elif command -v code &> /dev/null; then
        echo "code"
    else
        log_error "Команда VS Code не найдена"
        exit 1
    fi
}

# Получение установленных расширений
get_installed_extensions() {
    local code_cmd=$(get_code_cmd)
    $code_cmd --list-extensions 2>/dev/null || echo ""
}

# Установка расширения
install_extension() {
    local extension_id="$1"
    local code_cmd=$(get_code_cmd)
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Установка расширения: $extension_id"
        return 0
    fi
    
    log_info "Установка расширения: $extension_id"
    if $code_cmd --install-extension "$extension_id" --force 2>/dev/null; then
        log_success "Расширение установлено: $extension_id"
        return 0
    else
        log_warn "Не удалось установить расширение: $extension_id"
        return 1
    fi
}

# Удаление расширения
uninstall_extension() {
    local extension_id="$1"
    local code_cmd=$(get_code_cmd)
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Удаление расширения: $extension_id"
        return 0
    fi
    
    log_info "Удаление расширения: $extension_id"
    if $code_cmd --uninstall-extension "$extension_id" 2>/dev/null; then
        log_success "Расширение удалено: $extension_id"
        return 0
    else
        log_warn "Не удалось удалить расширение: $extension_id"
        return 1
    fi
}

# Загрузка конфигурации
load_config() {
    local config_path="$1"
    
    if [[ ! -f "$config_path" ]]; then
        log_error "Конфигурационный файл не найден: $config_path"
        return 1
    fi
    
    # Используем Python для парсинга JSON (более надежно, чем jq, который может отсутствовать)
    python3 -c "
import json, sys
try:
    with open('$config_path', 'r') as f:
        config = json.load(f)
    print('CONFIG_LOADED')
    
    # Выводим обязательные расширения
    if 'required' in config:
        for ext in config['required']:
            print(f'REQUIRED:{ext}')
    
    # Выводим исключенные расширения
    if 'excluded' in config:
        for ext in config['excluded']:
            print(f'EXCLUDED:{ext}')
            
except Exception as e:
    print(f'ERROR:{str(e)}')
    sys.exit(1)
" || {
        log_error "Ошибка при загрузке конфигурации"
        return 1
    }
}

# Парсинг вывода конфигурации
parse_config_output() {
    local output="$1"
    local -n required_ref="$2"
    local -n excluded_ref="$3"
    
    required_ref=()
    excluded_ref=()
    
    while IFS= read -r line; do
        if [[ "$line" == "REQUIRED:"* ]]; then
            required_ref+=("${line#REQUIRED:}")
        elif [[ "$line" == "EXCLUDED:"* ]]; then
            excluded_ref+=("${line#EXCLUDED:}")
        fi
    done <<< "$output"
}

# Проверка соответствия
check_compliance() {
    log_info "Проверка соответствия расширений..."
    
    local installed_extensions=$(get_installed_extensions)
    local config_output=$(load_config "$CONFIG_PATH")
    
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    local required=()
    local excluded=()
    parse_config_output "$config_output" required excluded
    
    # Проверка обязательных расширений
    local missing_required=()
    for ext in "${required[@]}"; do
        if ! echo "$installed_extensions" | grep -q "^${ext}$"; then
            missing_required+=("$ext")
        fi
    done
    
    # Проверка исключенных расширений
    local found_excluded=()
    for ext in "${excluded[@]}"; do
        if echo "$installed_extensions" | grep -q "^${ext}$"; then
            found_excluded+=("$ext")
        fi
    done
    
    # Расчет compliance score
    local total_required=${#required[@]}
    local installed_required=$((total_required - ${#missing_required[@]}))
    local compliance_score=100
    
    if [[ $total_required -gt 0 ]]; then
        compliance_score=$(echo "scale=2; $installed_required * 100 / $total_required" | bc)
    fi
    
    # Формирование отчета
    local total_installed=$(echo "$installed_extensions" | wc -l | tr -d ' ')
    
    echo "REPORT:"
    echo "TOTAL_INSTALLED:$total_installed"
    echo "REQUIRED_COUNT:$total_required"
    echo "INSTALLED_REQUIRED:$installed_required"
    echo "COMPLIANCE_SCORE:$compliance_score"
    echo "STATUS:$([[ ${#missing_required[@]} -eq 0 && ${#found_excluded[@]} -eq 0 ]] && echo "PASS" || echo "FAIL")"
    
    if [[ ${#missing_required[@]} -gt 0 ]]; then
        echo "MISSING_REQUIRED:"
        for ext in "${missing_required[@]}"; do
            echo "  - $ext"
        done
    fi
    
    if [[ ${#found_excluded[@]} -gt 0 ]]; then
        echo "FOUND_EXCLUDED:"
        for ext in "${found_excluded[@]}"; do
            echo "  - $ext"
        done
    fi
}

# Синхронизация расширений
sync_extensions() {
    log_info "Синхронизация расширений..."
    
    local installed_extensions=$(get_installed_extensions)
    local config_output=$(load_config "$CONFIG_PATH")
    
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    local required=()
    local excluded=()
    parse_config_output "$config_output" required excluded
    
    local installed_count=0
    local uninstalled_count=0
    local failed_count=0
    
    # Установка отсутствующих обязательных расширений
    for ext in "${required[@]}"; do
        if ! echo "$installed_extensions" | grep -q "^${ext}$"; then
            if install_extension "$ext"; then
                ((installed_count++))
            else
                ((failed_count++))
            fi
        fi
    done
    
    # Удаление исключенных расширений
    for ext in "${excluded[@]}"; do
        if echo "$installed_extensions" | grep -q "^${ext}$"; then
            if uninstall_extension "$ext"; then
                ((uninstalled_count++))
            else
                ((failed_count++))
            fi
        fi
    done
    
    log_info "Синхронизация завершена:"
    log_info "  Установлено: $installed_count"
    log_info "  Удалено: $uninstalled_count"
    log_info "  Ошибок: $failed_count"
}

# Генерация отчета
generate_report() {
    local report_output=$(check_compliance)
    
    echo -e "\n${CYAN}=== ОТЧЕТ О СООТВЕТСТВИИ РАСШИРЕНИЙ VS CODE ===${NC}"
    
    while IFS= read -r line; do
        case "$line" in
            TOTAL_INSTALLED:*)
                echo -e "Всего установлено расширений: ${WHITE}${line#TOTAL_INSTALLED:}${NC}"
                ;;
            REQUIRED_COUNT:*)
                echo -e "Обязательных расширений: ${WHITE}${line#REQUIRED_COUNT:}${NC}"
                ;;
            INSTALLED_REQUIRED:*)
                echo -e "Установлено обязательных: ${WHITE}${line#INSTALLED_REQUIRED:}${NC}"
                ;;
            COMPLIANCE_SCORE:*)
                local score="${line#COMPLIANCE_SCORE:}"
                local color=$GREEN
                if (( $(echo "$score < 70" | bc -l) )); then
                    color=$RED
                elif (( $(echo "$score < 90" | bc -l) )); then
                    color=$YELLOW
                fi
                echo -e "Оценка соответствия: ${color}$score%${NC}"
                ;;
            STATUS:*)
                local status="${line#STATUS:}"
                local color=$([ "$status" = "PASS" ] && echo "$GREEN" || echo "$RED")
                echo -e "Статус: ${color}$status${NC}"
                ;;
            MISSING_REQUIRED:*)
                echo -e "\n${YELLOW}Отсутствующие обязательные расширения:${NC}"
                ;;
            "  - "*)
                if [[ "$line" == "  - "* ]]; then
                    echo -e "  ${YELLOW}${line#  - }${NC}"
                fi
                ;;
            FOUND_EXCLUDED:*)
                echo -e "\n${RED}Найдены исключенные расширения:${NC}"
                ;;
        esac
    done <<< "$report_output"
    
    echo -e "${CYAN}=============================================${NC}\n"
}

# Парсинг аргументов
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config)
                CONFIG_PATH="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --install)
                ACTION="install"
                shift
                ;;
            --sync)
                ACTION="sync"
                shift
                ;;
            --check|--report)
                ACTION="check"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_warn "Неизвестный аргумент: $1"
                shift
                ;;
        esac
    done
}

# Показать справку
show_help() {
    echo "Использование: $0 [ОПЦИИ]"
    echo ""
    echo "Опции:"
    echo "  --config PATH    Путь к конфигурационному файлу (по умолчанию: config/vscode/vscode-extensions.json)"
    echo "  --dry-run        Режим предварительного просмотра (без реальных изменений)"
    echo "  --install        Установить отсутствующие обязательные расширения"
    echo "  --sync           Полная синхронизация (установить недостающие, удалить исключенные)"
    echo "  --check          Проверить соответствие (режим по умолчанию)"
    echo "  --report         Сгенерировать отчет о соответствии"
    echo "  --help           Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 --check"
    echo "  $0 --sync --dry-run"
    echo "  $0 --install --config my-config.json"
}

# Основная функция
main() {
    log_info "Запуск скрипта управления расширениями VS Code для Unix"
    log_info "Конфигурационный файл: $CONFIG_PATH"
    
    # Проверка VS Code
    if ! check_vscode_installed; then
        exit 1
    fi
    
    # Выполнение действия
    case "$ACTION" in
        "check")
            generate_report
            ;;
        "install")
            log_info "Режим установки обязательных расширений"
            local config_output=$(load_config "$CONFIG_PATH")
            local required=()
            local excluded=()
            parse_config_output "$config_output" required excluded
            
            local installed_extensions=$(get_installed_extensions)
            for ext in "${required[@]}"; do
                if ! echo "$installed_extensions" | grep -q "^${ext}$"; then
                    install_extension "$ext"
                fi
            done
            ;;
        "sync")
            sync_extensions
            generate_report
            ;;
    esac
    
    log_success "Скрипт завершен"
}

# Обработка аргументов и запуск
parse_args "$@"
main