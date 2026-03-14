from __future__ import annotations

import base64

from auto_stock.domain.notifications import (
    NotificationChannelKind,
    NotificationChannelStatus,
    NotificationDeliveryResult,
)
from auto_stock.infra.errors import ConfigurationError
from auto_stock.notifications.base import NotificationChannel
from auto_stock.notifications.transport import NotificationTransport


def _mask_destination(value: str | None) -> str:
    if not value:
        return "not set"
    trimmed = value.replace("whatsapp:", "")
    if len(trimmed) <= 4:
        return trimmed
    return f"...{trimmed[-4:]}"


class _TwilioMessageChannel(NotificationChannel):
    channel_kind = NotificationChannelKind.SMS

    def __init__(
        self,
        *,
        name: str,
        account_sid: str | None,
        auth_token: str | None,
        from_number: str | None,
        to_number: str | None,
        base_url: str,
        transport: NotificationTransport,
    ) -> None:
        self.name = name
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number
        self.base_url = base_url.rstrip("/")
        self.transport = transport

    def get_status(self) -> NotificationChannelStatus:
        missing = self._missing_fields()
        if missing:
            missing_text = ", ".join(missing)
            return NotificationChannelStatus(
                name=self.name,
                kind=self.channel_kind,
                configured=False,
                detail=f"Missing {missing_text}.",
            )
        return NotificationChannelStatus(
            name=self.name,
            kind=self.channel_kind,
            configured=True,
            detail=f"Configured for {_mask_destination(self.to_number)}.",
        )

    def send(self, message: str) -> NotificationDeliveryResult:
        missing = self._missing_fields()
        if missing:
            missing_text = ", ".join(missing)
            raise ConfigurationError(f"{self.name.title()} notifications are not configured. Missing {missing_text}.")
        self.transport.post_form(
            self._messages_url(),
            {
                "To": self._normalized_to(),
                "From": self._normalized_from(),
                "Body": message,
            },
            headers={"Authorization": self._authorization_header()},
        )
        return NotificationDeliveryResult(channel_name=self.name, success=True, detail=f"{self.name.title()} message sent.")

    def _messages_url(self) -> str:
        return f"{self.base_url}/2010-04-01/Accounts/{self.account_sid}/Messages.json"

    def _authorization_header(self) -> str:
        raw = f"{self.account_sid}:{self.auth_token}".encode("utf-8")
        return f"Basic {base64.b64encode(raw).decode('ascii')}"

    def _normalized_from(self) -> str:
        return self.from_number or ""

    def _normalized_to(self) -> str:
        return self.to_number or ""

    def _missing_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not self.auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not self.from_number:
            missing.append(self._from_env_name())
        if not self.to_number:
            missing.append(self._to_env_name())
        return missing

    def _from_env_name(self) -> str:
        raise NotImplementedError

    def _to_env_name(self) -> str:
        raise NotImplementedError


class TwilioSmsChannel(_TwilioMessageChannel):
    channel_kind = NotificationChannelKind.SMS

    def __init__(
        self,
        *,
        account_sid: str | None,
        auth_token: str | None,
        from_number: str | None,
        to_number: str | None,
        base_url: str,
        transport: NotificationTransport,
    ) -> None:
        super().__init__(
            name="twilio-sms",
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
            to_number=to_number,
            base_url=base_url,
            transport=transport,
        )

    def _from_env_name(self) -> str:
        return "TWILIO_SMS_FROM"

    def _to_env_name(self) -> str:
        return "TWILIO_SMS_TO"


class TwilioWhatsAppChannel(_TwilioMessageChannel):
    channel_kind = NotificationChannelKind.WHATSAPP

    def __init__(
        self,
        *,
        account_sid: str | None,
        auth_token: str | None,
        from_number: str | None,
        to_number: str | None,
        base_url: str,
        transport: NotificationTransport,
    ) -> None:
        super().__init__(
            name="twilio-whatsapp",
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
            to_number=to_number,
            base_url=base_url,
            transport=transport,
        )

    def _normalized_from(self) -> str:
        return _normalize_whatsapp_number(self.from_number)

    def _normalized_to(self) -> str:
        return _normalize_whatsapp_number(self.to_number)

    def _from_env_name(self) -> str:
        return "TWILIO_WHATSAPP_FROM"

    def _to_env_name(self) -> str:
        return "TWILIO_WHATSAPP_TO"


def _normalize_whatsapp_number(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip()
    if normalized.lower().startswith("whatsapp:"):
        return normalized
    return f"whatsapp:{normalized}"
