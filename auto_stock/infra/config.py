from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _get(env: dict[str, str], key: str, default: str) -> str:
    value = env.get(key)
    if not value:
        return default
    return value


def _get_optional(env: dict[str, str], key: str) -> str | None:
    value = env.get(key)
    return str(value) if value not in (None, "") else None


def _get_int(env: dict[str, str], key: str, default: int) -> int:
    try:
        return int(_get(env, key, str(default)))
    except ValueError:
        return default


def _get_float(env: dict[str, str], key: str, default: float) -> float:
    try:
        return float(_get(env, key, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True, slots=True)
class StorageConfig:
    root_dir: Path
    state_file: Path
    log_file: Path


@dataclass(frozen=True, slots=True)
class MarketDataConfig:
    provider_name: str
    timeout_seconds: float
    cache_ttl_seconds: int
    retry_attempts: int
    demo_seed: int
    polygon_api_key: str | None
    polygon_base_url: str
    alpaca_api_key: str | None
    alpaca_api_secret: str | None
    alpaca_base_url: str
    schwab_access_token: str | None
    schwab_base_url: str


@dataclass(frozen=True, slots=True)
class BrokerConfig:
    provider_name: str
    account_id: str | None
    schwab_client_id: str | None
    schwab_client_secret: str | None
    schwab_redirect_uri: str
    schwab_access_token: str | None
    schwab_refresh_token: str | None
    schwab_base_url: str


@dataclass(frozen=True, slots=True)
class NotificationConfig:
    discord_webhook_url: str | None
    twilio_account_sid: str | None
    twilio_auth_token: str | None
    twilio_base_url: str
    twilio_sms_from: str | None
    twilio_sms_to: str | None
    twilio_whatsapp_from: str | None
    twilio_whatsapp_to: str | None


@dataclass(frozen=True, slots=True)
class AppConfig:
    storage: StorageConfig
    market_data: MarketDataConfig
    broker: BrokerConfig
    notifications: NotificationConfig
    logging_level: str = "INFO"

    @classmethod
    def from_env(
        cls,
        env: dict[str, str] | None = None,
        env_file: Path | None = None,
    ) -> "AppConfig":
        merged = _load_env_file(env_file or Path(".env"))
        merged.update(os.environ)
        if env:
            merged.update(env)

        storage_root = Path(_get(merged, "AUTO_STOCK_STORAGE_DIR", ".auto_stock"))
        storage = StorageConfig(
            root_dir=storage_root,
            state_file=Path(_get(merged, "AUTO_STOCK_STATE_FILE", str(storage_root / "state.json"))),
            log_file=Path(_get(merged, "AUTO_STOCK_LOG_FILE", str(storage_root / "auto_stock.log"))),
        )
        market_data = MarketDataConfig(
            provider_name=_get(merged, "AUTO_STOCK_PROVIDER", "demo"),
            timeout_seconds=_get_float(merged, "AUTO_STOCK_HTTP_TIMEOUT", 8.0),
            cache_ttl_seconds=_get_int(merged, "AUTO_STOCK_CACHE_TTL_SECONDS", 15),
            retry_attempts=_get_int(merged, "AUTO_STOCK_RETRY_ATTEMPTS", 2),
            demo_seed=_get_int(merged, "AUTO_STOCK_DEMO_SEED", 7),
            polygon_api_key=_get_optional(merged, "POLYGON_API_KEY"),
            polygon_base_url=_get(merged, "POLYGON_BASE_URL", "https://api.polygon.io"),
            alpaca_api_key=_get_optional(merged, "ALPACA_API_KEY"),
            alpaca_api_secret=_get_optional(merged, "ALPACA_API_SECRET"),
            alpaca_base_url=_get(merged, "ALPACA_BASE_URL", "https://data.alpaca.markets"),
            schwab_access_token=_get_optional(merged, "SCHWAB_ACCESS_TOKEN"),
            schwab_base_url=_get(merged, "SCHWAB_BASE_URL", "https://api.schwabapi.com"),
        )
        broker = BrokerConfig(
            provider_name=_get(merged, "AUTO_STOCK_BROKER", "none"),
            account_id=_get_optional(merged, "SCHWAB_ACCOUNT_ID"),
            schwab_client_id=_get_optional(merged, "SCHWAB_CLIENT_ID"),
            schwab_client_secret=_get_optional(merged, "SCHWAB_CLIENT_SECRET"),
            schwab_redirect_uri=_get(merged, "SCHWAB_REDIRECT_URI", "https://127.0.0.1"),
            schwab_access_token=_get_optional(merged, "SCHWAB_ACCESS_TOKEN"),
            schwab_refresh_token=_get_optional(merged, "SCHWAB_REFRESH_TOKEN"),
            schwab_base_url=_get(merged, "SCHWAB_BASE_URL", "https://api.schwabapi.com"),
        )
        notifications = NotificationConfig(
            discord_webhook_url=_get_optional(merged, "DISCORD_WEBHOOK_URL"),
            twilio_account_sid=_get_optional(merged, "TWILIO_ACCOUNT_SID"),
            twilio_auth_token=_get_optional(merged, "TWILIO_AUTH_TOKEN"),
            twilio_base_url=_get(merged, "TWILIO_BASE_URL", "https://api.twilio.com"),
            twilio_sms_from=_get_optional(merged, "TWILIO_SMS_FROM"),
            twilio_sms_to=_get_optional(merged, "TWILIO_SMS_TO"),
            twilio_whatsapp_from=_get_optional(merged, "TWILIO_WHATSAPP_FROM"),
            twilio_whatsapp_to=_get_optional(merged, "TWILIO_WHATSAPP_TO"),
        )
        return cls(
            storage=storage,
            market_data=market_data,
            broker=broker,
            notifications=notifications,
            logging_level=_get(merged, "AUTO_STOCK_LOG_LEVEL", "INFO").upper(),
        )
