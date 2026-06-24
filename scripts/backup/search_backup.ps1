# search_backup.ps1 - Поиск ключевых компонентов в backup
# Использование: .\scripts\search_backup.ps1

$backupPath = "C:\Users\Z\Desktop\back"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Поиск компонентов в backup" -ForegroundColor Cyan
Write-Host "  Путь: $backupPath" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Проверяем, существует ли папка
if (-not (Test-Path $backupPath)) {
    Write-Host "❌ Папка не найдена: $backupPath" -ForegroundColor Red
    exit
}

# Паттерны для поиска
$searchPatterns = @(
    @{
        Name = "ChromaDB интеграция"
        Pattern = "chromadb\.Client|from chromadb|ChromaVectorStore"
        Files = "*.py"
    },
    @{
        Name = "E2E тесты"
        Pattern = "def test_e2e|test_full_lifecycle|test_integration"
        Files = "*.py"
    },
    @{
        Name = "ML модели (реальные)"
        Pattern = "RandomForest|LinearRegression|GradientBoosting|\.pkl|\.joblib"
        Files = "*.py"
    },
    @{
        Name = "Event bus / event-driven"
        Pattern = "asyncio\.Queue|event_bus|pubsub|EventBus"
        Files = "*.py"
    },
    @{
        Name = "ContextVar для FastAPI"
        Pattern = "from contextvars import ContextVar|ContextVar\("
        Files = "*.py"
    },
    @{
        Name = "Retry логика (tenacity)"
        Pattern = "@retry|from tenacity|wait_exponential"
        Files = "*.py"
    },
    @{
        Name = "API endpoints (не пустые)"
        Pattern = "@app\.(post|get|put|delete)"
        Files = "endpoints.py"
    },
    @{
        Name = "Валидация AI-ответов"
        Pattern = "_validate_ai_response|validate_response|sanitize_ai"
        Files = "*.py"
    },
    @{
        Name = "Autonomous Agent"
        Pattern = "class AutonomousCognitiveAgent"
        Files = "autonomous_agent.py"
    },
    @{
        Name = "Orchestrator"
        Pattern = "class CognitiveOrchestrator|class Orchestrator"
        Files = "orchestrator*.py"
    },
    @{
        Name = "Project Scanner"
        Pattern = "class ProjectScanner"
        Files = "project_scanner.py"
    },
    @{
        Name = "Guardrails конфиг"
        Pattern = "allowed_paths|blocked_patterns|safe_actions"
        Files = "guardrails.yaml"
    },
    @{
        Name = "GigaChat Bridge"
        Pattern = "class GigaChatBridge|gigachat_bridge"
        Files = "gigachat_bridge*.py"
    },
    @{
        Name = "Planner"
        Pattern = "class TaskPlanner|planner_main"
        Files = "planner*.py"
    },
    @{
        Name = "Learning System"
        Pattern = "class LearningSystem|learning_main"
        Files = "learning*.py"
    }
)

$results = @{}

foreach ($pattern in $searchPatterns) {
    Write-Host "🔍 Поиск: $($pattern.Name)..." -ForegroundColor Yellow

    $found = Get-ChildItem -Path $backupPath -Recurse -Include $pattern.Files -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "\\.venv|__pycache__|node_modules" } |
        Select-String -Pattern $pattern.Pattern -ErrorAction SilentlyContinue |
        Select-Object -First 3

    if ($found) {
        Write-Host "   ✅ Найдено: $($found.Count) совпадений" -ForegroundColor Green
        foreach ($match in $found) {
            $relPath = $match.Path -replace [regex]::Escape($backupPath), "."
            Write-Host "      📁 $relPath`:$($match.LineNumber)" -ForegroundColor Gray
        }
        $results[$pattern.Name] = @{
            Found = $true
            Count = $found.Count
            Paths = $found | ForEach-Object { $_.Path -replace [regex]::Escape($backupPath), "." }
        }
    } else {
        Write-Host "   ❌ Не найдено" -ForegroundColor Red
        $results[$pattern.Name] = @{
            Found = $false
            Count = 0
            Paths = @()
        }
    }
    Write-Host ""
}

# Итоговый отчёт
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ИТОГОВЫЙ ОТЧЁТ" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$foundCount = ($results.Values | Where-Object { $_.Found }).Count
$totalCount = $results.Count

Write-Host "Найдено компонентов: $foundCount из $totalCount`n" -ForegroundColor White

if ($foundCount -gt 0) {
    Write-Host "✅ Найденные компоненты:" -ForegroundColor Green
    foreach ($key in $results.Keys) {
        if ($results[$key].Found) {
            Write-Host "   • $key ($($results[$key].Count) совпадений)" -ForegroundColor Green
        }
    }

    Write-Host "`n❌ Отсутствующие компоненты:" -ForegroundColor Red
    foreach ($key in $results.Keys) {
        if (-not $results[$key].Found) {
            Write-Host "   • $key" -ForegroundColor Red
        }
    }

    Write-Host "`n💡 Рекомендация:" -ForegroundColor Yellow
    Write-Host "   Найденные компоненты можно перенести в основной репозиторий." -ForegroundColor Yellow
    Write-Host "   Сначала консолидируй то, что уже есть, потом допиши недостающее.`n" -ForegroundColor Yellow
} else {
    Write-Host "❌ Ничего не найдено в backup." -ForegroundColor Red
    Write-Host "   Возможно, все компоненты уже в основном репозитории или в другом месте.`n" -ForegroundColor Yellow
}

Write-Host "========================================`n" -ForegroundColor Cyan
