from __future__ import annotations

from datetime import datetime
from typing import List, Any

from data_sources.base_provider import MarketDataProvider
from data_sources.market_models import Quote, Candle


class AlpacaDataSource(MarketDataProvider):
    def __init__(self, api_key: str, api_secret: str, base_url: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def get_quote(self, symbol: str) -> Quote:
        raise NotImplementedError("Implement Alpaca quote request.")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> List[Candle]:
        raise NotImplementedError("Implement Alpaca candles request.")

    def is_available(self) -> bool:
        return True

    def normalize_quote(self, raw: Any) -> Quote:
        raise NotImplementedError("Implement Alpaca quote normalization.")

    def normalize_candles(self, raw: Any) -> List[Candle]:
        raise NotImplementedError("Implement Alpaca candle normalization.")