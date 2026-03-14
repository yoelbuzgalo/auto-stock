from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NotificationChannelKind(StrEnum):
    DISCORD = "discord"
    SMS = "sms"
    WHATSAPP = "whatsapp"


@dataclass(frozen=True, slots=True)
class NotificationChannelStatus:
    name: str
    kind: NotificationChannelKind
    configured: bool
    detail: str


@dataclass(frozen=True, slots=True)
class NotificationDeliveryResult:
    channel_name: str
    success: bool
    detail: str

