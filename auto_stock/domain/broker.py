from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(StrEnum):
    NEW = "NEW"
    WORKING = "WORKING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class OrderLeg:
    symbol: str
    instruction: str
    quantity: float


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    status: OrderStatus
    quantity: float
    time_in_force: str
    price: float | None = None
    legs: tuple[OrderLeg, ...] = ()
    source: str = "broker"
    entered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class Position:
    symbol: str
    quantity: float
    average_price: float
    market_value: float


@dataclass(frozen=True, slots=True)
class Account:
    account_id: str
    account_type: str
    cash_balance: float
    buying_power: float
    equity: float


@dataclass(frozen=True, slots=True)
class BrokerSnapshot:
    account: Account | None = None
    positions: tuple[Position, ...] = ()
    orders: tuple[Order, ...] = ()


@dataclass(frozen=True, slots=True)
class BrokerStatus:
    broker_name: str
    available: bool
    detail: str
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
