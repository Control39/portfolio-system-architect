# Mental Support

- **Путь**: `02_MODULES\it-compass\src\core\mental_support.py`
- **Тип**: .PY
- **Размер**: 7,229 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
"""
Психологическая поддержка для IT Compass (совместимость с предыдущими версиями)
Обеспечивает интерфейс MentalSupport, MoodRecord, SelfHelpPractices,
используя объединённый модуль PsychologicalSupport.
"""

import json
import random
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from .mental.psychological_support import PsychologicalSupport as PS


class MoodRecord:
    """Запись психологического состояния пользователя"""
    
    def __init__(
        self,

... (файл продолжается)
```
