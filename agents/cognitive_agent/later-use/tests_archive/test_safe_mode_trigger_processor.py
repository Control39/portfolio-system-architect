#!/usr/bin/env python3
"""Tests for safe_mode handling in TriggerProcessor."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

CONFIG_PATH = Path("agents/cognitive_agent/config/safe_mode.yaml")


def _write_safe_mode(mode: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "mode": mode,
        "require_approval": False,
        "log_all_actions": True,
    }
    CONFIG_PATH.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


@pytest.mark.parametrize(
    "mode,expected_allowed",
    [
        ("NORMAL", True),
        ("SAFE_READ_ONLY", False),
        ("LOCKDOWN", False),
    ],
)
def test_trigger_processor_safe_mode_blocks_or_allows(tmp_path: Path, mode: str, expected_allowed: bool) -> None:
    _write_safe_mode(mode)

    # Import inside the test so the module uses the current safe_mode.yaml value.
    from agents.cognitive_agent.scripts import trigger_processor as tp

    triggers_yaml = tmp_path / "triggers.yaml"
    triggers_yaml.write_text(
        yaml.safe_dump(
            {
                "version": "1.0.0",
                "triggers": {
                    "file_change": {
                        "enabled": True,
                        "conditions": [],
                        "actions": ["echo_ok"],
                    }
                },
                "actions": {
                    "echo_ok": {
                        "executable": "python",
                        "args": ["--version"],
                        "timeout": 5,
                        "allowed_failures": 0,
                    }
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    processor = tp.TriggerProcessor(config_path=str(triggers_yaml))
    event = tp.TriggerEvent(name="file_change", source="test", data={})

    assert processor.process_event(event) is expected_allowed
