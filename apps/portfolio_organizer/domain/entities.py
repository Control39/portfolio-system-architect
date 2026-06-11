# src/domain/portfolio/entities.py

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Portfolio:
    """
    Портфолио — коллекция доказательств компетенций владельца.

    В экосистеме Portfolio System Architect портфолио — это не про деньги.
    Это про карьеру, навыки и их подтверждение.

    Портфолио отвечает на вопрос:
    "Какие у меня есть доказательства того, что я обладаю нужными компетенциями?"
    """

    id: UUID
    owner_id: UUID  # Владелец (из auth_service)
    name: str  # Название портфолио

    # Основная связь с методологией
    compass_markers: list[str]  # Какие маркеры IT-Compass относятся

    created_at: datetime
    updated_at: datetime


@dataclass
class Project:
    """
    Проект — единица работы, содержащая доказательства.

    Не "проект" в смысле бизнес-проекта, а артефакт,
    демонстрирующий применение компетенций.
    """

    id: UUID
    portfolio_id: UUID  # К какому портфолио относится

    name: str
    description: str

    # Доказательства
    evidence_links: list[str]  # Ссылки на PR, документацию, код
    test_coverage: float | None  # Покрытие тестами (из system_proof)
    security_score: float | None  # Security score (из system_proof)

    # Связь с компетенциями
    demonstrated_markers: list[str]  # Какие маркеры доказаны этим проектом

    created_at: datetime
    updated_at: datetime  # Добавлено для согласованности
