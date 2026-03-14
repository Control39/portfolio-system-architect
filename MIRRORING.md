# MIRRORING.md

## Цель
Автоматически синхронизировать репозиторий **SourceCraft** → **GitHub**,
чтобы обеспечить публичный доступ к коду, реплицировать метаданные и поддерживать
прозрачность для грантовой комиссии.

## Способы

### 1️⃣ Встроенное mirroring (основное, recommended для гранта)
- Настройки выполнены в UI SourceCraft → *Settings → Repository → Mirroring*.
- URL удалённого репозитория: `git@github.com:leadarchitect-ai/portfolio-system-architect.git`
- Синхронизируемые ветки: `main`, `dev`.
- Снимок экрана (добавьте скриншот 1) – показ UI-параметров.
- Пуш происходит сразу после каждого коммита (latency < 5 сек).

### 2️⃣ GitHub Actions «Verification & Mirror»
- Файл `.github/workflows/mirror-sourcecraft.yml`.
- Запускается каждые 6 ч или вручную (`workflow_dispatch`).
- Выполняет lint (ruff), security-scan (trivy), затем `git push --mirror`.
- Журнал запусков доступен в GitHub Actions → *Runs* (скриншот 2).

## Почему оба подхода?
- **Primary** — быстрая синхронизация без дополнительного кода (важно для гранта).
- **Secondary** — контроль качества и доказательство CI/CD‑pipeline (демонстрирует зрелость процесса).

## Доступ и безопасность
- SSH‑ключ для GitHub хранится в SourceCraft в разделе *Deploy Keys* (только read‑only на GitHub).
- `GH_TOKEN` в GitHub имеет scope `repo` и хранится как secret.

## План обновления
- При изменении веток в SourceCraft обновляем список в UI и в workflow‑файле.
- При необходимости добавить новые проверки (например, проверка лицензий) – добавляем шаг в workflow.

*Последнее обновление:* 2026-03-14

