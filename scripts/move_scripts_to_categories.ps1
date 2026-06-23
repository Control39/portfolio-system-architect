# Скрипт для перемещения скриптов в папки по категориям

Write-Host "=== СТАРТ ПЕРЕМЕЩЕНИЯ СКРИПТОВ ===" -ForegroundColor Green

# Каталоги для скриптов
$scriptsDirs = @(
    "scripts/ai",
    "scripts/automation",
    "scripts/ci",
    "scripts/deployment",
    "scripts/dev",
    "scripts/diagnostics",
    "scripts/generators",
    "scripts/git",
    "scripts/linux",
    "scripts/management",
    "scripts/migration",
    "scripts/python",
    "scripts/security",
    "scripts/utils",
    "scripts/utils_legacy",
    "scripts/windows",
    ".scripts/personal"  # личные скрипты
)

# Создать папки
foreach ($dir in $scriptsDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Yellow
    }
}

# Переместить корневые файлы
$filesToMove = @(
    @{Source = "check_integrations.py"; Dest = "scripts/diagnostics/check_integrations.py"},
    @{Source = "test_fallback_fix.py"; Dest = "scripts/build/test/test_fallback_fix.py"}
)

# Создать папку build/test
if (-not (Test-Path "scripts/build/test")) {
    New-Item -ItemType Directory -Path "scripts/build/test" | Out-Null
    Write-Host "Created: scripts/build/test" -ForegroundColor Yellow
}

# Переместить корневые файлы
foreach ($file in $filesToMove) {
    if (Test-Path $file.Source) {
        Move-Item -Path $file.Source -Destination $file.Dest -Force
        Write-Host "Moved: $($file.Source) -> $($file.Dest)" -ForegroundColor Green
    }
}

# Список скриптов для перемещения в .scripts/personal (личные скрипты)
$personalScripts = @(
    "agent_self_analyze.py",
    "agent_self_analyze_quick.py",
    "agent_self_analyze.sh",
    "agent_self_analyze_quick.sh",
    "agent_menu.sh",
    "agent_status_check.py",
    "check_gigachat_token.py",
    "check_ports.py",
    "check_service_structure.py",
    "collect_metrics.py",
    "complete_strategic_analyzer.py",
    "cognitive_agent_chat.py",
    "ddd_analyzer.py",
    "ddd_show_dependencies.py",
    "ddd_show_issues.py",
    "generate_badges.py",
    "organize_repo_files.py",
    "run_cognitive_agent.py",
    "run_project_scanner.py",
    "simple_check.py",
    "simple_doc_audit_test.py",
    "strategic_analyzer_full.py",
    "test_ai_connection.py",
    "test_gigachat_connection.py",
    "update_agent_config.py",
    "update_readme_badges.py"
)

# Переместить личные скрипты в .scripts/personal
foreach ($script in $personalScripts) {
    $source = "scripts/$script"
    $dest = ".scripts/personal/$script"

    if (Test-Path $source) {
        if (-not (Test-Path ".scripts/personal")) {
            New-Item -ItemType Directory -Path ".scripts/personal" | Out-Null
        }
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "Moved to .scripts/personal: $script" -ForegroundColor Cyan
    }
}

Write-Host "=== ПЕРЕМЕЩЕНИЕ ЗАВЕРШЕНО ===" -ForegroundColor Green
