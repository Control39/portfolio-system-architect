# 🔑 Настройка API для поиска вакансий

## 🎯 Проблема

API hh.ru требует регистрации приложения для полноценной работы.

---

## ✅ Решение: 3 варианта

### Вариант 1: Демо-режим (работает сейчас) ✅

**Что делает:**
- Показывает шаблон вакансий
- Работает без API ключей
- Идеально для демонстрации методологии

**Как запустить:**
```bash
python demo_integration.py
```

**Результат:**
```
💡 Рекомендованные вакансии:

   1. Cognitive Systems Architect @ AI Innovation Lab
      Уровень: Senior | Совпадение: 95%
      Почему подходит: Методология IT Compass + архитектура когнитивных систем
```

---

### Вариант 2: hh.ru API (требуется регистрация)

#### Шаг 1: Зарегистрируйте приложение

1. Перейдите на https://dev.hh.ru/
2. Создайте учётную запись
3. Зарегистрируйте новое приложение
4. Скопируйте `client_id`

#### Шаг 2: Настройте окружение

```bash
# Скопируйте .env.example в .env
cp apps/job_automation_agent/.env.example apps/job_automation_agent/.env

# Отредактируйте .env
nano apps/job_automation_agent/.env
```

Добавьте:
```env
HH_RU_CLIENT_ID=your_client_id_here
HH_RU_SEARCH_ENABLED=true
```

#### Шаг 3: Обновите код

В `providers/hh_ru.py` добавьте:

```python
class HHruProvider:
    def __init__(self):
        self.client_id = os.getenv("HH_RU_CLIENT_ID")
        # ...
    
    async def search(self, query: str, ...):
        headers = {
            "User-Agent": "YourApp/1.0",
            "Authorization": f"Bearer {self.client_id}"  # Если нужно
        }
```

---

### Вариант 3: Альтернативные источники

#### Habr Career (без регистрации) ✅

```bash
python -m apps.job_automation_agent.src.providers.habr_career
```

**Пример результата:**
```
🔍 Найдено вакансий: 15
1. Python Architect @ Company X
   Зарплата: 250 000 - 400 000 руб.
```

#### LinkedIn (требуется API ключ)

```python
from .providers.linkedin import LinkedInProvider

provider = LinkedInProvider(api_key="your_key")
vacancies = await provider.search("Python architect")
```

#### Telegram-каналы

```python
from .providers.telegram import TelegramProvider

provider = TelegramProvider()
vacancies = await provider.search_channels([
    "python_jobs_ru",
    "it_vacancies_moscow"
])
```

---

## 🚀 Рекомендация

**Для старта используйте:**

1. **Демо-режим** (Вариант 1) — для демонстрации методологии
2. **Habr Career** (Вариант 3) — для реального поиска IT-вакансий
3. **hh.ru API** (Вариант 2) — после регистрации приложения

---

## 📊 Сравнение источников

| Источник | Регистрация | IT-вакансии | Россия | Интернациональный |
|----------|-------------|-------------|--------|-------------------|
| **Демо** | ❌ Нет | ✅ Шаблон | ✅ | ✅ |
| **Habr Career** | ❌ Нет | ✅ Да | ✅ | ⚠️ RU |
| **hh.ru** | ✅ Да | ✅ Да | ✅ Да | ⚠️ RU/CIS |
| **LinkedIn** | ✅ Да | ✅ Да | ⚠️ Мало | ✅ Глобально |

---

## 🎬 Для презентации/гранта

```bash
# 1. Запустите демо
python demo_integration.py

# 2. Покажите интеграцию
echo "IT Compass → CareerTracker → Job Agent → Вакансии"

# 3. Объясните архитектуру
echo "Авторская методология с объективными маркерами"

# 4. Для реального поиска используйте Habr Career
python -m apps.job_automation_agent.src.providers.habr_career
```

---

## 📝 Следующие шаги

1. **Регистрация на dev.hh.ru** (по желанию)
2. **Добавление LinkedIn API** (для международных вакансий)
3. **Интеграция с Telegram** (для оперативных вакансий)
4. **Экспорт в PDF** (для отправки HR)

---

**Дата:** 27 мая 2026  
**Статус:** ✅ Демо работает, API настраивается по желанию
