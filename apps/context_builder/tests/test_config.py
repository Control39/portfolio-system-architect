# apps/context_builder/tests/test_config.py

from apps.context_builder.config.settings import settings


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("CONTEXT_BUILDER_PORT", "9000")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "5")

    from apps.context_builder.config.settings import settings as reloaded

    assert reloaded.service_port == 9000
    assert reloaded.debug is True
    assert reloaded.max_file_size_mb == 5


def test_output_dir_created():
    assert settings.output_dir.exists()
