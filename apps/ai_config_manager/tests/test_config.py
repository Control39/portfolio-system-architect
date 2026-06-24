"""Unit tests for ai_config_manager ConfigManager.

Цель этих тестов — реально покрыть код:
- apps/ai_config_manager/src/ai_config_manager/config_manager.py
- apps/ai_config_manager/src/ai_config_manager/validators.py

Тесты написаны так, чтобы:
- не запускать watchdog в фоне без необходимости
- не зависать на hot-reload
- ловить реальные баги, а не просто "проходить"
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml
from pydantic import ValidationError

# conftest.py добавляет корневой src/ и репозиторий в sys.path
# Импортируем из ai_config_manager напрямую (package __init__.py экспортирует классы)
from ai_config_manager import AIConfig, ConfigManager
from ai_config_manager.validators import ResourceType


def _write_yaml(tmp_path: Path, data: dict[str, Any]) -> str:
    """Вспомогательная функция: записать данные в YAML-файл."""
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return str(p)


@pytest.fixture
def valid_config_data() -> dict[str, Any]:
    """Фикстура: валидные данные конфигурации для тестов."""
    return {
        "agents": {
            "test-agent": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1024,
                "resources": ["test-resource"],
                "timeout": 10,
                "retry_count": 2,
            }
        },
        "resources": {
            "test-resource": {
                "name": "test-resource",
                "type": "tool",
                "enabled": True,
                "config": {"language": "python"},
                "metadata": {"version": "1.0.0"},
            }
        },
        "secrets": {
            "api_keys": {"openai": "sk-..."},
            "database_urls": {
                "primary": "postgres://user:pass@localhost/db"
            },  # pragma: allowlist secret
            "custom": {"jwt": "jwt_secret"},  # pragma: allowlist secret
        },
        "version": "1.0.0",
    }


# =============================================================================
# БАЗОВЫЕ ТЕСТЫ: загрузка и валидация
# =============================================================================


def test_load_valid_config(tmp_path: Path, valid_config_data: dict[str, Any]):
    """Загрузка валидного конфига → корректный объект AIConfig."""
    config_path = _write_yaml(tmp_path, valid_config_data)

    cm = ConfigManager(config_path, auto_reload=False)
    cfg = cm.get_config()

    assert isinstance(cfg, AIConfig)
    assert "test-agent" in cfg.agents
    assert cfg.agents["test-agent"].model == "gpt-4"
    assert cfg.agents["test-agent"].temperature == 0.7

    assert "test-resource" in cfg.resources
    assert cfg.resources["test-resource"].name == "test-resource"
    assert cfg.resources["test-resource"].type == ResourceType.TOOL


def test_get_agent_config_not_found(tmp_path: Path, valid_config_data: dict[str, Any]):
    """Запрос несуществующего агента → KeyError."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    with pytest.raises(KeyError, match="Агент не найден: nonexistent"):
        cm.get_agent_config("nonexistent")


def test_get_resource_config_not_found(tmp_path: Path, valid_config_data: dict[str, Any]):
    """Запрос несуществующего ресурса → KeyError."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    with pytest.raises(KeyError, match="Ресурс не найден: nonexistent"):
        cm.get_resource_config("nonexistent")


def test_nonexistent_file_raises(tmp_path: Path):
    """Отсутствующий файл конфигурации → FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        ConfigManager(str(tmp_path / "does_not_exist.yaml"), auto_reload=False)


def test_get_config_requires_load(tmp_path: Path):
    """Вызов get_config() без предварительной загрузки → RuntimeError."""
    config_path = _write_yaml(
        tmp_path,
        {
            "agents": {},
            "resources": {},
        },
    )
    cm = ConfigManager(config_path, auto_reload=False)

    # Костыль: сбросить внутреннее состояние для теста edge-case
    cm._config = None  # type: ignore[assignment]

    with pytest.raises(RuntimeError, match="Конфигурация не загружена"):
        cm.get_config()


# =============================================================================
# ТЕСТЫ: обновление конфигурации (в памяти)
# =============================================================================


def test_update_agent_config_updates_in_memory(tmp_path: Path, valid_config_data: dict[str, Any]):
    """update_agent_config() меняет значение в памяти, но не на диске."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    cm.update_agent_config("test-agent", {"temperature": 0.95, "max_tokens": 2048})

    agent_cfg = cm.get_agent_config("test-agent")
    assert agent_cfg.temperature == 0.95
    assert agent_cfg.max_tokens == 2048


def test_update_agent_config_agent_missing(tmp_path: Path, valid_config_data: dict[str, Any]):
    """Обновление несуществующего агента → KeyError."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    with pytest.raises(KeyError, match="Агент не найден: missing"):
        cm.update_agent_config("missing", {"temperature": 0.5})


def test_update_agent_config_validation_error(tmp_path: Path, valid_config_data: dict[str, Any]):
    """Обновление с невалидными данными → ValidationError, старое значение сохраняется."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    # temperature должен быть 0.0-2.0, передаём 3.0 → ошибка валидации
    with pytest.raises(ValidationError):
        cm.update_agent_config("test-agent", {"temperature": 3.0})

    # Убедиться, что старое значение сохранилось (атомарность обновления)
    assert cm.get_agent_config("test-agent").temperature == 0.7


@pytest.mark.parametrize(
    "bad_value,field",
    [
        (3.0, "temperature"),  # > 2.0
        (-0.1, "temperature"),  # < 0.0
        (0, "max_tokens"),  # ноль (если min_tokens=1)
    ],
)
def test_agent_config_validation_parametrized(
    tmp_path: Path, valid_config_data: dict[str, Any], bad_value: Any, field: str
):
    """Параметризованный тест: невалидные значения полей → ValidationError."""
    valid_config_data["agents"]["test-agent"][field] = bad_value
    config_path = _write_yaml(tmp_path, valid_config_data)

    with pytest.raises(ValidationError):
        ConfigManager(config_path, auto_reload=False)


def test_init_raises_on_bad_config(tmp_path: Path):
    """ConfigManager.__init__ raises ValidationError for invalid config."""
    bad = {
        "agents": {
            "test-agent": {
                "model": "gpt-4",
                "temperature": 3.0,  # > 2.0 → ошибка
            }
        },
        "resources": {},
    }
    config_path = _write_yaml(tmp_path, bad)

    with pytest.raises(ValidationError):
        ConfigManager(config_path, auto_reload=False)


def test_validate_true_on_good_config(tmp_path: Path, valid_config_data: dict[str, Any]):
    """validate() возвращает True при валидном конфиге."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)
    assert cm.validate() is True


# =============================================================================
# ТЕСТЫ: reload и hot-reload
# =============================================================================


def test_hot_reload_calls_load(tmp_path: Path, valid_config_data: dict[str, Any]):
    """reload() перечитывает файл и обновляет конфигурацию в памяти."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    # Меняем файл на диске
    parsed = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    parsed["agents"]["test-agent"]["temperature"] = 0.1
    Path(config_path).write_text(yaml.safe_dump(parsed, allow_unicode=True), encoding="utf-8")

    # Перезагружаем и проверяем
    cm.reload()
    assert cm.get_agent_config("test-agent").temperature == 0.1


def test_reload_with_invalid_file_raises(tmp_path: Path, valid_config_data: dict[str, Any]):
    """reload() с битым файлом → ValidationError, старая конфигурация не теряется."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    # Записываем невалидный конфиг (температура > 2.0)
    Path(config_path).write_text(
        "agents:\n  test-agent:\n    temperature: 999\n    model: gpt-4", encoding="utf-8"
    )

    with pytest.raises(ValidationError):
        cm.reload()

    # Старая конфигурация должна остаться в памяти (политика: не терять рабочее состояние)
    assert cm._config is not None
    assert cm.get_agent_config("test-agent").temperature == 0.7


def test_get_config_returns_cached_object(tmp_path: Path, valid_config_data: dict[str, Any]):
    """get_config() возвращает кэшированный объект (одинаковый экземпляр)."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    cfg1 = cm.get_config()
    cfg2 = cm.get_config()

    assert cfg1 is cfg2  # same object = cached, экономия памяти


# =============================================================================
# ТЕСТЫ: валидация уникальности ресурсов
# =============================================================================


def test_resource_name_uniqueness_validation(tmp_path: Path):
    """validate_resource_names проверяет уникальность r.name среди ресурсов."""
    data = {
        "agents": {
            "agent1": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 1024},
        },
        "resources": {
            "r1": {"name": "dup", "type": "tool"},
            "r2": {"name": "dup", "type": "model"},  # дубликат имени!
        },
    }
    config_path = _write_yaml(tmp_path, data)

    with pytest.raises(ValidationError):
        ConfigManager(config_path, auto_reload=False)


# =============================================================================
# ТЕСТЫ: watchdog / hot-reload lifecycle (с моками)
# =============================================================================


@patch("ai_config_manager.config_manager.Observer")
def test_start_stop_watching_lifecycle(
    mock_observer, tmp_path: Path, valid_config_data: dict[str, Any]
):
    """start_watching() / stop_watching() корректно управляют Observer (mock)."""
    observer_instance = MagicMock()
    mock_observer.return_value = observer_instance

    config_path = _write_yaml(tmp_path, valid_config_data)

    cm = ConfigManager(config_path, auto_reload=True)
    assert cm._observer is not None

    observer_instance.schedule.assert_called_once()
    observer_instance.start.assert_called_once()

    cm.stop_watching()

    observer_instance.stop.assert_called_once()
    observer_instance.join.assert_called_once()
    assert cm._observer is None


@patch("ai_config_manager.config_manager.Observer")
def test_context_manager_stops_watching(
    mock_observer, tmp_path: Path, valid_config_data: dict[str, Any]
):
    """Контекстный менеджер автоматически останавливает наблюдение при выходе."""
    observer_instance = MagicMock()
    mock_observer.return_value = observer_instance

    config_path = _write_yaml(tmp_path, valid_config_data)

    with ConfigManager(config_path, auto_reload=True) as cm:
        assert cm.get_config() is not None

    observer_instance.stop.assert_called_once()
    assert cm._observer is None


@patch("ai_config_manager.config_manager.Observer")
def test_no_observer_when_auto_reload_false(
    mock_observer, tmp_path: Path, valid_config_data: dict[str, Any]
):
    """При auto_reload=False Observer не создаётся (экономия ресурсов)."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    mock_observer.assert_not_called()
    assert cm._observer is None


# =============================================================================
# ТЕСТЫ: потокобезопасность
# =============================================================================


def test_thread_safety_update_agent_config(tmp_path: Path, valid_config_data: dict[str, Any]):
    """update_agent_config() потокобезопасен: нет гонок данных при параллельных обновлениях."""
    config_path = _write_yaml(tmp_path, valid_config_data)
    cm = ConfigManager(config_path, auto_reload=False)

    errors: list[Exception] = []

    def worker(i: int) -> None:
        try:
            cm.update_agent_config("test-agent", {"temperature": 0.1 + i * 0.01})
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    # Финальное значение должно быть в допустимом диапазоне [0.0, 2.0]
    assert 0.0 <= cm.get_agent_config("test-agent").temperature <= 2.0


# =============================================================================
# ТЕСТЫ: безопасность (маскирование секретов в логах)
# =============================================================================


def test_secrets_are_masked_in_logs(
    tmp_path: Path, valid_config_data: dict[str, Any], caplog: pytest.LogCaptureFixture
):
    """Секреты не попадают в логи в открытом виде (маскирование)."""
    config_path = _write_yaml(tmp_path, valid_config_data)

    with caplog.at_level(logging.INFO):
        cm = ConfigManager(config_path, auto_reload=False)
        cm.get_config()

    # Секреты не должны попадать в логи в открытом виде
    log_text = caplog.text
    assert "sk-..." not in log_text
    assert "postgres://user:pass" not in log_text
    assert "jwt_secret" not in log_text
