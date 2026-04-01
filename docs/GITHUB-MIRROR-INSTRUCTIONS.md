# GitHub Mirror Instructions

## Репозитории:
- **SourceCraft** (основной): https://sourcecraft.dev/leadarchitect-ai/portfolio-system-architect - грант, разработка, CI/CD, PRs
- **GitHub** (зеркало): https://github.com/Control39/cognitive-systems-architecture - публичный доступ для работодателей

## Правила:
1. **НЕ создавать PR на GitHub** - только на SourceCraft
2. Синхронизация: SourceCraft → GitHub (автоматически через workflow)
3. Ручное обновление: `git push github main --force`

## Команды:
```bash
# Добавить remote если нет
git remote add github https://github.com/Control39/cognitive-systems-architecture.git

# Обновить зеркало
git push github main --force
```

## CI:
- SourceCraft CI - основной
- GitHub Actions отключить в Settings > Actions > General (Disable)

## Branch Management:
- Все ветки создаются и удаляются на SourceCraft
- GitHub содержит только `main` и `gh-pages`
- Автоматическая очистка старых веток: каждое воскресенье 03:00 UTC
- Подробности: [Git Branch Management](GIT-BRANCH-MANAGEMENT.md)

## Cleanup Commands:
```bash
# Проверить какие ветки будут удалены (dry run)
DRY_RUN=true ./scripts/cleanup-old-branches.sh

# Принудительная очистка
./scripts/cleanup-old-branches.sh
```

