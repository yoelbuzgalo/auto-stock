from __future__ import annotations

from datetime import datetime, timedelta, timezone

from auto_stock.domain.market import Candle, ProviderStatus, Quote
from auto_stock.infra.validation import normalize_symbol, normalize_timeframe
from auto_stock.providers.base import MarketDataProvider

_DEFAULT_WINDOWS = {
    "1Min": timedelta(hours=6),
    "5Min": timedelta(days=5),
    "15Min": timedelta(days=14),
    "1Hour": timedelta(days=45),
    "1Day": timedelta(days=180),
}


class MarketService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def get_quote(self, symbol: str) -> Quote:
        normalized_symbol = normalize_symbol(symbol)
        return self.provider.get_quote(normalized_symbol)

    def get_history(
        self,
        symbol: str,
        *,
        timeframe: str = "1Day",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Candle]:
        normalized_symbol = normalize_symbol(symbol)
        normalized_timeframe = normalize_timeframe(timeframe)
        end_time = end or datetime.now(timezone.utc)
        start_time = start or (end_time - _DEFAULT_WINDOWS[normalized_timeframe])
        return self.provider.get_candles(normalized_symbol, normalized_timeframe, start_time, end_time)

    def get_status(self) -> ProviderStatus:
        return self.provider.check_health()
