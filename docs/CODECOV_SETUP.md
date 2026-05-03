# Codecov Integration Guide

## 📊 Что даёт Codecov

- **Динамический бейдж** покрытия тестами в README
- **Детальные отчёты** по каждому коммиту и PR
- **История покрытия** и тренды
- **Интеграция с GitHub Checks** (annotations в коде)

## 🚀 Быстрая активация (3 шага)

### Шаг 1: Регистрация репозитория

1. Перейдите: https://codecov.io/login
2. Авторизуйтесь через GitHub
3. Нажмите **"Add New Repository"**
4. Найдите `Control39/portfolio-system-architect`
5. Нажмите **"Activate Repository"**

### Шаг 2: Получение TOKEN

После активации:
1. Перейдите в: `https://codecov.io/gh/Control39/portfolio-system-architect/settings`
2. Скопируйте **Repository Upload Token** (длинная строка символов)

### Шаг 3: Добавление в GitHub Secrets

1. Откройте: `https://github.com/Control39/portfolio-system-architect/settings/secrets/actions`
2. Нажмите **"New repository secret"**
3. Заполните:
   - **Name:** `CODECOV_TOKEN`
   - **Value:** (вставьте токен из шага 2)
4. Нажмите **"Add secret"**

## ✅ Проверка работы

После добавления токена:
1. Сделайте push любого изменения
2. Проверьте: `https://github.com/Control39/portfolio-system-architect/actions`
3. В логах CI должно быть: `✓ Coverage report uploaded successfully`
4. Перейдите: `https://app.codecov.io/github/Control39/portfolio-system-architect`
5. Должен отобразиться отчёт с покрытием

## 📈 Что делать после активации

1. **Добавьте бейдж в README** (уже добавлен)
   ```markdown
   [![Coverage](https://img.shields.io/codecov/c/github/Control39/portfolio-system-architect)](https://app.codecov.io/...)
   ```

2. **Настройте уведомления** (опционально)
   - В `codecov.yml` можно настроить Slack/Discord уведомления
   - Пример:
     ```yaml
     codecov:
       notify:
         after_n_builds: 1
         require_ci_to_pass: yes
     ```

3. **Мониторьте тренды**
   - Еженедельно проверяйте: `https://app.codecov.io/gh/Control39/portfolio-system-architect`
   - Следите за падением покрытия (алерт при <95%)

## 🔧 Конфигурация

Текущий конфиг: `.codecov.yml`

**Основные настройки:**
- **Цель покрытия:** 80% (порог успешности)
- **Допустимое падение:** 5%
- **Игнорируемые пути:** тесты, кэши, виртуальные окружения, документация

**Изменение цели:**
```yaml
coverage:
  range: "90...100"  # Повысить порог до 90%
  status:
    project:
      default:
        target: 95%   # Целевое покрытие
```

## 🐛 Troubleshooting

### Бейдж показывает "unknown"
- Проверьте, что `CODECOV_TOKEN` добавлен в Secrets
- Запустите CI вручную: Actions → Test & Coverage → Run workflow

### Отчёт не появляется на Codecov
- Подождите 5-10 минут после CI
- Проверьте: `https://codecov.io/gh/Control39/portfolio-system-architect/commits`
- Должен быть свежий commit с статусом "processed"

### Ошибка "Token not found"
- Перегенерируйте токен в настройках Codecov
- Удалите старый секрет и добавьте новый

## 📚 Дополнительные ресурсы

- [Официальная документация Codecov](https://docs.codecov.com)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
- [Конфигурация .codecov.yml](https://docs.codecov.com/docs/codecovyml-reference)

---

*Последнее обновление: Май 2026*
