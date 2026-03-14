from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from auto_stock.domain.market import Candle, ProviderStatus, Quote


class MarketDataProvider(ABC):
    name = "provider"

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
    ) -> list[Candle]:
        raise NotImplementedError

    @abstractmethod
    def check_health(self) -> ProviderStatus:
        raise NotImplementedError
