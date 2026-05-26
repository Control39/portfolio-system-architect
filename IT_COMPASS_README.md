# 🧭 IT Compass - Автоматическое сканирование компетенций

## 🎯 Обзор

**IT Compass** — система автоматического сканирования проекта для:
1. ✅ Обнаружения маркеров компетенций в коде
2. ✅ Расчёта прогресса развития
3. ✅ Генерации портфолио
4. ✅ Карьерных рекомендаций

**Интеграция с Cognitive Agent:**
- Сканирование запускается **автоматически** при открытии проекта
- Маркеры обновляются каждые 5 минут
- Портфолио генерируется через AI (GigaChat/Ollama)

---

## 🏗️ Архитектура

```
Открытие проекта в VS Code
        ↓
[Cognitive Agent Start]
        ↓
[IT Compass Scanner]
    ├─ Сканирует маркеры
    ├─ Обновляет прогресс
    └─ Генерирует портфолио
        ↓
[AI Provider Manager]
    ├─ GigaChat (основной)
    └─ Ollama (резервный)
        ↓
[Результаты]
    ├─ it_compass/markers.json
    ├─ it_compass/progress.json
    └─ it_compass/portfolio.json
```

---

## 📦 Маркеры компетенций

### Архитектура
- ✅ Микросервисная архитектура
- ✅ DDD (Domain-Driven Design)
- ✅ CQRS паттерн

### Разработка
- ✅ Python разработка
- ✅ Асинхронное программирование
- ✅ REST API

### Тестирование
- ✅ Модульное тестирование
- ✅ E2E тестирование
- ✅ TDD

### DevOps
- ✅ Docker контейнеризация
- ✅ CI/CD пайплайны
- ✅ Мониторинг

### Безопасность
- ✅ Аутентификация и авторизация
- ✅ Криптография

### Документация
- ✅ API документация
- ✅ ADR (Architecture Decision Records)

---

## 🚀 Использование

### Автоматическое сканирование

При открытии проекта в VS Code:
1. ✅ Cognitive Agent запускается автоматически
2. ✅ IT Compass Scanner сканирует проект
3. ✅ Маркеры обновляются в `it_compass/`
4. ✅ Портфолио генерируется через AI

### Ручное сканирование

```bash
# Через терминал
python -m apps.it_compass.src.it_compass_scanner --scan

# Статус
python -m apps.it_compass.src.it_compass_scanner --status
```

### Через код

```python
from apps.it_compass.src.it_compass_scanner import scan_it_compass

# Сканировать проект
results = scan_it_compass()

print(f"Маркеры: {results['markers_detected']}/{results['markers_total']}")
print(f"Прогресс: {results['progress']['overall']:.1f}%")
```

---

## 📊 Результаты

### it_compass/markers.json

```json
{
  "arch_microservices": {
    "id": "arch_microservices",
    "name": "Микросервисная архитектура",
    "category": "architecture",
    "detected": true,
    "evidence": ["auth_service", "infra_orchestrator", "cognitive_agent"],
    "confidence": 0.8
  }
}
```

### it_compass/progress.json

```json
{
  "overall": 67.5,
  "categories": {
    "architecture": 80.0,
    "development": 75.0,
    "testing": 60.0,
    "devops": 70.0,
    "security": 50.0,
    "documentation": 40.0
  },
  "markers_detected": 12,
  "markers_total": 16
}
```

### it_compass/portfolio.json

```json
{
  "summary": "Проект демонстрирует продвинутые навыки в микросервисной архитектуре",
  "strengths": [
    "Микросервисная архитектура с 5+ сервисами",
    "Полное покрытие тестами (unit + E2E)",
    "Docker контейнеризация"
  ],
  "areas_for_improvement": [
    "Добавить ADR документацию",
    "Усилить криптографию",
    "Добавить мониторинг"
  ],
  "career_recommendations": [
    "Senior Python Developer",
    "Backend Architect",
    "Tech Lead"
  ],
  "next_markers": [
    "doc_adr - Добавить ADR",
    "ops_monitoring - Настроить мониторинг",
    "sec_crypto - Усилить криптографию"
  ]
}
```

---

## 🎯 Как это работает

### 1. Сканирование маркеров

**Поиск паттернов в коде:**
```python
# Микросервисы
if (project_path / "apps").exists():
    apps = list((project_path / "apps").iterdir())
    if len(apps) >= 3:
        marker.detected = True

# Тесты
test_files = list(project_path.rglob("**/test_*.py"))
if len(test_files) >= 5:
    marker.detected = True

# Docker
if (project_path / "docker-compose.yml").exists():
    marker.detected = True
```

### 2. Расчёт прогресса

```python
# Формула:
progress = (detected_weight / total_weight) * 100

# Где:
# - detected_weight = сумма весов обнаруженных маркеров
# - total_weight = сумма всех весов маркеров
# - confidence = уверенность в обнаружении (0-1)
```

### 3. Генерация портфолио

```python
# AI получает контекст:
prompt = f"""
Обнаруженные маркеры: {detected_markers}
Общий прогресс: {overall}%

Сгенерируй портфолио:
- summary
- strengths
- areas_for_improvement
- career_recommendations
"""

# AI возвращает JSON с рекомендациями
```

---

## 🔍 Примеры использования

### Проверка прогресса

```python
from apps.it_compass.src.it_compass_scanner import get_scanner

scanner = get_scanner()
status = scanner.get_status()

print(f"Общий прогресс: {status['progress']:.1f}%")
print(f"Маркеры: {status['markers_detected']}/{status['markers_total']}")
print(f"\nПо категориям:")
for category, progress in status['categories'].items():
    print(f"  {category}: {progress:.1f}%")
```

### Получение рекомендаций

```python
# Карьерные советы
recommendations = scanner.get_recommendations()
for rec in recommendations:
    print(f"• {rec}")

# Следующие маркеры для достижения
next_markers = scanner.get_next_markers()
for marker in next_markers:
    print(f"• {marker}")
```

---

## 🎯 Интеграция с Cognitive Agent

### Автозапуск

При открытии проекта:
1. ✅ VS Code запускает Cognitive Agent
2. ✅ Agent запускает IT Compass Scanner
3. ✅ Сканирование занимает ~2-5 секунд
4. ✅ Результаты сохраняются в `it_compass/`

### Настройка

```json
// .vscode/settings.json
{
  "cognitiveAgent.autoStart": true,
  "itCompass.scanInterval": 300  // 5 минут
}
```

---

## 🐛 Troubleshooting

### Проблема: Нет маркеров

**Решение:**
```bash
# Проверь структуру проекта
ls apps/  # Должно быть >= 3 сервисов
ls tests/e2e/  # Должны быть E2E тесты
ls docs/  # Должна быть документация

# Пересканируй
python -m apps.it_compass.src.it_compass_scanner --scan
```

### Проблема: AI недоступен

**Решение:**
```bash
# Проверь GigaChat
.\scripts\auto-update-gigacode-token.ps1

# Проверь Ollama
ollama list

# Используй только базовое сканирование (без AI)
# Портфолио не будет сгенерировано, но маркеры будут обнаружены
```

### Проблема: Низкий прогресс

**Решение:**
1. Добавь больше микросервисов (минимум 3)
2. Добавь E2E тесты
3. Добавь Docker конфигурацию
4. Добавь документацию

---

## 📈 Метрики

| Маркер | Вес | Для обнаружения |
|--------|-----|-----------------|
| Микросервисы | 10 | >= 3 сервисов в `apps/` |
| Python | 5 | >= 10 Python файлов |
| Тесты | 5 | >= 5 test файлов |
| E2E | 8 | `tests/e2e/` с тестами |
| Docker | 5 | `docker-compose.yml` |
| CI/CD | 8 | `.github/workflows/` |
| Auth | 8 | `auth_service/` |
| ADR | 6 | `docs/adr/` |

---

## 🎓 Карьерные уровни

### Junior (0-30%)
- Базовая структура проекта
- Некоторые тесты
- Основная документация

### Middle (30-60%)
- Микросервисная архитектура
- Полное тестирование
- Docker контейнеризация
- API документация

### Senior (60-80%)
- Продвинутая архитектура (DDD, CQRS)
- E2E тесты
- CI/CD пайплайны
- ADR документация

### Expert (80-100%)
- Все маркеры
- Мониторинг и логирование
- Продвинутая безопасность
- Полная документация

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| **`docs/IT_COMPASS_GUIDE.md`** | **Полное руководство** |
| `apps/it_compass/src/it_compass_scanner.py` | Исходный код |
| `it_compass/markers.json` | Обнаруженные маркеры |
| `it_compass/progress.json` | Прогресс развития |
| `it_compass/portfolio.json` | Сгенерированное портфолио |

---

## ✅ Следующие шаги

1. **Запусти сканирование:**
   ```bash
   python -m apps.it_compass.src.it_compass_scanner --scan
   ```

2. **Проверь результаты:**
   ```bash
   cat it_compass/progress.json
   cat it_compass/portfolio.json
   ```

3. **Улучшай проект:**
   - Реализуй недостающие маркеры
   - Повторно сканируй
   - Следи за прогрессом

---

**Готово! IT Compass автоматически сканирует твой проект и даст карьерные рекомендации!** 🧭✨
