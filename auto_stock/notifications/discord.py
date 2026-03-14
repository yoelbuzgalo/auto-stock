from __future__ import annotations

from auto_stock.domain.notifications import (
    NotificationChannelKind,
    NotificationChannelStatus,
    NotificationDeliveryResult,
)
from auto_stock.infra.errors import ConfigurationError
from auto_stock.notifications.base import NotificationChannel
from auto_stock.notifications.transport import NotificationTransport


class DiscordWebhookChannel(NotificationChannel):
    name = "discord"

    def __init__(self, webhook_url: str | None, transport: NotificationTransport) -> None:
        self.webhook_url = webhook_url
        self.transport = transport

    def get_status(self) -> NotificationChannelStatus:
        if not self.webhook_url:
            return NotificationChannelStatus(
                name=self.name,
                kind=NotificationChannelKind.DISCORD,
                configured=False,
                detail="Set DISCORD_WEBHOOK_URL to enable Discord webhook delivery.",
            )
        return NotificationChannelStatus(
            name=self.name,
            kind=NotificationChannelKind.DISCORD,
            configured=True,
            detail="Discord webhook configured.",
        )

    def send(self, message: str) -> NotificationDeliveryResult:
        if not self.webhook_url:
            raise ConfigurationError("Discord notifications are not configured. Set DISCORD_WEBHOOK_URL.")
        self.transport.post_json(self.webhook_url, {"content": message})
        return NotificationDeliveryResult(channel_name=self.name, success=True, detail="Discord message sent.")
