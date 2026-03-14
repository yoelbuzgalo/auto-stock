from __future__ import annotations

import unittest
from datetime import datetime, timezone

from auto_stock.providers.schwab import SchwabDataSource
from auto_stock.domain.market import Quote, Candle

class _MockHttpClient:
    pass

class SchwabParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = SchwabDataSource(
            http_client=_MockHttpClient(),  # type: ignore
            access_token="test",
            base_url="https://test.com"
        )

    def test_normalize_quote_valid_data(self) -> None:
        raw_data = {
            "AAPL": {
                "quote": {"bidPrice": 150.0, "askPrice": 151.0, "lastPrice": 150.5, "totalVolume": 1000, "quoteTime": 1698400800000}
            }
        }
        quote = self.provider.normalize_quote("AAPL", raw_data)
        self.assertEqual(quote.symbol, "AAPL")
        self.assertEqual(quote.bid, 150.0)
        self.assertEqual(quote.ask, 151.0)
        self.assertEqual(quote.last, 150.5)
        self.assertEqual(quote.volume, 1000)
        self.assertEqual(quote.timestamp, datetime.fromtimestamp(1698400800, tz=timezone.utc))

    def test_normalize_quote_fallback_structure(self) -> None:
        raw_data = {
            "AAPL": {"bidPrice": 150.0, "askPrice": 151.0, "mark": 150.5, "totalVolume": 1000, "quoteTime": 1698400800000}
        }
        quote = self.provider.normalize_quote("AAPL", raw_data)
        self.assertEqual(quote.symbol, "AAPL")
        self.assertEqual(quote.bid, 150.0)
        self.assertEqual(quote.ask, 151.0)
        self.assertEqual(quote.last, 150.5)

    def test_normalize_candles_valid_data(self) -> None:
        raw_data = {
            "candles": [
                {"open": 10.0, "high": 15.0, "low": 9.0, "close": 12.0, "volume": 100, "datetime": 1698400800000}
            ]
        }
        candles = self.provider.normalize_candles("TSLA", raw_data)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0].open, 10.0)
        self.assertEqual(candles[0].close, 12.0)
        self.assertEqual(candles[0].timestamp, datetime.fromtimestamp(1698400800, tz=timezone.utc))

if __name__ == "__main__":
    unittest.main()
