from __future__ import annotations

import logging
from dataclasses import dataclass

from auto_stock.broker.base import BrokerClient
from auto_stock.broker.null import NullBrokerClient
from auto_stock.broker.schwab import SchwabClient
from auto_stock.infra.config import AppConfig
from auto_stock.infra.http import UrllibHttpClient
from auto_stock.infra.logging import configure_logging
from auto_stock.notifications.base import NotificationChannel
from auto_stock.notifications.discord import DiscordWebhookChannel
from auto_stock.notifications.transport import UrllibNotificationTransport
from auto_stock.notifications.twilio import TwilioSmsChannel, TwilioWhatsAppChannel
from auto_stock.persistence.state import JsonStateRepository
from auto_stock.providers.alpaca import AlpacaDataSource
from auto_stock.providers.base import MarketDataProvider
from auto_stock.providers.demo import DemoMarketDataProvider
from auto_stock.providers.polygon import PolygonDataSource
from auto_stock.providers.schwab import SchwabDataSource
from auto_stock.providers.wrappers import CachingMarketDataProvider, RetryingMarketDataProvider
from auto_stock.services.broker import BrokerService
from auto_stock.services.health import HealthService
from auto_stock.services.market import MarketService
from auto_stock.services.notifications import NotificationService
from auto_stock.services.orders import OrderPlanService
from auto_stock.services.watchlist import WatchlistService


@dataclass(slots=True)
class AppServices:
    config: AppConfig
    market: MarketService
    watchlist: WatchlistService
    order_plans: OrderPlanService
    broker: BrokerService
    notifications: NotificationService
    health: HealthService


def build_app_services(config: AppConfig | None = None) -> AppServices:
    resolved_config = config or AppConfig.from_env()
    configure_logging(
        level=resolved_config.logging_level,
        log_file=resolved_config.storage.log_file,
    )

    http_client = UrllibHttpClient(
        default_timeout_seconds=resolved_config.market_data.timeout_seconds,
        user_agent="auto-stock/0.1.0",
    )
    provider = _build_provider(resolved_config, http_client)
    broker = _build_broker(resolved_config, http_client)
    notifications = _build_notifications(resolved_config)
    repository = JsonStateRepository(resolved_config.storage.state_file)

    market_service = MarketService(provider)
    watchlist_service = WatchlistService(repository)
    order_plan_service = OrderPlanService(repository)
    broker_service = BrokerService(broker, default_account_id=resolved_config.broker.account_id)
    notification_service = NotificationService(notifications)
    health_service = HealthService(
        provider=provider,
        broker=broker,
        repository=repository,
        storage_config=resolved_config.storage,
        notifications=notification_service,
    )

    logging.getLogger(__name__).info(
        "Auto Stock services built with provider=%s broker=%s",
        provider.name,
        broker.name,
    )
    return AppServices(
        config=resolved_config,
        market=market_service,
        watchlist=watchlist_service,
        order_plans=order_plan_service,
        broker=broker_service,
        notifications=notification_service,
        health=health_service,
    )


def _build_provider(config: AppConfig, http_client: UrllibHttpClient) -> MarketDataProvider:
    provider_name = config.market_data.provider_name.lower()
    if provider_name == "polygon":
        provider: MarketDataProvider = PolygonDataSource(
            api_key=config.market_data.polygon_api_key,
            base_url=config.market_data.polygon_base_url,
            http_client=http_client,
        )
    elif provider_name == "alpaca":
        provider = AlpacaDataSource(
            api_key=config.market_data.alpaca_api_key,
            api_secret=config.market_data.alpaca_api_secret,
            base_url=config.market_data.alpaca_base_url,
            http_client=http_client,
        )
    elif provider_name == "schwab":
        provider = SchwabDataSource(
            base_url=config.market_data.schwab_base_url,
            access_token=config.market_data.schwab_access_token,
            http_client=http_client,
        )
    else:
        provider = DemoMarketDataProvider(seed=config.market_data.demo_seed)

    if config.market_data.cache_ttl_seconds > 0:
        provider = CachingMarketDataProvider(provider, ttl_seconds=config.market_data.cache_ttl_seconds)
    if config.market_data.retry_attempts > 1:
        provider = RetryingMarketDataProvider(provider, max_attempts=config.market_data.retry_attempts)
    return provider


def _build_broker(config: AppConfig, http_client: UrllibHttpClient) -> BrokerClient:
    broker_name = config.broker.provider_name.lower()
    if broker_name == "schwab":
        return SchwabClient(
            client_id=config.broker.schwab_client_id,
            client_secret=config.broker.schwab_client_secret,
            redirect_uri=config.broker.schwab_redirect_uri,
            account_id=config.broker.account_id,
            access_token=config.broker.schwab_access_token,
            refresh_token=config.broker.schwab_refresh_token,
            base_url=config.broker.schwab_base_url,
            http_client=http_client,
        )
    return NullBrokerClient()


def _build_notifications(config: AppConfig) -> tuple[NotificationChannel, ...]:
    transport = UrllibNotificationTransport(user_agent="auto-stock/0.1.0")
    return (
        DiscordWebhookChannel(config.notifications.discord_webhook_url, transport),
        TwilioSmsChannel(
            account_sid=config.notifications.twilio_account_sid,
            auth_token=config.notifications.twilio_auth_token,
            from_number=config.notifications.twilio_sms_from,
            to_number=config.notifications.twilio_sms_to,
            base_url=config.notifications.twilio_base_url,
            transport=transport,
        ),
        TwilioWhatsAppChannel(
            account_sid=config.notifications.twilio_account_sid,
            auth_token=config.notifications.twilio_auth_token,
            from_number=config.notifications.twilio_whatsapp_from,
            to_number=config.notifications.twilio_whatsapp_to,
            base_url=config.notifications.twilio_base_url,
            transport=transport,
        ),
    )
