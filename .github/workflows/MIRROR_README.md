# Mirror to SourceCraft — Руководство

## 📋 Обзор

Этот workflow автоматически синхронизирует репозиторий с SourceCraft при каждом пуше в ветку `main`.

**URL:** `ssh://ssh.sourcecraft.dev/leadarchitect-ai/portfolio-system-architect.git`

---

## 🔧 Как это работает

```
GitHub (main) → Mirror to SourceCraft workflow → SourceCraft
```

### Шаги workflow:

1. **Checkout code** — загрузка кода из GitHub
2. **Setup SSH Agent** — загрузка SSH-ключа из GitHub Secrets
3. **Add SourceCraft host key** — добавление `ssh.sourcecraft.dev` в known_hosts
4. **Add SourceCraft remote** — создание remote-адреса
5. **Push to SourceCraft** — отправку изменений в SourceCraft

---

## 🔐 Настройка SSH-ключа

### Шаг 1: Создать SSH-ключ (если нет)

```powershell
ssh-keygen -t ed25519 -C "github-actions@portfolio-system-architect"
```

Файлы:
- Приватный ключ: `~/.ssh/id_ed25519`
- Публичный ключ: `~/.ssh/id_ed25519.pub`

### Шаг 2: Добавить в GitHub Secrets

1. Зайдите в репозиторий на GitHub
2. **Settings → Secrets and variables → Actions**
3. Нажмите **"New repository secret"**
4. Название: `SOURCECRAFT_SSH_KEY`
5. Значение: содержимое **приватного** ключа (`id_ed25519`)

```powershell
# Получить содержимое приватного ключа:
Get-Content ~/.ssh/id_ed25519
```

### Шаг 3: Добавить публичный ключ в SourceCraft

1. Зайдите в панель SourceCraft
2. **Настройки → SSH Keys**
3. Добавьте публичный ключ (`id_ed25519.pub`)

```powershell
# Получить содержимое публичного ключа:
Get-Content ~/.ssh/id_ed25519.pub
```

### Шаг 4: Проверить подключение (локально)

```powershell
# Добавить ключ в агент:
ssh-add ~/.ssh/id_ed25519

# Проверить подключение:
ssh -T ssh.sourcecraft.dev
```

Ожидаемый результат:
```
Hi leadarchitect-ai! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## ❌ Типичные проблемы и решения

### Проблема 1: "Host key verification failed"

**Причина:** GitHub Actions не доверяет хосту `ssh.sourcecraft.dev`

**Решение:** Workflow автоматически добавляет host key через `ssh-keyscan`

```yaml
- name: Add SourceCraft host key
  run: |
    mkdir -p ~/.ssh
    ssh-keyscan -H ssh.sourcecraft.dev >> ~/.ssh/known_hosts
```

Если ошибка остаётся:
```bash
# Проверить, доступен ли хост из GitHub:
ssh-keyscan ssh.sourcecraft.dev
```

---

### Проблема 2: "Permission denied (publickey)"

**Причина:** SSH-ключ не найден или не добавлен в SourceCraft

**Решение:**

1. Проверить, что `SOURCECRAFT_SSH_KEY` добавлен в GitHub Secrets
2. Проверить, что публичный ключ добавлен в SourceCraft
3. Убедиться, что используется правильный приватный ключ

---

### Проблема 3: "Repository not found"

**Причина:** Репозиторий не существует на SourceCraft

**Решение:**

1. Создайте репозиторий вручную на SourceCraft:
   - URL: `https://sourcecraft.dev/leadarchitect-ai/portfolio-system-architect`
   - Имя: `portfolio-system-architect`
   - Доступ: **Private** (рекомендуется)

2. Проверьте права доступа:
   - Учётная запись должна иметь права **push** на репозиторий

---

### Проблема 4: "fatal: remote sourcecraft already exists"

**Причина:** Remote уже существует (используется `git remote add` вместо `set-url`)

**Решение:**

Workflow использует:
```bash
git remote add sourcecraft ... || git remote set-url sourcecraft ...
```

Это обрабатывает оба случая.

---

## 🚀 Запуск workflow

### Автоматический запуск

Workflow запускается автоматически при каждом пуше в `main`:

```powershell
git push origin main
# → Mirror workflow запускается автоматически
```

### Ручной запуск

1. Зайдите в **Actions → Mirror to SourceCraft**
2. Нажмите **"Run workflow"**
3. Выберите ветку (`main`)
4. Нажмите **"Run workflow"**

---

## 📊 Мониторинг

### Просмотр логов

1. **Actions → Mirror to SourceCraft**
2. Выберите запуск
3. Просмотрите логи каждого шага

### Статусы

| Статус | Значение |
|--------|----------|
| ✅ Success | Mirror успешно синхронизирован |
| ❌ Failed | Ошибка (см. логи) |
| ⏳ In progress | Запуск выполняется |

---

## 🔍 Отладка

### Включить детальный лог

Добавьте в workflow:
```yaml
- name: Debug SSH
  run: |
    echo "SSH_AUTH_SOCK: $SSH_AUTH_SOCK"
    ssh-add -l
    ssh -Tv ssh.sourcecraft.dev
```

### Проверить remote

```bash
git remote -v
# Ожидаемый вывод:
# sourcecraft	git@ssh.sourcecraft.dev:leadarchitect-ai/portfolio-system-architect.git (fetch)
# sourcecraft	git@ssh.sourcecraft.dev:leadarchitect-ai/portfolio-system-architect.git (push)
```

### Проверить known_hosts

```bash
cat ~/.ssh/known_hosts
# Должен содержать строку для ssh.sourcecraft.dev
```

---

## 📝 История изменений

| Дата | Версия | Изменения |
|------|--------|-----------|
| 2026-05-19 | v1.0 | Первоначальная версия |
| 2026-05-19 | v1.1 | Добавлен ssh-keyscan для known_hosts |
| 2026-05-19 | v1.2 | Исправлен формат SSH URL (SCP-style) |
| 2026-05-19 | v1.3 | Добавлен remote sourcecraft перед push |

---

## 📞 Поддержка

Если workflow не работает:

1. Проверьте логи в GitHub Actions
2. Убедитесь, что SSH-ключ добавлен в GitHub Secrets
3. Убедитесь, что публичный ключ добавлен в SourceCraft
4. Проверьте, что репозиторий существует на SourceCraft
5. Создайте issue в репозитории с подробным описанием проблемы

---

*Создано: 19 мая 2026 г.*
*Автор: Koda AI Assistant*
