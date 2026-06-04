import json
from pathlib import Path

import pytest

import sys
from pathlib import Path

# Ensure package import works when tests are executed without installing the project
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from assistant_orchestrator.core.analyzer import AssistantOrchestrator



def test_orchestrator_smoke(tmp_path: Path):
    """Smoke test: orchestrator should not crash and must return expected keys."""

    # Create minimal repository layout
    (tmp_path / "apps" / "it_compass" / "src" / "data" / "markers").mkdir(parents=True)
    # Minimal marker json so skills plugin can parse something
    (tmp_path / "apps" / "it_compass" / "src" / "data" / "markers" / "dummy.json").write_text(
        json.dumps({"description": "d", "levels": {"1": [{"id": "m1", "marker": "Marker 1", "evidence": []}]}}),
        encoding="utf-8",
    )

    orchestrator = AssistantOrchestrator(project_root=str(tmp_path))
    analysis = orchestrator.run_full_analysis()
    result = analysis.dict()

    assert "timestamp" in result
    assert "microservices" in result
    assert "skill_markers" in result
    assert "architecture_docs" in result
    assert "git_stats" in result
    assert "dependencies" in result

    assert isinstance(result["microservices"], dict)
    assert isinstance(result["skill_markers"], dict)
    assert "total_count" in result["skill_markers"]
