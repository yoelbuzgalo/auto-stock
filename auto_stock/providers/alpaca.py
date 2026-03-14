from __future__ import annotations

from datetime import datetime, timezone

from auto_stock.domain.market import Candle, ProviderStatus, Quote
from auto_stock.infra.errors import HttpRequestError, ProviderError, ProviderUnavailableError
from auto_stock.infra.http import HttpClient
from auto_stock.infra.validation import ensure_time_range, normalize_timeframe
from auto_stock.providers.base import MarketDataProvider

_ALPACA_TIMEFRAMES = {
    "1Min": "1Min",
    "5Min": "5Min",
    "15Min": "15Min",
    "1Hour": "1Hour",
    "1Day": "1Day",
}


class AlpacaDataSource(MarketDataProvider):
    name = "alpaca"

    def __init__(
        self,
        api_key: str | None,
        api_secret: str | None,
        base_url: str,
        http_client: HttpClient,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    def get_quote(self, symbol: str) -> Quote:
        self._ensure_configured()
        try:
            raw = self.http_client.request_json(
                "GET",
                f"{self.base_url}/v2/stocks/{symbol}/snapshot",
                headers=self._headers(),
            )
        except HttpRequestError as exc:
            raise ProviderError(f"Alpaca quote lookup failed for {symbol}.") from exc
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
        try:
            raw = self.http_client.request_json(
                "GET",
                f"{self.base_url}/v2/stocks/{symbol}/bars",
                headers=self._headers(),
                params={
                    "timeframe": _ALPACA_TIMEFRAMES[normalize_timeframe(timeframe)],
                    "start": start_utc.isoformat(),
                    "end": end_utc.isoformat(),
                    "limit": 1000,
                    "feed": "iex",
                },
            )
        except HttpRequestError as exc:
            raise ProviderError(f"Alpaca history lookup failed for {symbol}.") from exc
        return self.normalize_candles(symbol, raw)

    def check_health(self) -> ProviderStatus:
        if not self.api_key or not self.api_secret:
            return ProviderStatus(
                provider_name=self.name,
                available=False,
                detail="Alpaca is selected but ALPACA_API_KEY or ALPACA_API_SECRET is missing.",
            )
        return ProviderStatus(
            provider_name=self.name,
            available=True,
            detail="Alpaca is configured. Requests use Market Data v2 endpoints.",
        )

    def normalize_quote(self, symbol: str, raw: dict[str, object]) -> Quote:
        latest_quote = raw.get("latestQuote")
        if not isinstance(latest_quote, dict): latest_quote = raw.get("quote")
        if not isinstance(latest_quote, dict): latest_quote = {}

        latest_trade = raw.get("latestTrade")
        if not isinstance(latest_trade, dict): latest_trade = raw.get("trade")
        if not isinstance(latest_trade, dict): latest_trade = {}

        minute_bar = raw.get("minuteBar")
        if not isinstance(minute_bar, dict): minute_bar = {}

        if not latest_quote:
            raise ProviderError(f"Alpaca returned no quote data for {symbol}.")

        timestamp_text = str(
            latest_quote.get("t")
            or latest_trade.get("t")
            or datetime.now(timezone.utc).isoformat()
        )
        return Quote(
            symbol=symbol,
            bid=float(str(latest_quote.get("bp", 0.0))),
            ask=float(str(latest_quote.get("ap", 0.0))),
            last=float(str(latest_trade.get("p", minute_bar.get("c", latest_quote.get("ap", 0.0))))),
            volume=int(str(minute_bar.get("v", latest_trade.get("s", 0)))),
            source=self.name,
            timestamp=datetime.fromisoformat(timestamp_text.replace("Z", "+00:00")),
        )

    def normalize_candles(self, symbol: str, raw: dict[str, object]) -> list[Candle]:
        candles: list[Candle] = []
        bars = raw.get("bars", [])
        if not isinstance(bars, list):
            bars = []
        for item in bars:
            if not isinstance(item, dict):
                continue
            if not {"o", "h", "l", "c", "t"}.issubset(item):
                continue
            candles.append(
                Candle(
                    symbol=symbol,
                    open=float(str(item["o"])),
                    high=float(str(item["h"])),
                    low=float(str(item["l"])),
                    close=float(str(item["c"])),
                    volume=int(str(item.get("v", 0))),
                    source=self.name,
                    timestamp=datetime.fromisoformat(str(item["t"]).replace("Z", "+00:00")),
                )
            )
        return candles

    def _headers(self) -> dict[str, str]:
        return {
            "APCA-API-KEY-ID": self.api_key or "",
            "APCA-API-SECRET-KEY": self.api_secret or "",
        }

    def _ensure_configured(self) -> None:
        if not self.api_key or not self.api_secret:
            raise ProviderUnavailableError("Alpaca requires ALPACA_API_KEY and ALPACA_API_SECRET.")
