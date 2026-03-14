from __future__ import annotations

from datetime import datetime
from typing import List, Any, Optional

from data_sources.base_provider import MarketDataProvider
from data_sources.market_models import Quote, Candle


class SchwabDataSource(MarketDataProvider):
    def __init__(self, base_url: str, access_token: Optional[str] = None) -> None:
        self.base_url = base_url
        self.access_token = access_token

    def get_quote(self, symbol: str) -> Quote:
        """
        Fetch a quote from Schwab market data endpoints.
        """
        raise NotImplementedError("Implement Schwab quote request.")

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> List[Candle]:
        """
        Fetch historical candles from Schwab.
        """
        raise NotImplementedError("Implement Schwab candles request.")

    def is_available(self) -> bool:
        """
        Optional health check or lightweight endpoint check.
        """
        return True

    def normalize_quote(self, raw: Any) -> Quote:
        """
        Convert Schwab-specific quote JSON into Quote model.
        """
        raise NotImplementedError("Implement Schwab quote normalization.")

    def normalize_candles(self, raw: Any) -> List[Candle]:
        """
        Convert Schwab-specific candles JSON into List[Candle].
        """
        raise NotImplementedError("Implement Schwab candle normalization.")