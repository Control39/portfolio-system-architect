"""
Инициализация модуля src для Cognitive Agent
"""

# NOTE:
# This package __init__ previously imported a large part of the agent runtime.
# That caused pytest collection failures in isolated unit tests (side-effect imports).
#
# Keep __init__ lightweight. Import concrete modules directly where needed.

__all__: list[str] = []
