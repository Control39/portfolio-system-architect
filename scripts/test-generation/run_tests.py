#!/usr/bin/env python3
"""Запуск тестов с таймаутом"""

import subprocess
import sys

# Запустить pytest с таймаутом
result = subprocess.run(
    [sys.executable, "-m", "pytest", "src/test_main.py", "-v", "--tb=short"],
    timeout=120,  # 2 минуты
    capture_output=False,
)

sys.exit(result.returncode)
