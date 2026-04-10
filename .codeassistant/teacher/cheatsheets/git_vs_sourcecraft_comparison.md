# Git vs SourceCraft: Сравнение для когнитивного архитектора

## Основные различия

### Git (традиционный)
- **Локальный контроль версий** - работает на вашем компьютере
- **Децентрализованный** - каждый разработчик имеет полную копию
- **Командная строка** - основной интерфейс через терминал
- **GitHub/GitLab** - внешние платформы для хостинга
- **Pull Requests** - через веб-интерфейс платформы

### SourceCraft (современный)
- **Облачный контроль версий** - работает в браузере
- **Интегрированная среда** - код, задачи, CI/CD в одном месте
- **Визуальный интерфейс** - минимум командной строки
- **Встроенные AI-агенты** - CodeAssistant, GigaCode
- **Автоматические PR** - создаются агентами

## Когда использовать что

### Используйте Git, когда:
- Работаете с legacy проектами
- Нужен полный локальный контроль
- Требуется офлайн-работа
- Интеграция с существующими инструментами

### Используйте SourceCraft, когда:
- Начинаете новый проект
- Хотите максимальной автоматизации
- Работаете в команде с AI-агентами
- Нужна встроенная аналитика и мониторинг

## Миграция между системами

### Из Git в SourceCraft:
```bash
# Клонируем репозиторий
git clone <git-repo>
cd <repo>

# Создаем новый репозиторий в SourceCraft
# (через веб-интерфейс или API)

# Добавляем remote
git remote add sourcecraft <sourcecraft-repo-url>

# Пушим все ветки
git push --all sourcecraft
```

### Из SourceCraft в Git:
```bash
# Клонируем из SourceCraft
git clone <sourcecraft-repo-url>

# Добавляем GitHub/GitLab remote
git remote add github <github-repo-url>

# Пушим
git push --all github
```

## Рабочие процессы

### Git-рабочий процесс:
1. `git pull` - получить изменения
2. `git checkout -b feature/name` - создать ветку
3. Редактировать файлы
4. `git add .` - добавить изменения
5. `git commit -m "message"` - закоммитить
6. `git push origin feature/name` - отправить
7. Создать PR через веб-интерфейс

### SourceCraft-рабочий процесс:
1. Открыть репозиторий в браузере
2. Нажать "Create Branch" в интерфейсе
3. Редактировать файлы через встроенный редактор
4. Нажать "Commit changes"
5. Нажать "Create Pull Request"
6. AI-агенты автоматически проверяют код

## Полезные команды

### Git алиасы (добавить в .gitconfig):
```gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    lg = log --oneline --graph --all
    undo = reset HEAD~1
    amend = commit --amend --no-edit
```

### SourceCraft CLI (если доступен):
```bash
# Установка (если поддерживается)
npm install -g @sourcecraft/cli

# Основные команды
sc login
sc repo list
sc repo clone <slug>
sc pr create --title "Feature" --description "Description"
```

## Интеграция с VS Code

### Git в VS Code:
- Встроенная поддержка через расширение Git
- Source Control панель
- Визуальное diff

### SourceCraft в VS Code:
- Расширение SourceCraft (если доступно)
- Или работа через веб-интерфейс
- Альтернатива: использовать Git CLI с SourceCraft как remote

## Советы для когнитивного архитектора

1. **Начинайте с SourceCraft** для новых проектов - меньше настройки
2. **Используйте Git для экспериментов** локально
3. **Автоматизируйте миграцию** скриптами
4. **Документируйте процесс** для команды
5. **Тестируйте оба подхода** на небольших проектах

## Проблемы и решения

### Проблема: Потеря связи с SourceCraft
**Решение:** Иметь локальную Git-копию как backup

### Проблема: Конфликты при миграции
**Решение:** Использовать `--allow-unrelated-histories`

### Проблема: Разные настройки CI/CD
**Решение:** Хранить конфигурации в репозитории (не в платформе)

## Дополнительные ресурсы

- [SourceCraft Documentation](https://docs.sourcecraft.io)
- [Git Pro Book](https://git-scm.com/book/en/v2)
- [GitHub CLI](https://cli.github.com)
- [Visual Git Guide](https://marklodato.github.io/visual-git-guide)