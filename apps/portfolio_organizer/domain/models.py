"""Domain models for Portfolio Organizer."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PortfolioAnalysis:
    user_id: str
    analysis_date: datetime
    total_value: float
    risk_level: str
    recommendations: list[str]


@dataclass
class ProofItem:
    item_id: str
    user_id: str
    proof_type: str
    status: str
    created_at: datetime
    verified_at: datetime | None = None


@dataclass
class Portfolio:
    user_id: str
    name: str
    currency: str
    items: list[dict]
