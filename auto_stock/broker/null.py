from __future__ import annotations

from auto_stock.broker.base import BrokerClient
from auto_stock.domain.broker import Account, BrokerSnapshot, BrokerStatus, Order, Position
from auto_stock.infra.errors import BrokerError


class NullBrokerClient(BrokerClient):
    name = "none"

    def authenticate(self) -> None:
        raise BrokerError("No broker is configured.")

    def refresh_access_token(self) -> None:
        raise BrokerError("No broker is configured.")

    def check_health(self) -> BrokerStatus:
        return BrokerStatus(
            broker_name=self.name,
            available=False,
            detail="No live broker is configured. Local watchlists and order plans still work.",
        )

    def get_account(self, account_id: str) -> Account:
        raise BrokerError("No broker is configured.")

    def get_positions(self, account_id: str) -> list[Position]:
        raise BrokerError("No broker is configured.")

    def get_orders(self, account_id: str) -> list[Order]:
        raise BrokerError("No broker is configured.")

    def get_snapshot(self, account_id: str) -> BrokerSnapshot:
        raise BrokerError("No broker is configured.")

    def place_order(self, account_id: str, order: Order) -> Order:
        raise BrokerError("No broker is configured.")

    def cancel_order(self, account_id: str, order_id: str) -> bool:
        raise BrokerError("No broker is configured.")
