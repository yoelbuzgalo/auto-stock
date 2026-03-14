from __future__ import annotations

import unittest
from datetime import datetime, timezone

from auto_stock.providers.polygon import PolygonDataSource
from auto_stock.domain.market import Quote, Candle

class _MockHttpClient:
    pass

class PolygonParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = PolygonDataSource(
            http_client=_MockHttpClient(),  # type: ignore
            api_key="test",
            base_url="https://test.com"
        )

    def test_normalize_quote_valid_data(self) -> None:
        raw_quote = {"results": {"p": 140.0, "P": 141.0}}
        raw_trade = {"results": {"p": 140.5, "s": 300, "t": 1698400800000000000}}
        quote = self.provider.normalize_quote("AAPL", raw_quote, raw_trade)
        self.assertEqual(quote.symbol, "AAPL")
        self.assertEqual(quote.bid, 140.0)
        self.assertEqual(quote.ask, 141.0)
        self.assertEqual(quote.last, 140.5)
        self.assertEqual(quote.volume, 300)

    def test_normalize_candles_valid_data(self) -> None:
        raw_data = {
            "results": [
                {"o": 10.0, "h": 15.0, "l": 9.0, "c": 12.0, "v": 100, "t": 1698400800000}
            ]
        }
        candles = self.provider.normalize_candles("TSLA", raw_data)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0].open, 10.0)
        self.assertEqual(candles[0].close, 12.0)
        self.assertEqual(candles[0].timestamp, datetime.fromtimestamp(1698400800, tz=timezone.utc))

if __name__ == "__main__":
    unittest.main()
