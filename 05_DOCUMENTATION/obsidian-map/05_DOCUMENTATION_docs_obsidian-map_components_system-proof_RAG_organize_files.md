# Components System Proof Rag Organize Files

- **Путь**: `05_DOCUMENTATION\docs\obsidian-map\components_system-proof_RAG_organize_files.md`
- **Тип**: .MD
- **Размер**: 898 байт
- **Последнее изменение**: 2026-03-12 11:25:17

## Превью

```
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
    $Timestamp = Get-Da
... (файл продолжается)
```
