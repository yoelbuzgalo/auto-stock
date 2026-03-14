from __future__ import annotations

from datetime import datetime, timezone

from auto_stock.domain.market import Candle, ProviderStatus, Quote
from auto_stock.infra.errors import HttpRequestError, ProviderError, ProviderUnavailableError
from auto_stock.infra.http import HttpClient
from auto_stock.infra.validation import ensure_time_range, polygon_timeframe
from auto_stock.providers.base import MarketDataProvider


class PolygonDataSource(MarketDataProvider):
    name = "polygon"

    def __init__(self, api_key: str | None, base_url: str, http_client: HttpClient) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    def get_quote(self, symbol: str) -> Quote:
        self._ensure_configured()
        try:
            raw_quote = self.http_client.request_json(
                "GET",
                f"{self.base_url}/v2/last/nbbo/{symbol}",
                params={"apiKey": self.api_key},
            )
            raw_trade = self.http_client.request_json(
                "GET",
                f"{self.base_url}/v2/last/trade/{symbol}",
                params={"apiKey": self.api_key},
            )
        except HttpRequestError as exc:
            raise ProviderError(f"Polygon quote lookup failed for {symbol}.") from exc
        return self.normalize_quote(symbol, raw_quote, raw_trade)

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        self._ensure_configured()
        start_utc, end_utc = ensure_time_range(start, end)
        multiplier, timespan = polygon_timeframe(timeframe)
        try:
            raw = self.http_client.request_json(
                "GET",
                f"{self.base_url}/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/"
                f"{start_utc.date().isoformat()}/{end_utc.date().isoformat()}",
                params={
                    "adjusted": "true",
                    "sort": "asc",
                    "limit": 5000,
                    "apiKey": self.api_key,
                },
            )
        except HttpRequestError as exc:
            raise ProviderError(f"Polygon history lookup failed for {symbol}.") from exc
        return self.normalize_candles(symbol, raw)

    def check_health(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(
                provider_name=self.name,
                available=False,
                detail="Polygon is selected but POLYGON_API_KEY is missing.",
            )
        return ProviderStatus(
            provider_name=self.name,
            available=True,
            detail="Polygon is configured. Live connectivity is checked when requests run.",
        )

    def normalize_quote(
        self,
        symbol: str,
        raw_quote: dict[str, object],
        raw_trade: dict[str, object] | None = None,
    ) -> Quote:
        results = raw_quote.get("results")
        if not isinstance(results, dict):
            results = {}
        trade_payload = raw_trade or {}
        trade_results = trade_payload.get("results")
        if not isinstance(trade_results, dict):
            trade_results = {}
            
        if not results:
            raise ProviderError(f"Polygon returned no quote data for {symbol}.")

        bid_price = float(results.get("p", results.get("bp", 0.0)))
        ask_price = float(results.get("P", results.get("ap", 0.0)))
        if bid_price and ask_price and bid_price > ask_price:
            bid_price, ask_price = ask_price, bid_price

        trade_price = trade_results.get("p", results.get("last", ask_price or bid_price or 0.0))
        timestamp_ns = int(
            trade_results.get("t", results.get("t", int(datetime.now(timezone.utc).timestamp() * 1_000_000_000)))
        )
        return Quote(
            symbol=symbol,
            bid=bid_price,
            ask=ask_price,
            last=float(trade_price),
            volume=int(trade_results.get("s", 0)),
            source=self.name,
            timestamp=datetime.fromtimestamp(timestamp_ns / 1_000_000_000, tz=timezone.utc),
        )

    def normalize_candles(self, symbol: str, raw: dict[str, object]) -> list[Candle]:
        candles: list[Candle] = []
        items = raw.get("results", [])
        if not isinstance(items, list):
            items = []
        for item in items:
            if not isinstance(item, dict):
                continue
            candles.append(
                Candle(
                    symbol=symbol,
                    open=float(item["o"]),
                    high=float(item["h"]),
                    low=float(item["l"]),
                    close=float(item["c"]),
                    volume=int(item.get("v", 0)),
                    source=self.name,
                    timestamp=datetime.fromtimestamp(int(item["t"]) / 1000, tz=timezone.utc),
                )
            )
        return candles

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise ProviderUnavailableError("Polygon requires POLYGON_API_KEY.")
