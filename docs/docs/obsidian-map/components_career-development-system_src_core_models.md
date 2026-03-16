# Models

- **Путь**: `components\career-development-system\src\core\models.py`
- **Тип**: .PY
- **Размер**: 2,351 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    # Отношения
    skills = relationship("Skill", back_populates="user")
    progress_records 
... (файл продолжается)
```
