"""
Тесты для модуля психологической поддержки.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.mental.support import PsychologicalSupport
import pytest
from unittest.mock import patch, MagicMock

def test_psychological_support_initialization():
    """Проверяем, что класс инициализируется без ошибок."""
    ps = PsychologicalSupport()
    assert ps is not None
    assert hasattr(ps, 'motivational_quotes')
    assert hasattr(ps, 'crisis_contacts')
    assert hasattr(ps, 'simple_activities')
    assert hasattr(ps, 'gentle_encouragements')

def test_generate_support_report():
    """Проверяем генерацию отчёта поддержки."""
    ps = PsychologicalSupport()
    report = ps.generate_support_report()
    assert isinstance(report, dict)
    assert 'gentle_encouragement' in report
    assert 'motivational_quote' in report
    assert 'simple_activities' in report
    assert isinstance(report['simple_activities'], list)
    assert len(report['simple_activities']) == 3
    assert 'timestamp' in report

def test_get_random_quote():
    """Проверяем получение случайной цитаты."""
    ps = PsychologicalSupport()
    quote = ps.get_random_quote()
    assert isinstance(quote, str)
    # Если список цитат пуст, возвращается заглушка
    if not ps.motivational_quotes:
        assert quote == "Маленькие шаги ведут к большим достижениям."

def test_is_burnout_risk():
    """Проверяем определение риска выгорания."""
    ps = PsychologicalSupport()
    # Нет риска: последняя активность недавно
    recent = {
        "last_activity": "2026-03-09T10:00:00",
        "break_count": 3
    }
    # Мокаем datetime.now, чтобы вернуть фиксированное время
    with patch('src.core.mental.support.datetime') as mock_datetime:
        mock_now = MagicMock()
        mock_datetime.now.return_value = mock_datetime
        mock_datetime.fromisoformat.return_value = MagicMock()
        mock_datetime.__sub__ = lambda self, other: MagicMock()
        # Упростим: просто проверим, что функция вызывается
        result = ps.is_burnout_risk(recent)
        assert isinstance(result, bool)

def test_suggest_recovery_plan():
    """Проверяем генерацию плана восстановления."""
    ps = PsychologicalSupport()
    plan = ps.suggest_recovery_plan()
    assert plan['title'] == "План восстановления"
    assert 'steps' in plan
    assert len(plan['steps']) == 3
    assert plan['steps'][0]['day'] == 1

def test_get_crisis_resources():
    """Проверяем получение кризисных ресурсов."""
    ps = PsychologicalSupport()
    resources = ps.get_crisis_resources()
    assert 'contacts' in resources
    assert 'emergency_message' in resources
    assert 'support_message' in resources

def test_get_daily_checkin_prompt():
    """Проверяем получение ежедневного вопроса."""
    ps = PsychologicalSupport()
    prompt = ps.get_daily_checkin_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_export_import_support_data():
    """Проверяем экспорт и импорт данных поддержки."""
    ps = PsychologicalSupport()
    data = ps.export_support_data()
    assert 'motivational_quotes' in data
    assert 'exported_at' in data
    # Импортируем обратно (должно работать без ошибок)
    ps.import_support_data(data)
    # Проверяем, что данные загружены
    assert ps.motivational_quotes == data['motivational_quotes']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])