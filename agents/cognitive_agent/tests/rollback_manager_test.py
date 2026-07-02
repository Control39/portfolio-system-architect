#!/usr/bin/env python3
"""Критерий успеха для RollbackManager"""

import tempfile
from pathlib import Path

from agents.cognitive_agent.src.rollback_manager import RollbackManager

# Создать тестовый файл
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write("original content")
    test_file = f.name

manager = RollbackManager()
sid = manager.create_snapshot(test_file, "Test snapshot")
print(f"Snapshot created: {sid}")

# Изменить файл
Path(test_file).write_text("modified content")
print(f"File modified: {Path(test_file).read_text()}")

# Откатить
manager.rollback(sid)
print(f"After rollback: {Path(test_file).read_text()}")

# Очистить
Path(test_file).unlink()
print("✅ OK")
