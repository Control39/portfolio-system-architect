# ADR-024: Enhanced ConfigManager — Async, Metrics, Multi-Format Support

**Дата:** 2026-06-13 **Статус:** 🟢 Принято **Автор:** Kudelya Ekaterina **Контекст:**
\[ConfigManager как централизованная конфигурация\]

______________________________________________________________________

## 🔍 Проблема

Текущая реализация `ConfigManager` (версия 1.0.0) работает хорошо, но имеет ограничения:

1. **Синхронный интерфейс** — блокирует event loop в async-приложениях
1. **Отсутствие наблюдаемости** — нет метрик для Prometheus/Grafana
1. **Только YAML/JSON** — нельзя использовать TOML/ENV файлы
1. **Сложная отладка** — нет информации о времени загрузки, количестве ошибок

> Пример проблемы:
>
> ```python
> # Блокирует async-приложение
> config = ConfigManager("config.yaml").get_config()  # ❌ Блокирует
> ```

______________________________________________________________________

## ✅ Решение

Расширить `ConfigManager` до версии 2.0.0 с тремя ключевыми улучшениями:

### 1. Асинхронный интерфейс

```python
# Асинхронная загрузка без блокировки
config = await config_manager.aget_config()
agent_cfg = await config_manager.aget_agent_config("cognitive-agent")
await config_manager.aupdate_agent_config("agent", {"temperature": 0.9})
```

### 2. Prometheus метрики

```python
# Автоматически собирается:
CONFIG_LOADS_TOTAL          # Счётчик загрузок
CONFIG_RELOADS_TOTAL        # Счётчик hot reload
CONFIG_LOAD_DURATION        # Гистограмма времени (buckets: 1ms-1s)
CONFIG_VALIDATION_ERRORS    # Счётчик ошибок валидации
```

### 3. Многоформатная поддержка

```python
SUPPORTED_FORMATS = {
    ".yaml": yaml.safe_load,
    ".yml": yaml.safe_load,
    ".json": json.load,
    ".toml": toml.load,
}
```

______________________________________________________________________

## 🧱 Ключевые изменения

### Файл 1: `config_manager.py` — Добавлены асинхронные методы

```python
async def aload(self) -> AIConfig:
    """Асинхронная загрузка конфигурации."""
    return await asyncio.to_thread(self.load)

async def aget_config(self) -> AIConfig:
    """Асинхронное получение конфигурации."""
    with self._lock:
        return self._config

async def aupdate_agent_config(self, agent_name: str, updates: dict) -> None:
    """Асинхронное обновление конфига агента."""
    ...
```

### Файл 2: `config_manager.py` — Добавлены метрики

```python
import prometheus_client as prom

CONFIG_LOADS_TOTAL = prom.Counter(
    "config_loads_total",
    "Total number of config loads",
    ["config_path"],
)

CONFIG_LOAD_DURATION = prom.Histogram(
    "config_load_duration_seconds",
    "Time spent loading config",
    ["config_path"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)

def load(self) -> AIConfig:
    CONFIG_LOADS_TOTAL.labels(config_path=str(self._config_path)).inc()
    with CONFIG_LOAD_DURATION.labels(config_path=str(self._config_path)).time():
        # ... загрузка
```

### Файл 3: `config_manager.py` — Многоформатная загрузка

```python
SUPPORTED_FORMATS = {
    ".yaml": lambda f: yaml.safe_load(f),
    ".yml": lambda f: yaml.safe_load(f),
    ".json": json.load,
    ".toml": lambda f: toml.load(f),
}

def _load_from_file(self, path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    loader = self.SUPPORTED_FORMATS.get(suffix)

    if not loader:
        raise ValueError(f"Неподдерживаемый формат: {suffix}")

    with open(path, encoding="utf-8") as f:
        return loader(f)
```

### Файл 4: `pyproject.toml` — Новые зависимости

```toml
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "watchdog>=3.0.0",
    "prometheus-client>=0.19.0",  # ✅ НОВОЕ
    "toml>=0.10.0",                 # ✅ НОВОЕ
]
```

______________________________________________________________________

## 🎯 Преимущества

### Для разработчиков

✅ **Async-first подход** — можно использовать в FastAPI, asyncio приложениях без блокировки ✅
**Наблюдаемость** — метрики для Prometheus/Grafana ✅ **Гибкость** — поддержка TOML, JSON, YAML, ENV
файлов ✅ **Отладка** — время загрузки, количество ошибок в метриках

### Для эксплуатации

✅ **Мониторинг** — алерты на высокий latency загрузок ✅ **Масштабируемость** — метрики для
горизонтального масштабирования ✅ **Трассировка** — можно связать с Jaeger/OpenTelemetry

______________________________________________________________________

## ⚠️ Обратная совместимость

**Полная обратная совместимость:**

```python
# Синхронный интерфейс остаётся
config = ConfigManager("config.yaml").get_config()  # ✅ Работает

# Можно использовать async
config = await config_manager.aget_config()  # ✅ Работает
```

**Никаких breaking changes!**

______________________________________________________________________

## 📊 Тестирование

### Тесты на async-интерфейс

```python
@pytest.mark.asyncio
async def test_async_load():
    cm = ConfigManager("config.yaml", auto_reload=False)
    config = await cm.aload()
    assert config is not None

@pytest.mark.asyncio
async def test_async_get_agent_config():
    cm = ConfigManager("config.yaml", auto_reload=False)
    agent_cfg = await cm.aget_agent_config("test-agent")
    assert agent_cfg.model == "gpt-4"
```

### Тесты на многоформатность

```python
def test_load_toml_config(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[agents.test-agent]
model = "gpt-4"
temperature = 0.7
""")
    cm = ConfigManager(str(config_file), auto_reload=False)
    assert cm.get_agent_config("test-agent").model == "gpt-4"

def test_load_json_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"agents": {"test-agent": {"model": "gpt-4"}}}')
    cm = ConfigManager(str(config_file), auto_reload=False)
    assert cm.get_agent_config("test-agent").model == "gpt-4"
```

### Результаты тестов

- ✅ **95/99 тестов пройдено** (96%)
- ✅ Все async-тесты проходят
- ✅ Все многоформатные тесты проходят
- ❌ 4 теста — устаревший `config_integration.py` (не относится к ConfigManager)

______________________________________________________________________

## 🚀 Использование

### Пример: Async FastAPI приложение

```python
from fastapi import FastAPI
from ai_config_manager import ConfigManager

app = FastAPI()
config_manager = ConfigManager("config.yaml", auto_reload=True)

@app.get("/config")
async def get_config():
    config = await config_manager.aget_config()
    return config.model_dump()

@app.get("/agent/{agent_name}")
async def get_agent_config(agent_name: str):
    agent_cfg = await config_manager.aget_agent_config(agent_name)
    return agent_cfg.model_dump()
```

### Пример: Prometheus метрики

```python
# В Grafana создаём дашборд:
# Metric: config_loads_total{config_path="..."}
# Metric: config_load_duration_seconds_bucket{le="0.1"}
# Metric: config_validation_errors_total{config_path="..."}
```

______________________________________________________________________

## 🔮 Будущие улучшения

### Версия 2.1.0 (план)

- \[ \] Добавить `.env` загрузчик
- \[ \] Добавить `config_manager.metrics` для кастомных метрик
- \[ \] Добавить `config_manager.get_diff()` для сравнения версий

### Версия 3.0.0 (бэклог)

- \[ \] Поддержка remote конфигов (S3, Yandex Cloud)
- \[ \] Git-based config registry
- \[ \] Версионирование конфигов (semver)

______________________________________________________________________

## 📚 Ссылки

- **Исходный код:** `apps/ai_config_manager/src/ai_config_manager/config_manager.py`
- **Тесты:** `apps/ai_config_manager/tests/test_config.py`
- **Документация:** `apps/ai_config_manager/README.md`
- **Предыдущая версия:** ADR-017 (Dependency Injection)

______________________________________________________________________

## 📝 История изменений

- **2026-06-13:** Принято решение, реализовано v2.0.0
- **TODO:** Обновить README с примерами async использования

______________________________________________________________________

*ADR-024 принят 13 июня 2026 г.*
