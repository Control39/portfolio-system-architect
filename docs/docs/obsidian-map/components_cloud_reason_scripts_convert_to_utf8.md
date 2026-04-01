# Convert To Utf8

- **Путь**: `components\cloud_reason\scripts\convert_to_utf8.py`
- **Тип**: .PY
- **Размер**: 11,159 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Массовая конвертация файлов в UTF-8 с резервным копированием.
Сохраняет оригинальные файлы в директории backups.
"""
import os
import shutil
import chardet
import logging
from pathlib import Path
import json
from typing import Dict, List, Tuple
import datetime

def setup_logging() -> None:
    """Настройка системы логирования"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,

... (файл продолжается)
```

