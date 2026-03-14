from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from auto_stock.bootstrap import build_app_services
from auto_stock.infra.config import AppConfig
from auto_stock.notifications.discord import DiscordWebhookChannel
from auto_stock.notifications.transport import NotificationResponse, NotificationTransport
from auto_stock.notifications.twilio import TwilioSmsChannel, TwilioWhatsAppChannel
from auto_stock.services.notifications import NotificationService
from auto_stock.ui.cli import run_cli
from tests.helpers import workspace_temp_dir


class FakeNotificationTransport(NotificationTransport):
    def __init__(self) -> None:
        self.json_calls: list[tuple[str, dict[str, object], dict[str, str] | None]] = []
        self.form_calls: list[tuple[str, dict[str, object], dict[str, str] | None]] = []

    def post_json(
        self,
        url: str,
        payload: dict[str, object],
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> NotificationResponse:
        self.json_calls.append((url, payload, headers))
        return NotificationResponse(status_code=204, body="")

    def post_form(
        self,
        url: str,
        payload: dict[str, object],
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> NotificationResponse:
        self.form_calls.append((url, payload, headers))
        return NotificationResponse(status_code=201, body="{}")


class NotificationTests(unittest.TestCase):
    def test_discord_status_reports_missing_webhook(self) -> None:
        channel = DiscordWebhookChannel(None, FakeNotificationTransport())

        status = channel.get_status()

        self.assertFalse(status.configured)
        self.assertIn("DISCORD_WEBHOOK_URL", status.detail)

    def test_whatsapp_channel_normalizes_numbers_for_twilio(self) -> None:
        transport = FakeNotificationTransport()
        channel = TwilioWhatsAppChannel(
            account_sid="sid",
            auth_token="token",
            from_number="+15550001111",
            to_number="+15550002222",
            base_url="https://api.twilio.com",
            transport=transport,
        )

        result = channel.send("hello")

        self.assertTrue(result.success)
        self.assertEqual(len(transport.form_calls), 1)
        _, payload, headers = transport.form_calls[0]
        self.assertEqual(payload["From"], "whatsapp:+15550001111")
        self.assertEqual(payload["To"], "whatsapp:+15550002222")
        self.assertIn("Authorization", headers or {})

    def test_notification_service_send_all_skips_unconfigured_channels(self) -> None:
        transport = FakeNotificationTransport()
        service = NotificationService(
            [
                DiscordWebhookChannel("https://discord.example/webhook", transport),
                TwilioSmsChannel(
                    account_sid="sid",
                    auth_token="token",
                    from_number="+15550001111",
                    to_number="+15550002222",
                    base_url="https://api.twilio.com",
                    transport=transport,
                ),
                TwilioWhatsAppChannel(
                    account_sid=None,
                    auth_token=None,
                    from_number=None,
                    to_number=None,
                    base_url="https://api.twilio.com",
                    transport=transport,
                ),
            ]
        )

        results = service.send_all("market update")

        self.assertEqual(len(results), 2)
        self.assertEqual(len(transport.json_calls), 1)
        self.assertEqual(len(transport.form_calls), 1)

    def test_notify_status_command_lists_channels(self) -> None:
        with workspace_temp_dir() as temp_dir:
            config = AppConfig.from_env(
                env={
                    "AUTO_STOCK_STORAGE_DIR": str(temp_dir),
                    "AUTO_STOCK_STATE_FILE": str(temp_dir / "state.json"),
                    "AUTO_STOCK_LOG_FILE": str(temp_dir / "auto_stock.log"),
                }
            )
            services = build_app_services(config)
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_cli(services, ["notify", "status"])

        self.assertEqual(exit_code, 0)
        self.assertIn("discord", output.getvalue())
        self.assertIn("twilio-whatsapp", output.getvalue())

    def test_notify_send_all_returns_error_when_nothing_is_configured(self) -> None:
        with workspace_temp_dir() as temp_dir:
            config = AppConfig.from_env(
                env={
                    "AUTO_STOCK_STORAGE_DIR": str(temp_dir),
                    "AUTO_STOCK_STATE_FILE": str(temp_dir / "state.json"),
                    "AUTO_STOCK_LOG_FILE": str(temp_dir / "auto_stock.log"),
                }
            )
            services = build_app_services(config)
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_cli(services, ["notify", "send", "--all", "hello"])

        self.assertEqual(exit_code, 1)
        self.assertIn("No configured notification channels", output.getvalue())


if __name__ == "__main__":
    unittest.main()
