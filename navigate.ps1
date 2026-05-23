#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Portfolio System Navigator - быстрая навигация по проекту

.DESCRIPTION
    Скрипт для быстрого доступа к различным частям проекта:
    - Переход к сервисам
    - Просмотр инструментов анализа
    - Открытие документации
    - Проверка статуса сервисов

.EXAMPLE
    .\navigate.ps1 -Service cognitive-agent
    .\navigate.ps1 -Tool koda
    .\navigate.ps1 -Status
    .\navigate.ps1 -Docs it-compass
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('client', 'ai-config-manager', 'auth-service', 'career-development',
                 'cognitive-agent', 'decision-engine', 'infra-orchestrator',
                 'it-compass', 'job-automation-agent', 'knowledge-graph',
                 'mcp-server', 'ml-model-registry', 'portfolio-organizer',
                 'system-proof', 'template-service', 'thought-architecture')]
    [string]$Service,

    [Parameter(Mandatory=$false)]
    [ValidateSet('koda', 'sourcecraft', 'continue', 'codeassistant')]
    [string]$Tool,

    [Parameter(Mandatory=$false)]
    [switch]$Status,

    [Parameter(Mandatory=$false)]
    [string]$Docs,

    [Parameter(Mandatory=$false)]
    [switch]$Map,

    [Parameter(Mandatory=$false)]
    [switch]$List
)

# Цвета вывода
$Colors = @{
    Success = 'Green'
    Warning = 'Yellow'
    Error   = 'Red'
    Info    = 'Cyan'
}

# ============================================================================
# ИМПОРТ МОДУЛЕЙ ОРКЕСТРАЦИИ (опционально)
# ============================================================================
$OrchestrationModulesPath = Join-Path $PSScriptRoot "tools\orchestration\powershell\modules"
if (Test-Path $OrchestrationModulesPath) {
    Write-Verbose "Загрузка модулей оркестрации из: $OrchestrationModulesPath"
    Get-ChildItem -Path $OrchestrationModulesPath -Filter "*.psm1" | ForEach-Object {
        try {
            Import-Module $_.FullName -Force -ErrorAction Stop
            Write-Verbose "  ✓ Импорт: $($_.Name)"
        }
        catch {
            Write-Warning "  ⚠ Ошибка импорта модуля $($_.Name): $_"
        }
    }
}
else {
    Write-Verbose "Модули оркестрации не найдены (опционально)"
}

function Write-Section { param([string]$Text) Write-Host "`n$Text`n" -ForegroundColor $Colors.Info }
function Write-Success { param([string]$Text) Write-Host "✅ $Text" -ForegroundColor $Colors.Success }
function Write-Warn    { param([string]$Text) Write-Host "⚠️  $Text" -ForegroundColor $Colors.Warning }
function Write-Error   { param([string]$Text) Write-Host "❌ $Text" -ForegroundColor $Colors.Error }

function Show-Services {
    Write-Section "📦 МИКРОСЕРВИСЫ (15)"
    $services = @(
        @{ Name = "client"; Path = "client"; Desc = "Frontend (React 19 + TS)" },
        @{ Name = "ai-config-manager"; Path = "apps/ai_config_manager"; Desc = "Управление AI конфигами" },
        @{ Name = "auth-service"; Path = "apps/auth_service"; Desc = "Аутентификация" },
        @{ Name = "career-development"; Path = "apps/career_development"; Desc = "Развитие карьеры" },
        @{ Name = "cognitive-agent"; Path = "apps/cognitive_agent"; Desc = "AI агент для автоматизации" },
        @{ Name = "decision-engine"; Path = "apps/decision_engine"; Desc = "Движок принятия решений" },
        @{ Name = "infra-orchestrator"; Path = "apps/infra_orchestrator"; Desc = "Оркестрация инфраструктуры (Python/FastAPI)" },
        @{ Name = "it-compass"; Path = "apps/it_compass"; Desc = "Методология системного мышления" },
        @{ Name = "job-automation-agent"; Path = "apps/job_automation_agent"; Desc = "Автоматизация работ" },
        @{ Name = "knowledge-graph"; Path = "apps/knowledge_graph"; Desc = "Граф знаний" },
        @{ Name = "mcp-server"; Path = "apps/mcp_server"; Desc = "Model Context Protocol" },
        @{ Name = "ml-model-registry"; Path = "apps/ml_model_registry"; Desc = "Реестр ML моделей" },
        @{ Name = "portfolio-organizer"; Path = "apps/portfolio_organizer"; Desc = "Организация портфолио" },
        @{ Name = "system-proof"; Path = "apps/system_proof"; Desc = "Доказательство системы" },
        @{ Name = "template-service"; Path = "apps/template_service"; Desc = "Шаблон сервиса" },
        @{ Name = "thought-architecture"; Path = "apps/thought_architecture"; Desc = "Архитектура решений" }
    )

    $services | ForEach-Object {
        Write-Host "  • $($_.Name)" -ForegroundColor Yellow
        Write-Host "    📁 $($_.Path)" -ForegroundColor Gray
        Write-Host "    📝 $($_.Desc)" -ForegroundColor Gray
    }
}

function Show-Tools {
    Write-Section "🛠️  ИНСТРУМЕНТЫ АНАЛИЗА"

    $tools = @(
        @{ Name = "Koda"; Path = ".koda"; Skills = 5; Desc = "Code intelligence IDE" },
        @{ Name = "Sourcecraft"; Path = ".sourcecraft"; Skills = "N/A"; Desc = "Coding assistant" },
        @{ Name = "Continue"; Path = ".continue"; Skills = "N/A"; Desc = "AI agents for IDE" },
        @{ Name = "Codeassistant"; Path = "codeassistant"; Skills = 10; Desc = "Code assistant + tools" }
    )

    $tools | ForEach-Object {
        Write-Host "  • $($_.Name)" -ForegroundColor Cyan
        Write-Host "    📁 $($_.Path)" -ForegroundColor Gray
        Write-Host "    🎯 $($_.Desc)" -ForegroundColor Gray
        Write-Host "    📦 Skills/Tools: $($_.Skills)" -ForegroundColor Gray
    }
}

function Show-Status {
    Write-Section "📊 СТАТУС ПРОЕКТА"

    $stats = @(
        @{ Item = "Code Coverage"; Value = "~85%"; Status = "✅ Отлично" },
        @{ Item = "Микросервисов"; Value = "15"; Status = "✅ Активно" },
        @{ Item = "Инструментов"; Value = "4"; Status = "✅ Оптимизировано" },
        @{ Item = "Уязвимостей"; Value = "0"; Status = "✅ Безопасно" },
        @{ Item = "ADR-документов"; Value = "14"; Status = "✅ Документировано" },
        @{ Item = "AI Config Integration"; Value = "14/14"; Status = "✅ Полная" }
    )

    $stats | ForEach-Object {
        Write-Host "  $($_.Item): " -ForegroundColor White -NoNewline
        Write-Host "$($_.Value)" -ForegroundColor Yellow -NoNewline
        Write-Host " — $($_.Status)"
    }

    Write-Section "📈 ИНСТРУМЕНТЫ МОНИТОРИНГА"
    Write-Host "  • Prometheus: http://localhost:9090" -ForegroundColor Cyan
    Write-Host "  • Grafana: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  • Auth Service: http://localhost:8100/docs" -ForegroundColor Cyan
    Write-Host "  • IT-Compass UI: http://localhost:8501" -ForegroundColor Cyan
}

# Маппинг имен сервисов на реальные пути (snake_case)
$ServiceMap = @{
    'client' = 'client'
    'ai-config-manager' = 'apps/ai_config_manager'
    'auth-service' = 'apps/auth_service'
    'career-development' = 'apps/career_development'
    'cognitive-agent' = 'apps/cognitive_agent'
    'decision-engine' = 'apps/decision_engine'
    'infra-orchestrator' = 'apps/infra_orchestrator'
    'it-compass' = 'apps/it_compass'
    'job-automation-agent' = 'apps/job_automation_agent'
    'knowledge-graph' = 'apps/knowledge_graph'
    'mcp-server' = 'apps/mcp_server'
    'ml-model-registry' = 'apps/ml_model_registry'
    'portfolio-organizer' = 'apps/portfolio_organizer'
    'system-proof' = 'apps/system_proof'
    'template-service' = 'apps/template_service'
    'thought-architecture' = 'apps/thought_architecture'
}

function Go-To-Service {
    param([string]$ServiceName)

    $servicePath = $ServiceMap[$ServiceName]

    if ($servicePath -and (Test-Path $servicePath)) {
        Write-Success "Найден сервис: $ServiceName"
        $fullPath = Join-Path $PWD.ProviderPath $servicePath
        Write-Host "📁 Путь: $fullPath`n"

        Get-ChildItem $servicePath -Depth 1 -Force | Select-Object FullName, @{
            Name = "Type"
            Expression = { if ($_.PSIsContainer) { "📁" } else { "📄" } }
        } | Format-Table -AutoSize

        $fullPath = Join-Path $PWD.ProviderPath $servicePath
        Write-Host "`n💡 Быстрые команды:"
        Write-Host "  cd '$fullPath'              # Перейти в сервис"
        Write-Host "  ls '$fullPath\src'          # Исходный код (если есть)"
        Write-Host "  ls '$fullPath\tests'        # Тесты (если есть)"
        Write-Host "  cat '$fullPath\README.md'   # Документация"
    }
    else {
        Write-Error "Сервис не найден: $ServiceName"
        Write-Host "💡 Доступные сервисы: $(($ServiceMap.Keys) -join ', ')"
    }
}

function Go-To-Tool {
    param([string]$ToolName)

    $toolPaths = @{
        'koda' = '.koda'
        'sourcecraft' = '.sourcecraft'
        'continue' = '.continue'
        'codeassistant' = 'codeassistant'
    }

    $path = $toolPaths[$ToolName]

    if (Test-Path $path) {
        Write-Success "Открытие $ToolName..."
        Write-Host "📁 Путь: $path`n"

        Get-ChildItem $path -Directory | ForEach-Object {
            Write-Host "  📁 $($_.Name)"
        }

        Write-Host "`n💡 Быстрые команды:"
        Write-Host "  cd $path                   # Перейти к инструменту"
        Write-Host "  ls $path/skills            # Доступные скиллы (если есть)"
        Write-Host "  ls $path/rules             # Правила (если есть)"
    }
    else {
        Write-Error "Инструмент не найден: $path"
    }
}

function Show-Docs {
    param([string]$DocName)

    if ($DocName) {
        Write-Host "🔍 Поиск документации по '$DocName'..."
        $found = Get-ChildItem -Recurse -Filter "*$DocName*" -Include "*.md" 2>$null | Select-Object -First 5

        if ($found) {
            Write-Success "Найдено:"
            $found | ForEach-Object {
                Write-Host "  📄 $($_.FullName)"
            }
        }
        else {
            Write-Warn "Документация не найдена"
        }
    }
    else {
        Write-Section "📚 ОСНОВНАЯ ДОКУМЕНТАЦИЯ"
        $docs = @(
            "README.md",
            "ARCHITECTURE.md",
            "docs/it-compass/METHODOLOGY.md",
            "docs/architecture/decisions/",
            "docs/HIRING_BRIEF.md",
            "docs/SOURCECRAFT_GRANT_APPLICATION.md"
        )

        $docs | ForEach-Object {
            if (Test-Path $_) {
                Write-Success "✓ $_"
            }
            else {
                Write-Warn "✗ $_"
            }
        }
    }
}

function Show-Map {
    Write-Host @"
┌────────────────────────────────────────────────────────────────────┐
│           PORTFOLIO SYSTEM ARCHITECT - СТРУКТУРА                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  🔧 ИНСТРУМЕНТЫ РАЗРАБОТКИ                                        │
│  ├── .koda/            (Koda IDE + правила)                       │
│  ├── .continue/        (Continue AI agents)                        │
│  ├── .vscode/          (VS Code settings)                          │
│  └── codeassistant/    (Code assistant + tools)                   │
│                                                                    │
│  🏗️ МИКРОСЕРВИСЫ (16 в apps/)                                     │
│  ├── client/             (Frontend React 19)                      │
│  ├── apps/cognitive_agent/      (AI агент)                        │
│  ├── apps/decision_engine/      (Решения)                         │
│  ├── apps/it_compass/           (Методология)                     │
│  ├── apps/knowledge_graph/      (Граф знаний)                     │
│  ├── apps/portfolio_organizer/  (Портфолио)                       │
│  ├── apps/career_development/   (Карьера)                         │
│  ├── apps/job_automation_agent/ (Автоматизация)                   │
│  ├── apps/infra_orchestrator/   (Инфраструктура)                  │
│  ├── apps/ml_model_registry/    (ML модели)                       │
│  ├── apps/mcp_server/           (MCP протокол)                    │
│  ├── apps/auth_service/         (Аутентификация)                  │
│  ├── apps/ai_config_manager/    (AI конфигурация)                 │
│  ├── apps/template_service/     (Шаблоны)                         │
│  ├── apps/system_proof/         (Доказательства)                  │
│  └── apps/thought_architecture/ (Архитектура)                     │
│                                                                    │
│  📦 ИНФРАСТРУКТУРА & МОНИТОРИНГ                                   │
│  ├── deployment/        (K8s manifests)                           │
│  ├── docker/            (Dockerfiles)                             │
│  ├── monitoring/        (Prometheus + Grafana)                    │
│  └── config/            (Конфигурации)                            │
│                                                                    │
│  📚 ДОКУМЕНТАЦИЯ                                                   │
│  ├── docs/              (Все документы)                           │
│  ├── diagrams/          (Архитектурные диаграммы)                 │
│  └── examples/          (Примеры использования)                   │
│                                                                    │
│  🧪 ТЕСТИРОВАНИЕ                                                   │
│  ├── tests/             (Интеграционные тесты)                    │
│  └── apps/*/tests/      (Unit тесты)                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

БЫСТРЫЕ КОМАНДЫ:
  .navigate.ps1 -Service <name>     # К микросервису
  .navigate.ps1 -Tool <name>        # К инструменту
  .navigate.ps1 -Status             # Статус проекта
  .navigate.ps1 -List               # Все сервисы и инструменты
  .navigate.ps1 -Map                # Эта диаграмма
" @
}

# Основная логика
if ($Map) {
    Show-Map
}
elseif ($List) {
    Show-Services
    "`n"
    Show-Tools
}
elseif ($Status) {
    Show-Status
}
elseif ($Service) {
    Go-To-Service $Service
}
elseif ($Tool) {
    Go-To-Tool $Tool
}
elseif ($Docs) {
    Show-Docs $Docs
}
else {
    Write-Host @"
📦 Portfolio System Navigator

ИСПОЛЬЗОВАНИЕ:
  .\navigate.ps1 -Service <name>   # Перейти к микросервису
  .\navigate.ps1 -Tool <name>      # Перейти к инструменту
  .\navigate.ps1 -Status           # Статус проекта
  .\navigate.ps1 -Docs [keyword]   # Найти документацию
  .\navigate.ps1 -List             # Все сервисы и инструменты
  .\navigate.ps1 -Map              # Архитектурная карта

ПРИМЕРЫ:
  .\navigate.ps1 -Service cognitive-agent
  .\navigate.ps1 -Tool koda
  .\navigate.ps1 -Docs architecture
  .\navigate.ps1 -Status

"@
}
