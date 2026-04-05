# Auto Upload Cycle

- **Путь**: `components\system-proof\RAG\auto_upload_cycle.ps1`
- **Тип**: .PS1
- **Размер**: 2,532 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# Auto Upload Cycle Script
# Скрипт автоматического цикла загрузки

param(
    [string]$WatchFolder = ".\documents\incoming",
    [string]$ProcessedFolder = ".\documents\processed",
    [int]$CheckInterval = 60
)

# Функция для логирования
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

# Создание необходимых папок
if (!(Test-Path $WatchFolder)) {
    New-Item -ItemType Directory -Path $WatchFolder
... (файл продолжается)
```

