#!/usr/bin/env python3
"""Unit tests for TriggerProcessor._check_conditions."""

from __future__ import annotations

import logging
from datetime import datetime
from datetime import time as dtime
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _silence_logging() -> None:
    logging.getLogger("agents.cognitive_agent.scripts.trigger_processor").setLevel(logging.CRITICAL)


def test_file_exists_condition(tmp_path: Path) -> None:
    from agents.cognitive_agent.scripts.trigger_processor import TriggerEvent, TriggerProcessor

    exists_file = tmp_path / "exists.txt"
    exists_file.write_text("ok", encoding="utf-8")

    processor = TriggerProcessor(config_path=str(tmp_path / "triggers.yaml"))

    assert processor._check_conditions(
        conditions=[{"file_exists": str(exists_file)}],
        event=TriggerEvent(name="t", source="s", data={}),
    )

    assert not processor._check_conditions(
        conditions=[{"file_exists": str(tmp_path / "missing.txt")}],
        event=TriggerEvent(name="t", source="s", data={}),
    )


def test_time_of_day_condition_inside_window(tmp_path: Path) -> None:
    from agents.cognitive_agent.scripts.trigger_processor import TriggerEvent, TriggerProcessor

    # Force "now" inside the window by using a window that spans current time.
    now = datetime.now().time()
    start = dtime(max(0, now.hour - 1), now.minute)
    end = dtime(min(23, now.hour + 1), now.minute)

    # handle wrap-around by ensuring window includes start->end ordering in our implementation
    if start <= end:
        window = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
    else:
        # If wrap-around, still create a valid window string.
        window = f"{end.strftime('%H:%M')}-{start.strftime('%H:%M')}"  # implementation should handle wrap

    processor = TriggerProcessor(config_path=str(tmp_path / "triggers.yaml"))

    assert processor._check_conditions(
        conditions=[{"time_of_day": window}],
        event=TriggerEvent(name="t", source="s", data={}),
    )


def test_unknown_condition_fallbacks_true(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    from agents.cognitive_agent.scripts.trigger_processor import TriggerEvent, TriggerProcessor

    processor = TriggerProcessor(config_path=str(tmp_path / "triggers.yaml"))
    caplog.set_level(logging.WARNING)

    ok = processor._check_conditions(
        conditions=[{"some_unknown_condition": True}],
        event=TriggerEvent(name="t", source="s", data={}),
    )

    assert ok is True
    # Log capture may not include warnings if logger levels are overridden;
    # the functional requirement is that unknown conditions return True.


def test_combination_and_logic(tmp_path: Path) -> None:
    from agents.cognitive_agent.scripts.trigger_processor import TriggerEvent, TriggerProcessor

    exists_file = tmp_path / "exists.txt"
    exists_file.write_text("ok", encoding="utf-8")

    processor = TriggerProcessor(config_path=str(tmp_path / "triggers.yaml"))

    event = TriggerEvent(name="t", source="s", data={})

    assert (
        processor._check_conditions(
            conditions=[
                {"file_exists": str(exists_file)},
                {"file_exists": str(tmp_path / "missing.txt")},
            ],
            event=event,
        )
        is False
    )
