from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any

from data_sources.market_models import Quote, Candle


class MarketDataProvider(ABC):
    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        raise NotImplementedError

    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> List[Candle]:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def normalize_quote(self, raw: Any) -> Quote:
        raise NotImplementedError

    @abstractmethod
    def normalize_candles(self, raw: Any) -> List[Candle]:
        raise NotImplementedError