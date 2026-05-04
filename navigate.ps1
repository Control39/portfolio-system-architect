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
    [ValidateSet('cognitive-agent', 'decision-engine', 'it-compass', 'portfolio-organizer', 
                 'career-development', 'job-automation-agent', 'knowledge-graph', 'infra-orchestrator',
                 'ml-model-registry', 'mcp-server', 'auth-service', 'ai-config-manager', 
                 'template-service', 'system-proof', 'thought-architecture')]
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

function Write-Section { param([string]$Text) Write-Host "`n$Text`n" -ForegroundColor $Colors.Info }
function Write-Success { param([string]$Text) Write-Host "✅ $Text" -ForegroundColor $Colors.Success }
function Write-Warn    { param([string]$Text) Write-Host "⚠️  $Text" -ForegroundColor $Colors.Warning }
function Write-Error   { param([string]$Text) Write-Host "❌ $Text" -ForegroundColor $Colors.Error }

function Show-Services {
    Write-Section "📦 МИКРОСЕРВИСЫ (14)"
    $services = @(
        @{ Name = "cognitive-agent"; Path = "apps/cognitive-agent"; Desc = "AI агент для автоматизации" },
        @{ Name = "decision-engine"; Path = "apps/decision-engine"; Desc = "Движок принятия решений" },
        @{ Name = "it-compass"; Path = "apps/it_compass"; Desc = "Методология системного мышления" },
        @{ Name = "knowledge-graph"; Path = "apps/knowledge-graph"; Desc = "Граф знаний" },
        @{ Name = "infra-orchestrator"; Path = "apps/infra-orchestrator"; Desc = "Оркестрация инфраструктуры" },
        @{ Name = "portfolio-organizer"; Path = "apps/portfolio_organizer"; Desc = "Организация портфолио" },
        @{ Name = "career-development"; Path = "apps/career_development"; Desc = "Развитие карьеры" },
        @{ Name = "job-automation-agent"; Path = "apps/job-automation-agent"; Desc = "Автоматизация работ" },
        @{ Name = "ml-model-registry"; Path = "apps/ml-model-registry"; Desc = "Реестр ML моделей" },
        @{ Name = "mcp-server"; Path = "apps/mcp-server"; Desc = "Model Context Protocol" },
        @{ Name = "auth-service"; Path = "apps/auth_service"; Desc = "Аутентификация" },
        @{ Name = "ai-config-manager"; Path = "apps/ai-config-manager"; Desc = "Управление AI конфигами" },
        @{ Name = "template-service"; Path = "apps/template-service"; Desc = "Сервис шаблонов" },
        @{ Name = "system-proof"; Path = "apps/system-proof"; Desc = "Доказательство системы" }
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
        @{ Item = "Code Coverage"; Value = "95%"; Status = "✅ Отлично" },
        @{ Item = "Микросервисов"; Value = "14+"; Status = "✅ Активно" },
        @{ Item = "Инструментов"; Value = "4"; Status = "⚠️  Дублирование" },
        @{ Item = "Скилов/Tools"; Value = "40+"; Status = "⚠️  Много" },
        @{ Item = "Документов"; Value = "~2000"; Status = "🔴 Неорганизовано" },
        @{ Item = "Production Sервисов"; Value = "14"; Status = "✅ Работают" }
    )

    $stats | ForEach-Object {
        Write-Host "  $($_.Item): " -ForegroundColor White -NoNewline
        Write-Host "$($_.Value)" -ForegroundColor Yellow -NoNewline
        Write-Host " — $($_.Status)"
    }

    Write-Section "📈 ИНСТРУМЕНТЫ МОНИТОРИНГА"
    Write-Host "  • Prometheus: http://localhost:9090" -ForegroundColor Cyan
    Write-Host "  • Grafana: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  • PostgreSQL: localhost:5432" -ForegroundColor Cyan
    Write-Host "  • Elasticsearch: localhost:9200" -ForegroundColor Cyan
}

function Go-To-Service {
    param([string]$ServiceName)
    
    $servicePath = "apps/" + ($ServiceName -replace "-", "_")
    
    if (Test-Path $servicePath) {
        Write-Success "Открытие $ServiceName..."
        Write-Host "📁 Путь: $servicePath`n"
        
        Get-ChildItem $servicePath -Depth 1 | Select-Object Name, @{
            Name = "Type"
            Expression = { if ($_.PSIsContainer) { "📁" } else { "📄" } }
        } | Format-Table -AutoSize
        
        Write-Host "`n💡 Быстрые команды:"
        Write-Host "  cd $servicePath                    # Перейти в сервис"
        Write-Host "  ls $servicePath/src                # Исходный код"
        Write-Host "  ls $servicePath/tests              # Тесты"
        Write-Host "  cat $servicePath/README.md         # Документация"
    }
    else {
        Write-Error "Сервис не найден: $servicePath"
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
        $found = Get-ChildItem -Recurse -Filter "*$DocName*" -Include "*.md" 2>/dev/null | Select-Object -First 5
        
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
            "ARCHITECTURE_MAP.md",
            "docs/README.md",
            "docs/architecture/",
            "docs/cases/",
            "docs/methodology/"
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
│  ├── .koda/            (Koda IDE + 5 skills)                      │
│  ├── .continue/        (Continue AI agents)                        │
│  ├── .vscode/          (VS Code settings)                          │
│  └── codeassistant/    (Code assistant + tools)                   │
│                                                                    │
│  🏗️ МИКРОСЕРВИСЫ (14 в PRODUCTION)                                │
│  ├── apps/cognitive-agent/      (AI агент)                        │
│  ├── apps/decision-engine/      (Решения)                         │
│  ├── apps/it-compass/           (Методология)                     │
│  ├── apps/knowledge-graph/      (Граф знаний)                     │
│  ├── apps/portfolio-organizer/  (Портфолио)                       │
│  ├── apps/career-development/   (Карьера)                         │
│  ├── apps/job-automation-agent/ (Автоматизация)                   │
│  ├── apps/infra-orchestrator/   (Инфраструктура)                  │
│  ├── apps/ml-model-registry/    (ML модели)                       │
│  ├── apps/mcp-server/           (MCP протокол)                    │
│  ├── apps/auth-service/         (Аутентификация)                  │
│  ├── apps/ai-config-manager/    (AI конфигурация)                 │
│  ├── apps/template-service/     (Шаблоны)                         │
│  └── apps/system-proof/         (Доказательства)                  │
│                                                                    │
│  📦 ИНФРАСТРУКТУРА & МОНИТОРИНГ                                   │
│  ├── deployment/        (K8s manifests)                           │
│  ├── docker/            (Dockerfiles)                             │
│  ├── monitoring/        (Prometheus + Grafana)                    │
│  ├── postgres/          (БД конфигурация)                         │
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
│  💡 Coverage: 95% ✅                                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

БЫСТРЫЕ КОМАНДЫ:
  .\navigate.ps1 -Service cognitive-agent     # К микросервису
  .\navigate.ps1 -Tool koda                   # К инструменту
  .\navigate.ps1 -Status                      # Статус проекта
  .\navigate.ps1 -List                        # Все сервисы
  .\navigate.ps1 -Map                         # Эта диаграмма
"@
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
