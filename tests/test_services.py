from __future__ import annotations

import unittest
from pathlib import Path

from auto_stock.broker.null import NullBrokerClient
from auto_stock.infra.errors import ValidationError
from auto_stock.persistence.state import JsonStateRepository
from auto_stock.providers.demo import DemoMarketDataProvider
from auto_stock.services.broker import BrokerService
from auto_stock.services.market import MarketService
from auto_stock.services.orders import OrderPlanService
from auto_stock.services.watchlist import WatchlistService
from tests.helpers import workspace_temp_dir


class ServicesTests(unittest.TestCase):
    def test_watchlist_service_prevents_duplicates(self) -> None:
        with workspace_temp_dir() as temp_dir:
            repository = JsonStateRepository(temp_dir / "state.json")
            service = WatchlistService(repository)
            service.add_item("AAPL")
            with self.assertRaises(ValidationError):
                service.add_item("aapl")

    def test_order_service_validates_side(self) -> None:
        with workspace_temp_dir() as temp_dir:
            repository = JsonStateRepository(temp_dir / "state.json")
            service = OrderPlanService(repository)
            with self.assertRaises(ValidationError):
                service.add_order("AAPL", side="HOLD")

    def test_market_service_uses_demo_provider(self) -> None:
        service = MarketService(DemoMarketDataProvider(seed=3))
        quote = service.get_quote("NVDA")
        history = service.get_history("NVDA", timeframe="1Day")
        self.assertEqual(quote.symbol, "NVDA")
        self.assertTrue(history)

    def test_broker_service_requires_account(self) -> None:
        service = BrokerService(NullBrokerClient())
        with self.assertRaises(ValidationError):
            service.get_snapshot()


if __name__ == "__main__":
    unittest.main()
