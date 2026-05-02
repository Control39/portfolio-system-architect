# System-Proof Module

Proof storage for GigaChain traces/CoT. Verification + Metadata Tagging.

System Proof - это система для исследования и подтверждения системной архитектуры.

## Описание

System Proof предоставляет инструменты для анализа, верификации и документирования системной архитектуры, включая функции для работы с ИИ, автоматизацию и исследование архитектурных решений.

## Основные компоненты

### Core Proof Storage
- **Proof Schema** - Схема для хранения доказательств и метаданных
- **Verification System** - Система верификации доказательств

### RAG (Retrieval-Augmented Generation)
- **Auto Upload Cycle** - Автоматическая загрузка документов (`scripts/rag/auto_upload_cycle.ps1`)
- **Document Processing** - Обработка документов (`scripts/rag/process_document.ps1`)
- **File Organization** - Организация файлов (`scripts/rag/organize_files.ps1`)

### IT Compass Integration
- **Local Folder Compass** - Локальная система отслеживания компетенций

### Documentation
- **Architecture Documentation** - Документация по архитектуре
- **User Guide** - Руководство пользователя
- **Process Documentation** - Документация по процессам

## Setup

```bash
cd apps/system-proof
pip install chromadb pydantic
```

## Usage

### Core Proof Storage
- Store verified inferences.
- Tags: `thought-architecture`, `system-thinking-level`, `source-link`.

**Metrics:** Verification accuracy >90%, Coverage 92%.

Integrates with GigaChain RAG (decision-engine).

### Автоматическая загрузка документов

Скрипт `auto_upload_cycle.ps1` автоматически загружает новые документы в систему:

```powershell
./scripts/rag/auto_upload_cycle.ps1
```

### Обработка документов

Скрипт `process_document.ps1` обрабатывает отдельные документы:

```powershell
./scripts/rag/process_document.ps1 -Path "path/to/document.pdf"
```

### Организация файлов

Скрипт `organize_files.ps1` организует файлы в структурированную систему:

```powershell
./scripts/rag/organize_files.ps1 -SourcePath "path/to/source" -DestinationPath "path/to/destination"
```

## Docker

```bash
docker build -t system-proof .
docker run -p 8005:8005 system-proof
```

## Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](LICENSE) для получения подробной информации.
