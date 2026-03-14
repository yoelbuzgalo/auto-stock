from __future__ import annotations

from datetime import datetime, timezone

from auto_stock.domain.market import Candle, ProviderStatus, Quote
from auto_stock.infra.errors import HttpRequestError, ProviderError, ProviderUnavailableError
from auto_stock.infra.http import HttpClient
from auto_stock.infra.validation import ensure_time_range, normalize_timeframe
from auto_stock.providers.base import MarketDataProvider

_SCHWAB_TIMEFRAMES = {
    "1Min": ("minute", 1),
    "5Min": ("minute", 5),
    "15Min": ("minute", 15),
    "1Day": ("daily", 1),
}


class SchwabDataSource(MarketDataProvider):
    name = "schwab"

    def __init__(self, base_url: str, access_token: str | None, http_client: HttpClient) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.http_client = http_client

    def get_quote(self, symbol: str) -> Quote:
        self._ensure_configured()
        try:
            raw = self.http_client.request_json(
                "GET",
                f"{self.base_url}/marketdata/v1/quotes",
                headers=self._headers(),
                params={"symbols": symbol},
            )
        except HttpRequestError as exc:
            raise ProviderError(f"Schwab quote lookup failed for {symbol}.") from exc
        return self.normalize_quote(symbol, raw)

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        self._ensure_configured()
        start_utc, end_utc = ensure_time_range(start, end)
        normalized = normalize_timeframe(timeframe)
        if normalized not in _SCHWAB_TIMEFRAMES:
            raise ProviderError(f"Schwab does not currently support timeframe '{normalized}'.")
        frequency_type, frequency = _SCHWAB_TIMEFRAMES[normalized]
        try:
            raw = self.http_client.request_json(
                "GET",
                f"{self.base_url}/marketdata/v1/pricehistory",
                headers=self._headers(),
                params={
                    "symbol": symbol,
                    "startDate": int(start_utc.timestamp() * 1000),
                    "endDate": int(end_utc.timestamp() * 1000),
                    "frequencyType": frequency_type,
                    "frequency": frequency,
                    "needExtendedHoursData": "false",
                },
            )
        except HttpRequestError as exc:
            raise ProviderError(f"Schwab history lookup failed for {symbol}.") from exc
        return self.normalize_candles(symbol, raw)

    def check_health(self) -> ProviderStatus:
        if not self.access_token:
            return ProviderStatus(
                provider_name=self.name,
                available=False,
                detail="Schwab market data is selected but SCHWAB_ACCESS_TOKEN is missing.",
            )
        return ProviderStatus(
            provider_name=self.name,
            available=True,
            detail="Schwab market data is configured with a bearer token.",
        )

    def normalize_quote(self, symbol: str, raw: dict[str, object]) -> Quote:
        symbol_entry = raw.get(symbol) if isinstance(raw, dict) else None
        if not symbol_entry and isinstance(raw, dict) and raw:
            symbol_entry = next(iter(raw.values()))
            
        quote_entry: dict[str, object] = {}
        if isinstance(symbol_entry, dict):
            qe = symbol_entry.get("quote")
            if isinstance(qe, dict):
                quote_entry = qe
            else:
                quote_entry = symbol_entry
                
        if not quote_entry:
            raise ProviderError(f"Schwab returned no quote data for {symbol}.")

        timestamp_ms = int(str(
            quote_entry.get("quoteTime")
            or quote_entry.get("tradeTime")
            or int(datetime.now(timezone.utc).timestamp() * 1000)
        ))
        return Quote(
            symbol=symbol,
            bid=float(str(quote_entry.get("bidPrice", 0.0))),
            ask=float(str(quote_entry.get("askPrice", 0.0))),
            last=float(str(quote_entry.get("lastPrice", quote_entry.get("mark", 0.0)))),
            volume=int(str(quote_entry.get("totalVolume", 0))),
            source=self.name,
            timestamp=datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc),
        )

    def normalize_candles(self, symbol: str, raw: dict[str, object]) -> list[Candle]:
        candles: list[Candle] = []
        items = raw.get("candles", [])
        if not isinstance(items, list):
            items = []
        for item in items:
            if not isinstance(item, dict):
                continue
            candles.append(
                Candle(
                    symbol=symbol,
                    open=float(str(item["open"])),
                    high=float(str(item["high"])),
                    low=float(str(item["low"])),
                    close=float(str(item["close"])),
                    volume=int(str(item.get("volume", 0))),
                    source=self.name,
                    timestamp=datetime.fromtimestamp(int(item["datetime"]) / 1000, tz=timezone.utc),
                )
            )
        return candles

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def _ensure_configured(self) -> None:
        if not self.access_token:
            raise ProviderUnavailableError("Schwab market data requires SCHWAB_ACCESS_TOKEN.")
