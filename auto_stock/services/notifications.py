from __future__ import annotations

from collections.abc import Iterable

from auto_stock.domain.notifications import NotificationChannelStatus, NotificationDeliveryResult
from auto_stock.infra.errors import ValidationError
from auto_stock.infra.validation import normalize_optional_text
from auto_stock.notifications.base import NotificationChannel


class NotificationService:
    def __init__(self, channels: Iterable[NotificationChannel]) -> None:
        self._channels = tuple(channels)
        self._channel_map = {channel.name: channel for channel in self._channels}

    def list_statuses(self) -> tuple[NotificationChannelStatus, ...]:
        return tuple(channel.get_status() for channel in self._channels)

    def list_channel_names(self) -> tuple[str, ...]:
        return tuple(channel.name for channel in self._channels)

    def send(self, channel_name: str, message: str) -> NotificationDeliveryResult:
        normalized_name = normalize_optional_text(channel_name, max_length=60).lower()
        channel = self._channel_map.get(normalized_name)
        if channel is None:
            available = ", ".join(self.list_channel_names())
            raise ValidationError(f"Unknown notification channel '{channel_name}'. Available: {available}.")
        return channel.send(self._normalize_message(message))

    def send_all(self, message: str) -> tuple[NotificationDeliveryResult, ...]:
        normalized_message = self._normalize_message(message)
        results: list[NotificationDeliveryResult] = []
        for channel in self._channels:
            status = channel.get_status()
            if not status.configured:
                continue
            results.append(channel.send(normalized_message))
        return tuple(results)

    def _normalize_message(self, message: str) -> str:
        normalized = normalize_optional_text(message, max_length=1200)
        if not normalized:
            raise ValidationError("Notification message is required.")
        return normalized
