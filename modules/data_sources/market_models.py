from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SharedData:
    symbol: str
    volume: int
    source: str
    timestamp: datetime

@dataclass(slots=True)
class Quote(SharedData):
    bid: float
    ask: float
    last: float

@dataclass(slots=True)
class Candle(SharedData):
    open: float
    high: float
    low: float
    close: float