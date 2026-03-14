from __future__ import annotations

import json
import unittest
from pathlib import Path

from auto_stock.domain.broker import OrderSide
from auto_stock.domain.watchlist import PlannedOrder, WatchlistItem
from auto_stock.persistence.state import AppState, JsonStateRepository
from tests.helpers import workspace_temp_dir


class PersistenceTests(unittest.TestCase):
    def test_repository_round_trips_state(self) -> None:
        with workspace_temp_dir() as temp_dir:
            path = temp_dir / "state.json"
            repository = JsonStateRepository(path)
            repository.save_state(
                AppState(
                    watchlist=(WatchlistItem(symbol="AAPL", note="Core"),),
                    planned_orders=(PlannedOrder(order_id="abc123", symbol="MSFT", side=OrderSide.BUY, quantity=2),),
                )
            )

            loaded = repository.load_state()
            self.assertEqual(len(loaded.watchlist), 1)
            self.assertEqual(len(loaded.planned_orders), 1)
            self.assertEqual(loaded.watchlist[0].symbol, "AAPL")
            self.assertEqual(loaded.planned_orders[0].symbol, "MSFT")

    def test_repository_skips_malformed_entries(self) -> None:
        with workspace_temp_dir() as temp_dir:
            path = temp_dir / "state.json"
            path.write_text(
                json.dumps(
                    {
                        "watchlist": [
                            {"symbol": "AAPL", "added_at": "2026-01-01T00:00:00+00:00"},
                            {"symbol": "$$$", "added_at": "2026-01-01T00:00:00+00:00"},
                        ],
                        "planned_orders": [
                            {
                                "order_id": "ok1",
                                "symbol": "MSFT",
                                "side": "BUY",
                                "quantity": 1,
                                "created_at": "2026-01-01T00:00:00+00:00",
                            },
                            {"order_id": "bad", "symbol": "MSFT", "side": "HOLD", "quantity": 1},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            repository = JsonStateRepository(path)

            loaded = repository.load_state()
            self.assertEqual([item.symbol for item in loaded.watchlist], ["AAPL"])
            self.assertEqual([order.order_id for order in loaded.planned_orders], ["ok1"])


if __name__ == "__main__":
    unittest.main()
