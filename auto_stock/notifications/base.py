from __future__ import annotations

from abc import ABC, abstractmethod

from auto_stock.domain.notifications import NotificationChannelStatus, NotificationDeliveryResult


class NotificationChannel(ABC):
    name = "notification"

    @abstractmethod
    def get_status(self) -> NotificationChannelStatus:
        raise NotImplementedError

    @abstractmethod
    def send(self, message: str) -> NotificationDeliveryResult:
        raise NotImplementedError
