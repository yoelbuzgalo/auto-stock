from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from auto_stock.domain.market import Candle
from auto_stock.services.indicators import exponential_moving_average, relative_strength_index, simple_moving_average


class IndicatorTests(unittest.TestCase):
    def _build_candles(self, closes: list[float]) -> list[Candle]:
        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return [
            Candle(
                symbol="AAPL",
                open=close,
                high=close + 1.0,
                low=close - 1.0,
                close=close,
                volume=1000 + index,
                source="demo",
                timestamp=base_time + timedelta(days=index),
            )
            for index, close in enumerate(closes, start=1)
        ]

    def test_simple_moving_average_returns_expected_values(self) -> None:
        candles = self._build_candles([1, 2, 3, 4, 5])

        values = simple_moving_average(candles, 3)

        self.assertEqual(values[:2], [None, None])
        self.assertEqual(values[2:], [2.0, 3.0, 4.0])

    def test_exponential_moving_average_uses_standard_seed_and_multiplier(self) -> None:
        candles = self._build_candles([1, 2, 3, 4, 5])

        values = exponential_moving_average(candles, 3)

        self.assertEqual(values[:2], [None, None])
        self.assertEqual(values[2:], [2.0, 3.0, 4.0])

    def test_relative_strength_index_uses_wilder_smoothing(self) -> None:
        candles = self._build_candles([1, 2, 3, 2, 2, 4])

        values = relative_strength_index(candles, 3)

        self.assertEqual(values[:3], [None, None, None])
        self.assertAlmostEqual(values[3] or 0.0, 66.6666666667, places=6)
        self.assertAlmostEqual(values[4] or 0.0, 66.6666666667, places=6)
        self.assertAlmostEqual(values[5] or 0.0, 86.6666666667, places=6)

    def test_relative_strength_index_returns_neutral_value_for_flat_market(self) -> None:
        candles = self._build_candles([10] * 16)

        values = relative_strength_index(candles, 14)

        self.assertEqual(values[:14], [None] * 14)
        self.assertEqual(values[14], 50.0)
        self.assertEqual(values[15], 50.0)


if __name__ == "__main__":
    unittest.main()
