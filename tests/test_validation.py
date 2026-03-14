from __future__ import annotations

import unittest

from auto_stock.infra.errors import ValidationError
from auto_stock.infra.validation import normalize_symbol, normalize_timeframe


class ValidationTests(unittest.TestCase):
    def test_normalize_symbol_uppercases_valid_input(self) -> None:
        self.assertEqual(normalize_symbol(" brk.b "), "BRK.B")

    def test_normalize_symbol_rejects_invalid_input(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_symbol("$$$")

    def test_normalize_timeframe_accepts_aliases(self) -> None:
        self.assertEqual(normalize_timeframe("1d"), "1Day")


if __name__ == "__main__":
    unittest.main()
