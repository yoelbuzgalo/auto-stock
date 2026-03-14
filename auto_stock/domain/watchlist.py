from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from auto_stock.domain.broker import OrderSide


@dataclass(frozen=True, slots=True)
class WatchlistItem:
    symbol: str
    note: str = ""
    target_price: float | None = None
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PlannedOrder:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    target_price: float | None = None
    note: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
