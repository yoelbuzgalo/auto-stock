from __future__ import annotations

from abc import ABC, abstractmethod

from auto_stock.domain.broker import Account, BrokerSnapshot, BrokerStatus, Order, Position


class BrokerClient(ABC):
    name = "broker"

    @abstractmethod
    def authenticate(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh_access_token(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def check_health(self) -> BrokerStatus:
        raise NotImplementedError

    @abstractmethod
    def get_account(self, account_id: str) -> Account:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self, account_id: str) -> list[Position]:
        raise NotImplementedError

    @abstractmethod
    def get_orders(self, account_id: str) -> list[Order]:
        raise NotImplementedError

    @abstractmethod
    def get_snapshot(self, account_id: str) -> BrokerSnapshot:
        raise NotImplementedError

    @abstractmethod
    def place_order(self, account_id: str, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, account_id: str, order_id: str) -> bool:
        raise NotImplementedError
