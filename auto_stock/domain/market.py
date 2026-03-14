from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    source: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def spread(self) -> float:
        return round(max(self.ask - self.bid, 0.0), 4)  # type: ignore

    @property
    def mid_price(self) -> float:
        return round((self.ask + self.bid) / 2, 4)  # type: ignore


@dataclass(frozen=True, slots=True)
class Candle:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    source: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    provider_name: str
    available: bool
    detail: str
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
