from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from auto_stock.providers.demo import DemoMarketDataProvider


class DemoProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = DemoMarketDataProvider(seed=11)

    def test_quote_has_expected_shape(self) -> None:
        quote = self.provider.get_quote("AAPL")
        self.assertEqual(quote.symbol, "AAPL")
        self.assertGreater(quote.last, 0)
        self.assertGreaterEqual(quote.ask, quote.bid)

    def test_history_returns_candles(self) -> None:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=10)
        candles = self.provider.get_candles("MSFT", "1Day", start, end)
        self.assertTrue(candles)
        self.assertEqual(candles[0].symbol, "MSFT")
        self.assertLessEqual(len(candles), 180)


if __name__ == "__main__":
    unittest.main()
