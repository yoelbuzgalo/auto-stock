from __future__ import annotations

from typing import List, Optional

from broker.base_client import BrokerClient
from broker.account_models import Account, Position
from broker.order_models import Order


class SchwabClient(BrokerClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token

    def authenticate(self) -> None:
        """
        Exchange credentials/code for access and refresh tokens.
        """
        raise NotImplementedError("Implement Schwab OAuth flow here.")

    def refresh_access_token(self) -> None:
        """
        Refresh the Schwab access token using the refresh token.
        """
        raise NotImplementedError("Implement token refresh here.")

    def get_account(self, account_id: str) -> Account:
        """
        Fetch account summary from Schwab and map into Account.
        """
        raise NotImplementedError("Implement get_account().")

    def get_positions(self, account_id: str) -> List[Position]:
        """
        Fetch positions for an account and map into Position objects.
        """
        raise NotImplementedError("Implement get_positions().")

    def get_orders(self, account_id: str) -> List[Order]:
        """
        Fetch orders for an account and map into Order objects.
        """
        raise NotImplementedError("Implement get_orders().")

    def place_order(self, account_id: str, order: Order) -> Order:
        """
        Submit an order to Schwab.
        """
        raise NotImplementedError("Implement place_order().")

    def cancel_order(self, account_id: str, order_id: str) -> bool:
        """
        Cancel an order by ID.
        """
        raise NotImplementedError("Implement cancel_order().")