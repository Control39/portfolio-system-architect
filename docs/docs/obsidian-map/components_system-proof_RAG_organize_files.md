# Organize Files

- **Путь**: `components\system-proof\RAG\organize_files.ps1`
- **Тип**: .PS1
- **Размер**: 3,337 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# Organize Files Script
# Скрипт организации файлов

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    [Parameter(Mandatory=$true)]
    [string]$DestinationPath,
    [switch]$IncludeSubdirectories
)

# Функция для логирования
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

# Проверка существования исходной папки
if (!(Test-Path $SourcePath)) {
    Write-Log "Ошибка: Исходная папк
... (файл продолжается)
```

