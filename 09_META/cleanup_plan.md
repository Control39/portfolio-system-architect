# План очистки технического мусора и дубликатов

## Файлы для удаления

### Дубликаты README.md
- components/README.md (будет заменен новой структурой)
- components/arch-compass-framework/README.md (содержимое перенесено в новую структуру)
- components/it-compass/README.md (содержимое перенесено в новую структуру)
- components/career-development-system/README.md (содержимое перенесено в новую структуру)
- components/portfolio-organizer/README.md (содержимое перенесено в новую структуру)
- components/system-proof/README.md (содержимое перенесено в новую структуру)
- components/thought-architecture/README.md (содержимое перенесено в новую структуру)

### Технический мусор
- .gitignore (будет заменен новым, более точным файлом)
- compare-it-compass-versions.ps1 (вспомогательный скрипт, больше не нужен)
- component_versions_map.md (промежуточный файл, больше не нужен)
- tem-architect.txt (временный файл)
- unified_structure_plan.md (промежуточный файл, больше не нужен)
- ARCHITECTURE.md (дублирует cognitive-architect-manifesto/05_MANIFEST/ARCHITECTURE.md)
- templates/ (каталог с шаблонами, больше не нужен)
- .sourcecraft/ (каталог с настройками, если содержит только стандартные файлы)

### Служебные файлы редакторов
- .vscode/ (если существует)
- *.swp (файлы резервных копий vim)
- *~ (файлы резервных копий)
- Thumbs.db
- .DS_Store

## Файлы для перемещения/объединения

### Конфигурационные файлы
- configs/ (объединить все конфигурационные файлы в новую структуру)
- requirements.txt (переместить в соответствующий раздел новой структуры)

### Скрипты
- scripts/ (объединить все скрипты в новую структуру)
- components/cloud-reason/scripts/ (переместить в новую структуру)
- components/system-proof/RAG/ (переместить в новую структуру)

## Файлы для сохранения
Все файлы, которые не попадают под критерии удаления, должны быть сохранены и при необходимости перемещены в новую структуру.