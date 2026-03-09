"""
Тесты для CLI интерфейса IT Compass.
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, call
import builtins

# Добавляем путь к модулям
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Импортируем модули
try:
    from core.tracker import SkillTracker
    from cli.main import main, show_menu, show_directions, show_markers_for_direction, mark_marker_completed, show_progress, generate_portfolio
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    # Если модули не найдены, создадим заглушки для тестов
    class SkillTracker:
        pass

def test_show_menu(capsys):
    """Проверяем, что меню выводится без ошибок."""
    show_menu()
    captured = capsys.readouterr()
    assert "IT Compass" in captured.out
    assert "1. Просмотр направлений" in captured.out

def test_show_directions(capsys):
    """Проверяем вывод направлений."""
    tracker = MagicMock()
    tracker.get_directions.return_value = ["Python", "DevOps"]
    show_directions(tracker)
    captured = capsys.readouterr()
    assert "Доступные направления" in captured.out
    assert "Python" in captured.out
    assert "DevOps" in captured.out

def test_show_markers_for_direction(capsys):
    """Проверяем вывод маркеров для направления."""
    tracker = MagicMock()
    tracker.get_markers_by_direction.return_value = {
        "marker1": {"title": "Основы Python", "level": "junior"},
        "marker2": {"title": "ООП", "level": "middle"}
    }
    tracker.progress = {'completed': {}, 'in_progress': set()}
    show_markers_for_direction(tracker, "Python")
    captured = capsys.readouterr()
    assert "Маркеры для направления" in captured.out
    assert "Основы Python" in captured.out

def test_mark_marker_completed(monkeypatch, capsys):
    """Проверяем процесс отметки маркера как выполненного."""
    tracker = MagicMock()
    tracker.get_directions.return_value = ["Python", "DevOps"]
    tracker.get_markers_by_direction.return_value = {
        "marker1": {"title": "Основы Python", "level": "junior"}
    }
    tracker.progress = {'completed': {}, 'in_progress': set()}
    # Мокаем ввод пользователя
    inputs = iter(["1", "1", ""])  # выбираем направление 1, маркер 1, артефакт пустой
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    mark_marker_completed(tracker)
    captured = capsys.readouterr()
    assert "Маркер" in captured.out or "отмечен как выполненный" in captured.out
    # Проверяем, что метод mark_completed был вызван
    tracker.mark_completed.assert_called_once_with("marker1", None)

def test_show_progress(capsys):
    """Проверяем вывод статистики прогресса."""
    tracker = MagicMock()
    tracker.get_progress_stats.return_value = {
        'completed': 5,
        'in_progress': 3,
        'total': 20,
        'completion_rate': 25.0
    }
    show_progress(tracker)
    captured = capsys.readouterr()
    assert "Статистика прогресса" in captured.out
    assert "5" in captured.out
    assert "25.0%" in captured.out

def test_generate_portfolio(monkeypatch, capsys, tmp_path):
    """Проверяем генерацию портфолио."""
    tracker = MagicMock()
    generator = MagicMock()
    generator.generate_portfolio.return_value = "<html>portfolio</html>"
    # Мокаем PortfolioGenerator
    with patch('cli.main.PortfolioGenerator', return_value=generator):
        # Мокаем ввод пользователя
        inputs = iter(["1"])  # выбираем Markdown
        monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
        # Мокаем open для записи файла
        mock_file = MagicMock()
        with patch('builtins.open', mock_file):
            generate_portfolio(tracker)
    captured = capsys.readouterr()
    assert "Генерация портфолио" in captured.out
    generator.generate_portfolio.assert_called_once_with("markdown")

def test_main_exit(monkeypatch, capsys):
    """Проверяем выход из приложения."""
    # Мокаем ввод: сразу выход
    inputs = iter(["0"])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    # Мокаем SkillTracker
    with patch('cli.main.SkillTracker', MagicMock()):
        main()
    captured = capsys.readouterr()
    assert "До свидания" in captured.out

if __name__ == '__main__':
    pytest.main([__file__, '-v'])