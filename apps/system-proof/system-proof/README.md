# System Proof

System Proof - это система для исследования и подтверждения системной архитектуры.

## Описание

System Proof предоставляет инструменты для анализа, верификации и документирования системной архитектуры, включая функции для работы с ИИ, автоматизацию и исследование архитектурных решений.

## Основные компоненты

### RAG (Retrieval-Augmented Generation)
- **Auto Upload Cycle** - Автоматическая загрузка документов
- **Document Processing** - Обработка документов
- **File Organization** - Организация файлов
- **Monitoring** - Мониторинг системы

### IT Compass Integration
- **Local Folder Compass** - Локальная система отслеживания компетенций

### Documentation
- **Architecture Documentation** - Документация по архитектуре
- **User Guide** - Руководство пользователя
- **Process Documentation** - Документация по процессам

## Использование

### Автоматическая загрузка документов

Скрипт `auto_upload_cycle.ps1` автоматически загружает новые документы в систему:

```powershell
./RAG/auto_upload_cycle.ps1
```

### Обработка документов

Скрипт `process_document.ps1` обрабатывает отдельные документы:

```powershell
./RAG/process_document.ps1 -Path "path/to/document.pdf"
```

### Организация файлов

Скрипт `organize_files.ps1` организует файлы в структурированную систему:

```powershell
./RAG/organize_files.ps1 -SourcePath "path/to/source" -DestinationPath "path/to/destination"
```

## Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](LICENSE) для получения подробной информации.
