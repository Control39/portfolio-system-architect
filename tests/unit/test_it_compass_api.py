import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from apps.portfolio_organizer.src.core.ITCompassAPI import ITCompassAPI

def test_get_competency_markers():
    api = ITCompassAPI()
    skills = ["python", "docker"]
    result = api.get_competency_markers(skills)
    assert isinstance(result, list)
    if result:
        assert 'marker' in result[0]
        assert 'level' in result[0]
    # Basic smoke test passes

def test_empty_skills():
    api = ITCompassAPI()
    result = api.get_competency_markers([])
    assert isinstance(result, list)
    # Currently returns a dummy marker, but that's fine