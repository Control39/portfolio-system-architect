# Git Fix History

- **Путь**: `components\cloud_reason\scripts\git_fix_history.py`
- **Тип**: .PY
- **Размер**: 11,841 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Подготовка коммитов для Git после конвертации кодировок.
Создает корректные коммиты, сохраняя историю изменений.
"""
import os
import subprocess
import logging
from pathlib import Path
import json
import shutil
from typing import Dict, List, Tuple
import datetime

def setup_logging() -> None:
    """Настройка системы логирования"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INF
... (файл продолжается)
```

