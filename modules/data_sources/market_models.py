from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    timestamp: datetime
    source: str

@dataclass(slots=True)
class Ohlcv:
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(slots=True)
class Candle(Ohlcv):
    symbol: str
    timestamp: datetime
    source: str

