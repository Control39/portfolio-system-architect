"""
Тесты для ConfigManager — полная версия.

Покрывает:
- Загрузку, валидацию, обновление, перезагрузку
- Работу с Observer (hot-reload)
- Безопасность (логи, секреты)
- Потокобезопасность
- Контекстный менеджер
"""

import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from unittest.mock import MagicMock, patch

import sys

# Настройка пути к src
REPO_ROOT = Path(__file__).resolve().parents[3]
APP_SRC = REPO_ROOT / "apps" / "ai_config_manager" / "src"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

from ai_config_manager.config_manager import ConfigManager


class TestConfigManager:
    """Тесты для ConfigManager."""

    @pytest.fixture
    def temp_config_data(self) -> Dict[str, Any]:
        """Фикстура: валидные данные конфига."""
        return {
            "agents": {
                "test-agent": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "resources": ["tool1"],
                }
            },
            "resources": {
                "tool1": {"name": "tool1", "type": "tool", "enabled": True}
            },
            "secrets": {
                "api_keys": {"openai": "sk-test-1234567890abcdef"}
            },
            "version": "1.0.0",
        }

    @pytest.fixture
    def temp_config_file(self, tmp_path, temp_config_data):
        """Создание временного YAML-файла."""
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(temp_config_data, f, allow_unicode=True)
        return str(config_file)

    # ========================================================================
    # БАЗОВЫЕ ОПЕРАЦИИ: загрузка, получение
    # ========================================================================

    def test_load_valid_config(self, temp_config_file):
        """Загрузка валидной конфигурации."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        cfg = cm.get_config()

        assert cfg is not None
        assert "test-agent" in cfg.agents
        assert cfg.agents["test-agent"].model == "gpt-4"
        assert len(cfg.resources) == 1
        assert cfg.version == "1.0.0"

    def test_load_nonexistent_file(self):
        """Загрузка несуществующего файла → FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigManager("/nonexistent/config.yaml", auto_reload=False)

    def test_get_agent_config(self, temp_config_file):
        """Получение конфигурации агента."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        agent_cfg = cm.get_agent_config("test-agent")
        assert agent_cfg.model == "gpt-4"
        assert agent_cfg.temperature == 0.7

    def test_get_agent_config_not_found(self, temp_config_file):
        """Попытка получить несуществующий агент → KeyError."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        with pytest.raises(KeyError, match="Агент не найден: nonexistent"):
            cm.get_agent_config("nonexistent")

    def test_get_resource_config(self, temp_config_file):
        """Получение конфигурации ресурса."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        res_cfg = cm.get_resource_config("tool1")
        assert res_cfg.name == "tool1"
        assert res_cfg.type == "tool"

    def test_get_resource_config_not_found(self, temp_config_file):
        """Попытка получить несуществующий ресурс → KeyError."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        with pytest.raises(KeyError, match="Ресурс не найден: nonexistent"):
            cm.get_resource_config("nonexistent")

    # ========================================================================
    # ДИНАМИЧЕСКАЯ ПЕРЕЗАГРУЗКА (HOT-RELOAD)
    # ========================================================================

    def test_hot_reload_updates_config(self, temp_config_file):
        """reload() должен обновить конфиг после изменения файла."""
        cm = ConfigManager(temp_config_file, auto_reload=False)

        # Меняем температуру
        data = yaml.safe_load(Path(temp_config_file).read_text(encoding="utf-8"))
        data["agents"]["test-agent"]["temperature"] = 0.9
        Path(temp_config_file).write_text(yaml.dump(data), encoding="utf-8")

        cm.reload()
        new_temp = cm.get_agent_config("test-agent").temperature
        assert new_temp == 0.9

    def test_reload_with_invalid_syntax_logs_error(self, temp_config_file, caplog):
        """При синтаксической ошибке в YAML → ValidationError, старый конфиг сохраняется."""
        cm = ConfigManager(temp_config_file, auto_reload=False)

        # Пишем битый YAML
        Path(temp_config_file).write_text("agents:\n  test-agent:\n    model: gpt-4\n    bad-indent >> key", encoding="utf-8")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(yaml.YAMLError):
                cm.reload()

        # Старая конфигурация должна остаться
        assert cm.get_agent_config("test-agent").temperature == 0.7

    def test_reload_with_validation_error_preserves_old_config(self, temp_config_file, caplog):
        """Если новый конфиг не проходит валидацию — старый не теряется."""
        cm = ConfigManager(temp_config_file, auto_reload=False)

        data = yaml.safe_load(Path(temp_config_file).read_text(encoding="utf-8"))
        data["agents"]["test-agent"]["temperature"] = 999  # invalid
        Path(temp_config_file).write_text(yaml.dump(data), encoding="utf-8")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):  # ValidationError или другая ошибка
                cm.reload()

        # Старое значение сохранено
        assert cm.get_agent_config("test-agent").temperature == 0.7

    # ========================================================================
    # ОБНОВЛЕНИЕ В ПАМЯТИ
    # ========================================================================

    def test_update_agent_config_in_memory(self, temp_config_file):
        """update_agent_config() обновляет только в памяти."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        cm.update_agent_config("test-agent", {"temperature": 0.95, "max_tokens": 2048})

        cfg = cm.get_agent_config("test-agent")
        assert cfg.temperature == 0.95
        assert cfg.max_tokens == 2048

        # Перезагружаем — должно вернуться к диску
        cm.reload()
        assert cm.get_agent_config("test-agent").temperature == 0.7

    def test_update_agent_config_validation_error(self, temp_config_file):
        """Обновление с невалидными данными → ValidationError, старое значение остаётся."""
        cm = ConfigManager(temp_config_file, auto_reload=False)

        with pytest.raises(Exception):  # ValidationError
            cm.update_agent_config("test-agent", {"temperature": 999})

        assert cm.get_agent_config("test-agent").temperature == 0.7

    # ========================================================================
    # WATCHDOG / HOT-RELOAD LIFECYCLE (с моками)
    # ========================================================================

    @patch("ai_config_manager.config_manager.Observer")
    def test_start_watching_creates_observer(self, mock_observer, temp_config_file):
        """При auto_reload=True создаётся Observer."""
        observer_instance = MagicMock()
        mock_observer.return_value = observer_instance

        cm = ConfigManager(temp_config_file, auto_reload=True)

        mock_observer.assert_called_once()
        observer_instance.schedule.assert_called_once()
        observer_instance.start.assert_called_once()
        assert cm._observer is observer_instance

    @patch("ai_config_manager.config_manager.Observer")
    def test_stop_watching_stops_observer(self, mock_observer, temp_config_file):
        """stop_watching() останавливает Observer."""
        observer_instance = MagicMock()
        mock_observer.return_value = observer_instance

        cm = ConfigManager(temp_config_file, auto_reload=True)
        cm.stop_watching()

        observer_instance.stop.assert_called_once()
        observer_instance.join.assert_called_once()
        assert cm._observer is None

    @patch("ai_config_manager.config_manager.Observer")
    def test_context_manager_stops_observer(self, mock_observer, temp_config_file):
        """Контекстный менеджер автоматически останавливает наблюдение."""
        observer_instance = MagicMock()
        mock_observer.return_value = observer_instance

        with ConfigManager(temp_config_file, auto_reload=True) as cm:
            assert cm._observer is not None

        observer_instance.stop.assert_called_once()
        assert cm._observer is None

    @patch("ai_config_manager.config_manager.Observer")
    def test_no_observer_when_auto_reload_false(self, mock_observer, temp_config_file):
        """При auto_reload=False Observer не создаётся."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        mock_observer.assert_not_called()
        assert cm._observer is None

    # ========================================================================
    # ПОТОКОБЕЗОПАСНОСТЬ
    # ========================================================================

    def test_thread_safety_update_agent_config(self, temp_config_file):
        """update_agent_config() потокобезопасен."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        errors = []

        def worker(i):
            try:
                cm.update_agent_config("test-agent", {"temperature": 0.1 + i * 0.1})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        final_temp = cm.get_agent_config("test-agent").temperature
        assert 0.0 <= final_temp <= 2.0

    # ========================================================================
    # БЕЗОПАСНОСТЬ: логи, секреты
    # ========================================================================

    def test_secrets_not_logged_in_clear_text(self, temp_config_file, caplog):
        """Секреты не попадают в логи в открытом виде."""
        with caplog.at_level(logging.INFO):
            cm = ConfigManager(temp_config_file, auto_reload=False)
            cm.get_config()

        log_text = caplog.text
        assert "sk-test-1234567890abcdef" not in log_text
        assert "openai" not in log_text.lower()  # если маскируешь ключи

    # ========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ ТЕСТЫ
    # ========================================================================

    def test_validate_returns_true_for_valid_config(self, temp_config_file):
        """validate() возвращает True для валидного конфига."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        assert cm.validate() is True

    def test_get_config_caches_result(self, temp_config_file):
        """get_config() кэширует объект (одинаковые экземпляры)."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        cfg1 = cm.get_config()
        cfg2 = cm.get_config()
        assert cfg1 is cfg2

    def test_config_manager_requires_load_before_get(self, temp_config_file):
        """get_config() без загрузки → RuntimeError."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        cm._config = None  # принудительно сбрасываем
        with pytest.raises(RuntimeError, match="Конфигурация не загружена"):
            cm.get_config()

    def test_repr_does_not_expose_secrets(self, temp_config_file):
        """__repr__ ConfigManager не показывает секреты."""
        cm = ConfigManager(temp_config_file, auto_reload=False)
        repr_str = repr(cm)
        assert "sk-" not in repr_str
        assert "api_keys" not in repr_str.lower()