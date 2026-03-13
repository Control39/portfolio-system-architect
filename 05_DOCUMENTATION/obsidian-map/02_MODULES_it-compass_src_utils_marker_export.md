# Marker Export

- **Путь**: `02_MODULES\it-compass\src\utils\marker_export.py`
- **Тип**: .PY
- **Размер**: 10,944 байт
- **Последнее изменение**: 2026-03-05 05:17:34

## Превью

```
"""
Модуль экспорта маркеров для интеграции с LLM и RAG-системами.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from ..core.tracker import CareerTracker, Marker

logger = logging.getLogger(__name__)


class MarkerExporter:
    """Класс для экспорта маркеров в различные форматы для LLM и RAG-поиска."""

    def __init__(self, tracker: CareerTracker):
        self.tracker = tracker

    def export_to_llm_format(self, output_path: str) -> bool:
       
... (файл продолжается)
```
