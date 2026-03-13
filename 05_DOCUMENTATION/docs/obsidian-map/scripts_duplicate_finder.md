# Duplicate Finder

- **Путь**: `scripts\duplicate_finder.py`
- **Тип**: .PY
- **Размер**: 10,015 байт
- **Последнее изменение**: 2026-03-05 05:17:36

## Превью

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для поиска дублирующихся файлов в директории проекта по хешу содержимого.
Рекурсивно обходит все поддиректории, игнорируя системные директории.
Выводит таблицу с названием файла, содержимым и путем для найденных дубликатов.
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

# Установка кодировки для корректного отображения кириллицы в консоли Windows
if os.name == 'nt':

... (файл продолжается)
```
