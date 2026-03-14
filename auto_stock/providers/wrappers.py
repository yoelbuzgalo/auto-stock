from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime
from typing import TypeVar, cast

T = TypeVar("T")

from auto_stock.domain.market import Candle, ProviderStatus, Quote
from auto_stock.infra.errors import ProviderError
from auto_stock.providers.base import MarketDataProvider


class CachingMarketDataProvider(MarketDataProvider):
    def __init__(self, inner: MarketDataProvider, ttl_seconds: int) -> None:
        self.inner = inner
        self.ttl_seconds = ttl_seconds
        self.name = inner.name
        self._cache: dict[str, tuple[float, object]] = {}

    def get_quote(self, symbol: str) -> Quote:
        return self._get_cached(f"quote:{symbol}", lambda: self.inner.get_quote(symbol))

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        cache_key = f"candles:{symbol}:{timeframe}:{start.isoformat()}:{end.isoformat()}"
        return self._get_cached(cache_key, lambda: self.inner.get_candles(symbol, timeframe, start, end))

    def check_health(self) -> ProviderStatus:
        return self.inner.check_health()

    def _get_cached(self, key: str, loader: Callable[[], T]) -> T:
        now = time.monotonic()
        cached = self._cache.get(key)
        if cached and now - cached[0] <= self.ttl_seconds:
            return cast(T, cached[1])
        value = loader()
        self._cache[key] = (now, value)
        return value


class RetryingMarketDataProvider(MarketDataProvider):
    def __init__(self, inner: MarketDataProvider, max_attempts: int) -> None:
        self.inner = inner
        self.max_attempts = max(1, max_attempts)
        self.name = inner.name

    def get_quote(self, symbol: str) -> Quote:
        return self._run(lambda: self.inner.get_quote(symbol))

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        return self._run(lambda: self.inner.get_candles(symbol, timeframe, start, end))

    def check_health(self) -> ProviderStatus:
        return self.inner.check_health()

    def _run(self, callback: Callable[[], T]) -> T:
        last_error: ProviderError | None = None
        for _ in range(self.max_attempts):
            try:
                return callback()
            except ProviderError as exc:
                last_error = exc
        raise last_error or ProviderError("Market data request failed.")
