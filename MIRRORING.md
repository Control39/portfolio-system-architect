# MIRRORING.md

## Цель
Автоматически синхронизировать репозиторий **SourceCraft** → **GitHub**,  
чтобы обеспечить публичный доступ к коду, реплицировать метаданные и поддерживать  
прозрачность для грантовой комиссии.

## Текущее состояние
- **SourceCraft репозиторий:** `leadarchitect-ai/portfolio-system-architect`
- **GitHub зеркало:** `Control39/cognitive-systems-architecture`
- **Основные синхронизированные ветки:** `main`, `blackboxai/job-automation-system`, `gh-pages`
- **Дополнительные ветки на GitHub:** `blackboxai/tree-v2`, `reorg-10-directions-2026-03-21` (требуют ручной синхронизации)
- **Механизмы:** встроенное mirroring SourceCraft + GitHub Actions workflow

## Способы синхронизации

### 1️⃣ Встроенное mirroring (основное, recommended для гранта)
- Настройки выполнены в UI SourceCraft → *Settings → Repository → Mirroring*.
- URL удалённого репозитория: `git@github.com:Control39/cognitive-systems-architecture.git`
- Синхронизируемые ветки: `main`, `blackboxai/job-automation-system`, `gh-pages`.
- Пуш происходит сразу после каждого коммита (latency < 5 сек).

### 2️⃣ GitHub Actions «Sync to GitHub Mirror»
- Файл `.github/workflows/sync-to-github.yml`.
- Запускается:
  - При пуше в ветки `main`, `blackboxai/job-automation-system`, `gh-pages`
  - Вручную (`workflow_dispatch`)
  - Ежедневно по расписанию (cron: '0 0 * * *')
- Выполняет полную синхронизацию всех веток и тегов (`git push --mirror`).
- Журнал запусков доступен в GitHub Actions → *Runs*.

## Почему оба подхода?
- **Primary** — быстрая синхронизация без дополнительного кода (важно для гранта).
- **Secondary** — резервное копирование и гарантия полной синхронизации всех веток (демонстрирует зрелость процесса).

## Доступ и безопасность
- SSH‑ключ для GitHub хранится в SourceCraft в разделе *Deploy Keys* (только read‑only на GitHub).
- `GITHUB_TOKEN` в GitHub имеет scope `repo` и используется автоматически в workflow.

## Мониторинг расхождений
Для проверки синхронизации можно выполнить:
```bash
git fetch origin
git fetch github
git diff origin/main github/main
```
Автоматическая проверка добавлена в workflow `sync-to-github.yml` (шаг сравнения хэшей).

## План обновления
- При добавлении новых веток в SourceCraft обновляем список в UI mirroring и в workflow‑файле.
- При необходимости добавить новые проверки (например, проверка лицензий) – добавляем шаг в workflow.
- Регулярно проверять наличие устаревших веток на GitHub и удалять их.

## Последние изменения
- **2026-03-24**: Обновлен workflow для полного зеркалирования всех веток
- **2026-03-24**: Исправлена документация, актуализированы URL и список веток
- **2026-03-24**: Добавлен ежедневный cron и мониторинг расхождений

*Последнее обновление документации:* 2026-03-24