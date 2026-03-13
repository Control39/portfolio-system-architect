# Compare It Compass Versions

- **Путь**: `07_TOOLS\scripts\scripts\compare-it-compass-versions.ps1`
- **Тип**: .PS1
- **Размер**: 1,276 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
#! /bin/powershell
Write-Host "🔍 Сравнение версий IT-Compass..." -ForegroundColor Yellow

$versions = @(
    @{Path = "additional/it-compass"; Name = "Main (current)"},
    @{Path = "additional/leadarchitect-ai-repos/ekaterina-kudelya-it-compass"; Name = "Ekaterina-Kudelya"},
    @{Path = "additional/leadarchitect-ai-repos/my-ecosystem/core/it-compass"; Name = "My-Ecosystem-Core"}
)

foreach ($v in $versions) {
    if (Test-Path $v.Path) {
        Write-Host "📁 Версия: $($v.Name) ($($v.Path))" -
... (файл продолжается)
```
