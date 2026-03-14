from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone

from auto_stock.domain.market import Candle, ProviderStatus, Quote
from auto_stock.infra.validation import as_utc, ensure_time_range, timeframe_delta
from auto_stock.providers.base import MarketDataProvider


class DemoMarketDataProvider(MarketDataProvider):
    name = "demo"

    def __init__(self, seed: int = 7) -> None:
        self.seed = seed

    def get_quote(self, symbol: str) -> Quote:
        now = datetime.now(timezone.utc)
        base_price = self._base_price(symbol)
        drift = ((now.minute % 9) - 4) * 0.14
        last = round(base_price + drift, 2)
        bid = round(last - 0.03, 2)
        ask = round(last + 0.03, 2)
        volume = 100_000 + self._symbol_hash(symbol) % 900_000
        return Quote(
            symbol=symbol,
            bid=bid,
            ask=ask,
            last=last,
            volume=volume,
            source=self.name,
            timestamp=now,
        )

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        start_utc, end_utc = ensure_time_range(start, end)
        step = timeframe_delta(timeframe)
        series: list[Candle] = []
        cursor = start_utc
        last_close = self._base_price(symbol)
        while cursor <= end_utc:
            rng = random.Random(self._symbol_hash(symbol) + int(cursor.timestamp()) + self.seed)
            move = rng.uniform(-1.2, 1.2)
            open_price = round(last_close, 2)
            close_price = round(max(1.0, open_price + move), 2)
            high_price = round(max(open_price, close_price) + rng.uniform(0.05, 0.9), 2)
            low_price = round(min(open_price, close_price) - rng.uniform(0.05, 0.9), 2)
            volume = int(50_000 + abs(move) * 30_000 + rng.randint(0, 10_000))
            series.append(
                Candle(
                    symbol=symbol,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                    source=self.name,
                    timestamp=as_utc(cursor),
                )
            )
            last_close = close_price
            cursor += step
        return series[-180:]

    def check_health(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.name,
            available=True,
            detail="Demo market data is active. No API credentials are required.",
        )

    def _base_price(self, symbol: str) -> float:
        return round(20.0 + (self._symbol_hash(symbol) % 25_000) / 100.0, 2)

    def _symbol_hash(self, symbol: str) -> int:
        digest = hashlib.sha256(f"{self.seed}:{symbol}".encode("utf-8")).hexdigest()
        return int(digest[:12], 16)
