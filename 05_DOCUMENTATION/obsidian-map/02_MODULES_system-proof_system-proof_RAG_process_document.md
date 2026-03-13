# Process Document

- **Путь**: `02_MODULES\system-proof\system-proof\RAG\process_document.ps1`
- **Тип**: .PS1
- **Размер**: 3,256 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# Process Document Script
# Скрипт обработки документов

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    [string]$OutputFolder = ".\documents\processed"
)

# Функция для логирования
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

# Проверка существования файла
if (!(Test-Path $Path)) {
    Write-Log "Ошибка: Файл не найден - $Path"
    exit 1
}

# Создание папки для вывода
if (!(Test
... (файл продолжается)
```
