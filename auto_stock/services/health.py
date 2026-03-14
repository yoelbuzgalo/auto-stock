from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from auto_stock.broker.base import BrokerClient
from auto_stock.domain.broker import BrokerStatus
from auto_stock.domain.market import ProviderStatus
from auto_stock.domain.notifications import NotificationChannelStatus
from auto_stock.infra.config import StorageConfig
from auto_stock.persistence.state import StateRepository
from auto_stock.providers.base import MarketDataProvider
from auto_stock.services.notifications import NotificationService


@dataclass(frozen=True, slots=True)
class ApplicationStatus:
    provider: ProviderStatus
    broker: BrokerStatus
    notifications: tuple[NotificationChannelStatus, ...]
    storage_path: Path
    log_file: Path
    watchlist_count: int
    planned_order_count: int


class HealthService:
    def __init__(
        self,
        provider: MarketDataProvider,
        broker: BrokerClient,
        repository: StateRepository,
        storage_config: StorageConfig,
        notifications: NotificationService,
    ) -> None:
        self.provider = provider
        self.broker = broker
        self.repository = repository
        self.storage_config = storage_config
        self.notifications = notifications

    def get_status(self) -> ApplicationStatus:
        state = self.repository.load_state()
        return ApplicationStatus(
            provider=self.provider.check_health(),
            broker=self.broker.check_health(),
            notifications=self.notifications.list_statuses(),
            storage_path=self.storage_config.state_file,
            log_file=self.storage_config.log_file,
            watchlist_count=len(state.watchlist),
            planned_order_count=len(state.planned_orders),
        )
