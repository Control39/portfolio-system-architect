# SourceCraft Mirror Instructions

## Репозитории:
- **GitHub** (основной): https://github.com/Control39/portfolio-system-architect - разработка, CI/CD, PRs, публичный доступ
- **SourceCraft** (зеркало): https://sourcecraft.dev/leadarchitect-ai/portfolio-system-architect - грант, резервная копия

## Правила:
1. **Все PR и issues — на GitHub**
2. Синхронизация: GitHub → SourceCraft (автоматически через workflow)
3. Ручное обновление зеркала: `git push sourcecraft main --force`

## Команды:
```bash
# Добавить remote для зеркала если нет
git remote add sourcecraft https://sourcecraft.dev/leadarchitect-ai/portfolio-system-architect.git

# Обновить зеркало SourceCraft
git push sourcecraft main --force
```

## CI:
- GitHub Actions — основной CI/CD
- SourceCraft CI — резервный

## Branch Management:
- Все ветки управляются на GitHub
- SourceCraft зеркалит только `main` и `gh-pages`
- Автоматическая очистка старых веток на GitHub: каждое воскресенье 03:00 UTC
- Подробности: [Git Branch Management](GIT-BRANCH-MANAGEMENT.md)
