#!/usr/bin/env python3
"""Security unit tests for TriggerAction.execute().

These tests MUST NOT execute real external processes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _silence_logging() -> None:
    import logging

    logging.getLogger("agents.cognitive_agent.scripts.trigger_processor").setLevel(logging.CRITICAL)


def _write_safe_mode(tmp_path: Path, mode: str) -> None:
    safe_mode_path = tmp_path / "agents" / "cognitive_agent" / "config" / "safe_mode.yaml"
    safe_mode_path.parent.mkdir(parents=True, exist_ok=True)

    # Minimal structure expected by load_safe_mode()
    safe_mode_path.write_text(
        f"mode: {mode}\nrequire_approval: false\nlog_all_actions: true\n",
        encoding="utf-8",
    )


def test_execute_allows_whitelisted_executable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Arrange safe mode to NORMAL by writing into a temp location and monkeypatching the constant.
    from agents.cognitive_agent.scripts import trigger_processor as tp

    _write_safe_mode(tmp_path, "NORMAL")
    monkeypatch.setattr(tp, "SAFE_MODE_CONFIG", tmp_path / "agents" / "cognitive_agent" / "config" / "safe_mode.yaml")

    called: dict[str, Any] = {}

    def fake_run(cmd: list[str], **kwargs: Any) -> Any:
        called["cmd"] = cmd
        called["cwd"] = kwargs.get("cwd")

        class R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return R()

    monkeypatch.setattr(tp.subprocess, "run", fake_run)
    monkeypatch.setattr(tp.shutil, "which", lambda x: f"C:/Resolved/{x}" if x else None)

    action = tp.TriggerAction(
        name="t",
        executable="python",
        args=["--version"],
        timeout=5,
        allowed_failures=0,
    )

    # Act
    res = action.execute()

    # Assert
    assert res["success"] is True
    assert called["cmd"][0].lower().endswith("python.exe") or called["cmd"][0].lower().endswith("python")
    assert called["cmd"][1] == "--version"


def test_execute_rejects_dangerous_chars_in_args(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from agents.cognitive_agent.scripts import trigger_processor as tp

    _write_safe_mode(tmp_path, "NORMAL")
    monkeypatch.setattr(tp, "SAFE_MODE_CONFIG", tmp_path / "agents" / "cognitive_agent" / "config" / "safe_mode.yaml")

    # If validation fails, subprocess.run must never be called.
    monkeypatch.setattr(
        tp.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("subprocess.run called"))
    )

    action = tp.TriggerAction(
        name="t",
        executable="echo",
        args=["hello; rm -rf /"],
        timeout=5,
        allowed_failures=0,
    )

    res = action.execute()
    assert res["success"] is False
    assert res["stderr"] == "Command validation failed"


@pytest.mark.parametrize("mode", ["SAFE_READ_ONLY", "LOCKDOWN"])
def test_safe_mode_blocks_execution_in_processor(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mode: str) -> None:
    from agents.cognitive_agent.scripts import trigger_processor as tp

    _write_safe_mode(tmp_path, mode)
    monkeypatch.setattr(tp, "SAFE_MODE_CONFIG", tmp_path / "agents" / "cognitive_agent" / "config" / "safe_mode.yaml")

    # Build config file with an action that would be allowed in NORMAL.
    triggers_yaml = tmp_path / "triggers.yaml"
    triggers_yaml.write_text(
        """
version: "1.0.0"
triggers:
  file_change:
    enabled: true
    conditions: []
    actions: [echo_ok]
actions:
  echo_ok:
    executable: echo
    args: [ok]
    timeout: 5
    allowed_failures: 0
""".lstrip(),
        encoding="utf-8",
    )

    processor = tp.TriggerProcessor(config_path=str(triggers_yaml))
    event = tp.TriggerEvent(name="file_change", source="test", data={})

    assert processor.process_event(event) is False
