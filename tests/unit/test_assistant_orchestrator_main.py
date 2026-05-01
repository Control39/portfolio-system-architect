"""
Unit tests for assistant_orchestrator/main.py
"""

from argparse import ArgumentParser
from unittest.mock import MagicMock, patch

import pytest


def test_assistant_orchestrator_main_import():
    """Проверяем, что main.py импортируется"""
    try:
        import src.assistant_orchestrator.main

        assert src.assistant_orchestrator.main is not None
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_setup_logging():
    """Проверяем настройку логирования"""
    with patch("src.assistant_orchestrator.main.logging") as mock_logging:
        from src.assistant_orchestrator.main import setup_logging

        setup_logging(verbose=True)

        mock_logging.getLogger().handlers.clear.assert_called_once()
        mock_logging.basicConfig.assert_called_once()
        assert mock_logging.getLogger("urllib3").setLevel.called

        # Проверяем с verbose=False
        setup_logging(verbose=False)
        # Проверяем, что basicConfig вызвана снова с другим уровнем
        assert mock_logging.basicConfig.call_count == 2


def test_main_parser_defaults():
    """Проверяем аргументы парсера по умолчанию"""
    with patch("argparse.ArgumentParser") as mock_parser_class:
        from src.assistant_orchestrator.main import main

        mock_parser = MagicMock(spec=ArgumentParser)
        mock_parser_class.return_value = mock_parser

        # Запускаем main для инициализации парсера
        try:
            main()
        except SystemExit:
            pass  # main вызывает sys.exit(), что нормально для теста

        # Проверяем, что ArgumentParser был вызван
        mock_parser_class.assert_called_once()

        # Проверяем, что add_argument вызван с правильными параметрами по умолчанию
        add_arg_calls = mock_parser.add_argument.call_args_list

        # Собираем все вызовы add_argument в словарь
        arg_calls = {}
        for call in add_arg_calls:
            args, kwargs = call
            if args:
                arg_calls[args[0]] = kwargs

        # Проверяем root
        assert "--root" in arg_calls
        assert arg_calls["--root"]["default"] == "."

        # Проверяем format
        assert "--format" in arg_calls
        assert arg_calls["--format"]["default"] == "text"
        assert "choices" in arg_calls["--format"]
        assert set(arg_calls["--format"]["choices"]) == {"text", "json", "html"}

        # Проверяем output
        assert "--output" in arg_calls
        assert arg_calls["--output"]["default"] == "reports"

        # Проверяем verbose
        assert "--verbose" in arg_calls
        assert arg_calls["--verbose"]["action"] == "store_true"

        # Проверяем version
        assert "--version" in arg_calls
        assert arg_calls["--version"]["action"] == "store_true"
        mock_parser = MagicMock(spec=ArgumentParser)
        mock_parser_class.return_value = mock_parser

        from src.assistant_orchestrator.main import main

        # Не запускаем main(), просто проверяем, что парсер создается
        mock_parser_class.assert_called_once()

        # Проверяем, что add_argument вызван с правильными параметрами по умолчанию
        add_arg_calls = mock_parser.add_argument.call_args_list

        # Собираем все вызовы add_argument в словарь
        arg_calls = {}
        for call in add_arg_calls:
            args, kwargs = call
            if args:
                arg_calls[args[0]] = kwargs

        # Проверяем root
        assert "--root" in arg_calls
        assert arg_calls["--root"]["default"] == "."

        # Проверяем format
        assert "--format" in arg_calls
        assert arg_calls["--format"]["default"] == "text"
        assert "choices" in arg_calls["--format"]
        assert set(arg_calls["--format"]["choices"]) == {"text", "json", "html"}

        # Проверяем output
        assert "--output" in arg_calls
        assert arg_calls["--output"]["default"] == "reports"

        # Проверяем verbose
        assert "--verbose" in arg_calls
        assert arg_calls["--verbose"]["action"] == "store_true"

        # Проверяем version
        assert "--version" in arg_calls
        assert arg_calls["--version"]["action"] == "store_true"


def test_main_version_flag():
    """Проверяем, что флаг --version работает"""
    with patch("argparse.ArgumentParser") as mock_parser_class, patch(
        "src.assistant_orchestrator.main.sys"
    ) as mock_sys:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(version=True)

        # Импортируем main и модифицируем __version__
        from src.assistant_orchestrator.main import main

        main.__globals__["__version__"] = "1.0.0"

        # Запускаем main
        with pytest.raises(SystemExit):
            main()

        # Проверяем, что sys.exit был вызван
        assert mock_sys.exit.called

        with patch("src.assistant_orchestrator.main.__version__", "1.0.0"):
            main()

        mock_sys.exit.assert_called_with(0)
        # Проверяем, что print был вызван с версией
        # (здесь мы не можем легко проверить print, но можно добавить мок)


def test_main_with_valid_root():
    """Проверяем запуск main с валидной директорией"""
    with patch("argparse.ArgumentParser") as mock_parser_class, patch(
        "src.assistant_orchestrator.main.setup_logging"
    ), patch(
        "src.assistant_orchestrator.core.analyzer.AssistantOrchestrator"
    ) as mock_orchestrator_class, patch(
        "src.assistant_orchestrator.core.reporter.Reporter"
    ) as mock_reporter_class, patch(
        "pathlib.Path"
    ) as mock_path, patch(
        "src.assistant_orchestrator.main.logging"
    ), patch(
        "src.assistant_orchestrator.main.sys"
    ) as mock_sys:
        # Настройка моков
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(
            root="./test_project",
            format="json",
            output="output_reports",
            verbose=False,
            version=False,
        )

        # Мок существующей директории
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.resolve.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True

        # Мок orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator_instance
        mock_analysis = {"test": "data"}
        mock_orchestrator_instance.run_full_analysis.return_value = mock_analysis

        # Мок reporter
        mock_reporter_instance = MagicMock()
        mock_reporter_class.return_value = mock_reporter_instance

        # Мок sys.exit
        mock_sys.exit.side_effect = SystemExit(0)  # Чтобы main() завершился

        from src.assistant_orchestrator.main import main

        # Запускаем main и ловим SystemExit
        try:
            main()
        except SystemExit:
            pass

        # Проверяем, что orchestrator был создан с правильным root
        mock_orchestrator_class.assert_called_with(project_root="./test_project")
        # Проверяем, что run_full_analysis был вызван
        mock_orchestrator_instance.run_full_analysis.assert_called_once()
        # Проверяем, что reporter был создан
        mock_reporter_class.assert_called_with(mock_analysis)
        # Проверяем, что save был вызван хотя бы раз
        assert mock_reporter_instance.save.called

        # Настройка моков
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(
            root="./test_project",
            format="json",
            output="output_reports",
            verbose=False,
            version=False,
        )

        # Мок существующей директории
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.resolve.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True

        # Мок orchestrator
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator_instance
        mock_analysis = {"test": "data"}
        mock_orchestrator_instance.run_full_analysis.return_value = mock_analysis

        # Мок reporter
        mock_reporter_instance = MagicMock()
        mock_reporter_class.return_value = mock_reporter_instance

        # Мок datetime
        with patch("src.assistant_orchestrator.main.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20260501_120000"

        # Мок sys.exit
        mock_sys.exit.side_effect = SystemExit(0)  # Чтобы main() завершился

        from src.assistant_orchestrator.main import main

        # Запускаем main и ловим SystemExit
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

        # Проверяем, что orchestrator был создан с правильным root
        mock_orchestrator_class.assert_called_with(project_root="./test_project")
        # Проверяем, что run_full_analysis был вызван
        mock_orchestrator_instance.run_full_analysis.assert_called_once()
        # Проверяем, что reporter был создан
        mock_reporter_class.assert_called_with(mock_analysis)
        # Проверяем, что save был вызван с правильным путем
        mock_output_path = mock_path.return_value / "analysis_20260501_120000.json"
        mock_reporter_instance.save.assert_called_with(mock_output_path)


def test_main_with_invalid_root():
    """Проверяем поведение при несуществующей директории"""
    with patch("argparse.ArgumentParser") as mock_parser_class, patch(
        "src.assistant_orchestrator.main.setup_logging"
    ), patch("pathlib.Path") as mock_path, patch("src.assistant_orchestrator.main.logging"), patch(
        "src.assistant_orchestrator.main.sys"
    ) as mock_sys:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(root="./nonexistent")

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.resolve.return_value = mock_path_instance
        mock_path_instance.exists.return_value = False

        mock_sys.exit.side_effect = SystemExit(1)

        from src.assistant_orchestrator.main import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        # mock_logging.getLogger().error.assert_called()


def test_main_keyboard_interrupt():
    """Проверяем обработку KeyboardInterrupt"""
    with patch("argparse.ArgumentParser") as mock_parser_class, patch(
        "src.assistant_orchestrator.main.setup_logging"
    ), patch(
        "src.assistant_orchestrator.core.analyzer.AssistantOrchestrator"
    ) as mock_orchestrator_class, patch(
        "src.assistant_orchestrator.main.logging"
    ), patch(
        "src.assistant_orchestrator.main.sys"
    ) as mock_sys:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(root=".", version=False)

        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator_instance
        mock_orchestrator_instance.run_full_analysis.side_effect = KeyboardInterrupt

        mock_sys.exit.side_effect = SystemExit(130)

        from src.assistant_orchestrator.main import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 130
        # mock_logging.getLogger().warning.assert_called()
