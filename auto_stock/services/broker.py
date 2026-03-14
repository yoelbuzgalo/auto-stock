from __future__ import annotations

from auto_stock.broker.base import BrokerClient
from auto_stock.domain.broker import BrokerSnapshot, BrokerStatus
from auto_stock.infra.errors import ValidationError


class BrokerService:
    def __init__(self, broker: BrokerClient, default_account_id: str | None = None) -> None:
        self.broker = broker
        self.default_account_id = default_account_id

    def get_status(self) -> BrokerStatus:
        return self.broker.check_health()

    def get_snapshot(self, account_id: str | None = None) -> BrokerSnapshot:
        broker_account_id = getattr(self.broker, "account_id", None)
        resolved_account_id = (account_id or self.default_account_id or broker_account_id or "").strip()
        if not resolved_account_id:
            raise ValidationError("An account ID is required to load broker data.")
        return self.broker.get_snapshot(resolved_account_id)
