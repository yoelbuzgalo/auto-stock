from __future__ import annotations

import unittest
from datetime import datetime, timezone

from auto_stock.providers.alpaca import AlpacaDataSource
from auto_stock.domain.market import Quote, Candle

class _MockHttpClient:
    def check_health(self):
        return True

class AlpacaParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = AlpacaDataSource(
            http_client=_MockHttpClient(),  # type: ignore
            api_key="test",
            api_secret="test",
            base_url="https://test.com"
        )

    def test_normalize_quote_valid_data(self) -> None:
        raw_data = {
            "symbol": "AAPL",
            "quote": {"bp": 150.0, "ap": 150.5, "t": "2023-10-27T10:00:00Z"},
            "trade": {"p": 150.25, "s": 100, "t": "2023-10-27T10:00:00Z"},
            "minuteBar": {"c": 150.2, "v": 1000}
        }
        quote = self.provider.normalize_quote("AAPL", raw_data)
        self.assertEqual(quote.symbol, "AAPL")
        self.assertEqual(quote.bid, 150.0)
        self.assertEqual(quote.ask, 150.5)
        self.assertEqual(quote.last, 150.25)
        self.assertEqual(quote.volume, 1000)

    def test_normalize_quote_missing_trade_minutebar(self) -> None:
        raw_data = {
            "quote": {"bp": 100.0, "ap": 101.0, "t": "2023-10-27T10:00:00Z"},
        }
        quote = self.provider.normalize_quote("MSFT", raw_data)
        self.assertEqual(quote.symbol, "MSFT")
        self.assertEqual(quote.bid, 100.0)
        self.assertEqual(quote.ask, 101.0)
        self.assertEqual(quote.last, 101.0) # Falls back to ask
        self.assertEqual(quote.volume, 0) # defaults to 0

    def test_normalize_candles_valid_data(self) -> None:
        raw_data = {
            "bars": [
                {"o": 100.0, "h": 105.0, "l": 95.0, "c": 102.0, "v": 5000, "t": "2023-10-27T10:00:00Z"}
            ]
        }
        candles = self.provider.normalize_candles("TSLA", raw_data)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0].open, 100.0)
        self.assertEqual(candles[0].high, 105.0)
        self.assertEqual(candles[0].low, 95.0)
        self.assertEqual(candles[0].close, 102.0)
        self.assertEqual(candles[0].volume, 5000)
        self.assertEqual(candles[0].timestamp, datetime.fromisoformat("2023-10-27T10:00:00+00:00"))

    def test_normalize_candles_empty_data(self) -> None:
        self.assertEqual(self.provider.normalize_candles("TSLA", {}), [])
        self.assertEqual(self.provider.normalize_candles("TSLA", {"bars": None}), [])

if __name__ == "__main__":
    unittest.main()
