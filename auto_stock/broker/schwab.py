from __future__ import annotations

import base64

from auto_stock.broker.base import BrokerClient
from auto_stock.domain.broker import (
    Account,
    BrokerSnapshot,
    BrokerStatus,
    Order,
    OrderLeg,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
)
from auto_stock.infra.errors import BrokerError, ConfigurationError, HttpRequestError
from auto_stock.infra.http import HttpClient


class SchwabClient(BrokerClient):
    name = "schwab"

    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        redirect_uri: str,
        account_id: str | None,
        access_token: str | None,
        refresh_token: str | None,
        base_url: str,
        http_client: HttpClient,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.account_id = account_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    def authenticate(self) -> None:
        if self.access_token:
            return
        self.refresh_access_token()

    def refresh_access_token(self) -> None:
        if not self.client_id or not self.client_secret or not self.refresh_token:
            raise ConfigurationError(
                "Schwab token refresh requires SCHWAB_CLIENT_ID, SCHWAB_CLIENT_SECRET, and SCHWAB_REFRESH_TOKEN."
            )

        credentials = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        authorization = base64.b64encode(credentials).decode("ascii")
        try:
            response = self.http_client.request_json(
                "POST",
                f"{self.base_url}/v1/oauth/token",
                headers={"Authorization": f"Basic {authorization}"},
                payload={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "redirect_uri": self.redirect_uri,
                },
            )
        except HttpRequestError as exc:
            raise BrokerError("Unable to refresh Schwab access token.") from exc
        token = response.get("access_token")
        if not token:
            raise BrokerError("Schwab token refresh did not return an access token.")
        self.access_token = str(token)

    def check_health(self) -> BrokerStatus:
        if not self.access_token and not self.refresh_token:
            return BrokerStatus(
                broker_name=self.name,
                available=False,
                detail="Schwab broker is not fully configured. Missing access or refresh token.",
            )
        if not self.account_id:
            return BrokerStatus(
                broker_name=self.name,
                available=True,
                detail="Schwab credentials are present. Set SCHWAB_ACCOUNT_ID to load account data in the GUI.",
            )
        return BrokerStatus(
            broker_name=self.name,
            available=True,
            detail="Schwab broker is configured.",
        )

    def get_account(self, account_id: str) -> Account:
        data = self._request_json(
            "GET",
            f"{self.base_url}/trader/v1/accounts/{account_id}",
            params={"fields": "positions"},
        )
        if not isinstance(data, dict):
            data = {}
        securities_account = data.get("securitiesAccount")
        if not isinstance(securities_account, dict):
            securities_account = data
            
        balances_obj = securities_account.get("currentBalances") or securities_account.get("initialBalances")
        balances = balances_obj if isinstance(balances_obj, dict) else {}
        
        return Account(
            account_id=str(securities_account.get("accountId", account_id)),
            account_type=str(securities_account.get("type", "UNKNOWN")),
            cash_balance=float(str(balances.get("cashBalance", balances.get("availableFunds", 0.0)))),
            buying_power=float(str(balances.get("buyingPower", 0.0))),
            equity=float(str(balances.get("equity", balances.get("liquidationValue", 0.0)))),
        )

    def get_positions(self, account_id: str) -> list[Position]:
        data = self._request_json(
            "GET",
            f"{self.base_url}/trader/v1/accounts/{account_id}",
            params={"fields": "positions"},
        )
        if not isinstance(data, dict):
            data = {}
        securities_account = data.get("securitiesAccount")
        if not isinstance(securities_account, dict):
            securities_account = data
            
        positions: list[Position] = []
        positions_list = securities_account.get("positions", [])
        if not isinstance(positions_list, list):
            positions_list = []
            
        for item in positions_list:
            if not isinstance(item, dict):
                continue
            instrument = item.get("instrument")
            if not isinstance(instrument, dict):
                instrument = {}
                
            quantity = float(str(item.get("longQuantity", 0.0))) - float(str(item.get("shortQuantity", 0.0)))
            positions.append(
                Position(
                    symbol=str(instrument.get("symbol", "UNKNOWN")),
                    quantity=quantity,
                    average_price=float(str(item.get("averagePrice", 0.0))),
                    market_value=float(str(item.get("marketValue", 0.0))),
                )
            )
        return positions

    def get_orders(self, account_id: str) -> list[Order]:
        data = self._request_json("GET", f"{self.base_url}/trader/v1/accounts/{account_id}/orders")
        if not isinstance(data, list):
            data = []
        return [self._normalize_order(item) for item in data if isinstance(item, dict)]

    def get_snapshot(self, account_id: str) -> BrokerSnapshot:
        return BrokerSnapshot(
            account=self.get_account(account_id),
            positions=tuple(self.get_positions(account_id)),
            orders=tuple(self.get_orders(account_id)),
        )

    def place_order(self, account_id: str, order: Order) -> Order:
        self._request_json(
            "POST",
            f"{self.base_url}/trader/v1/accounts/{account_id}/orders",
            payload=self._build_order_payload(order),
        )
        return order

    def cancel_order(self, account_id: str, order_id: str) -> bool:
        self._request_json("DELETE", f"{self.base_url}/trader/v1/accounts/{account_id}/orders/{order_id}")
        return True

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, object] | None = None,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object] | list[dict[str, object]]:
        if not self.access_token:
            self.authenticate()
        try:
            return self.http_client.request_json(
                method,
                url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                params=params,
                payload=payload,
            )
        except HttpRequestError as exc:
            raise BrokerError(f"Schwab request failed for {url}.") from exc

    def _normalize_order(self, raw: dict[str, object]) -> Order:
        raw_legs = raw.get("orderLegCollection", [])
        if not isinstance(raw_legs, list):
            raw_legs = []
        valid_legs = [leg for leg in raw_legs if isinstance(leg, dict)]
        
        legs = tuple(
            OrderLeg(
                symbol=str((leg.get("instrument") if isinstance(leg.get("instrument"), dict) else {}).get("symbol", "UNKNOWN")),
                instruction=str(leg.get("instruction", "BUY")),
                quantity=float(str(leg.get("quantity", raw.get("quantity", 0.0)))),
            )
            for leg in valid_legs
        )
        symbol = legs[0].symbol if legs else "UNKNOWN"
        first_instruction = str((valid_legs[0].get("instruction") if valid_legs else "BUY")).upper()
        side_value = first_instruction if first_instruction in OrderSide._value2member_map_ else OrderSide.BUY.value
        order_type_text = str(raw.get("orderType", "MARKET")).upper()
        order_type_value = order_type_text if order_type_text in OrderType._value2member_map_ else OrderType.MARKET.value
        status_text = str(raw.get("status", "UNKNOWN")).upper()
        status_value = status_text if status_text in OrderStatus._value2member_map_ else OrderStatus.UNKNOWN.value
        return Order(
            order_id=str(raw.get("orderId", "unknown")),
            symbol=symbol,
            side=OrderSide(side_value),
            order_type=OrderType(order_type_value),
            status=OrderStatus(status_value),
            quantity=float(str(raw.get("quantity", legs[0].quantity if legs else 0.0))),
            time_in_force=str(raw.get("duration", "DAY")),
            price=float(str(raw["price"])) if raw.get("price") is not None else None,
            legs=legs,
            source=self.name,
        )

    def _build_order_payload(self, order: Order) -> dict[str, object]:
        payload: dict[str, object] = {
            "orderType": order.order_type.value,
            "session": "NORMAL",
            "duration": order.time_in_force,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": order.side.value,
                    "quantity": order.quantity,
                    "instrument": {"symbol": order.symbol, "assetType": "EQUITY"},
                }
            ],
        }
        if order.price is not None:
            payload["price"] = order.price
        return payload
