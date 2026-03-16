#! /bin/powershell
Write-Host "🔍 Сравнение версий IT-Compass..." -ForegroundColor Yellow

$versions = @(
    @{Path = "additional/it-compass"; Name = "Main (current)"},
    @{Path = "additional/leadarchitect-ai-repos/ekaterina-kudelya-it-compass"; Name = "Ekaterina-Kudelya"},
    @{Path = "additional/leadarchitect-ai-repos/my-ecosystem/core/it-compass"; Name = "My-Ecosystem-Core"}
)

foreach ($v in $versions) {
    if (Test-Path $v.Path) {
        Write-Host "📁 Версия: $($v.Name) ($($v.Path))" -ForegroundColor Cyan
        $files = Get-ChildItem -Path $v.Path -Recurse -File
        Write-Host "   📄 Файлы: $($files.Count)" -ForegroundColor Green

        # Выводим список файлов для визуального сравнения
        Write-Host "   Список файлов:" -ForegroundColor Gray
        foreach ($file in $files) {
            Write-Host "     - $($file.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Версия не найдена: $($v.Name) ($($v.Path))" -ForegroundColor Red
    }
}

Write-Host "💡 Сравните файлы вручную для выявления уникальных функций." -ForegroundColor Yellow
