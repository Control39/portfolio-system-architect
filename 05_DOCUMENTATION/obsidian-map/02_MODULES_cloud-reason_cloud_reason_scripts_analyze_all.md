# Analyze All

- **Путь**: `02_MODULES\cloud-reason\cloud_reason\scripts\analyze_all.py`
- **Тип**: .PY
- **Размер**: 6,492 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ всех текстовых файлов в проекте на предмет кодировки.
Поддерживает кириллицу в путях и названиях файлов.
"""
import os
import chardet
import logging
from pathlib import Path
import json
from typing import Dict, List, Tuple

def setup_logging() -> None:
    """Настройка системы логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            loggi
... (файл продолжается)
```
