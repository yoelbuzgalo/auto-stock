from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Final

from auto_stock.infra.errors import ValidationError

_SYMBOL_PATTERN: Final = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")
_TIMEFRAME_ALIASES: Final = {
    "1m": "1Min",
    "1min": "1Min",
    "5m": "5Min",
    "5min": "5Min",
    "15m": "15Min",
    "15min": "15Min",
    "1h": "1Hour",
    "60m": "1Hour",
    "1hour": "1Hour",
    "1d": "1Day",
    "day": "1Day",
    "1day": "1Day",
}
_TIMEFRAME_DELTAS: Final = {
    "1Min": timedelta(minutes=1),
    "5Min": timedelta(minutes=5),
    "15Min": timedelta(minutes=15),
    "1Hour": timedelta(hours=1),
    "1Day": timedelta(days=1),
}
_POLYGON_TIMEFRAMES: Final = {
    "1Min": (1, "minute"),
    "5Min": (5, "minute"),
    "15Min": (15, "minute"),
    "1Hour": (1, "hour"),
    "1Day": (1, "day"),
}


def normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValidationError("Ticker symbol is required.")
    if not _SYMBOL_PATTERN.fullmatch(normalized):
        raise ValidationError(
            "Ticker symbols must start with a letter and use only letters, digits, '.' or '-'."
        )
    return normalized


def normalize_optional_text(text: str | None, *, max_length: int = 180) -> str:
    if text is None:
        return ""
    normalized = text.strip()
    if len(normalized) > max_length:
        raise ValidationError(f"Text must be {max_length} characters or fewer.")
    return normalized


def ensure_positive_number(value: float | int | str, field_name: str, *, allow_zero: bool = False) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a number.") from exc
    if allow_zero and number < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    if not allow_zero and number <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
    return number


def normalize_timeframe(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValidationError("Timeframe is required.")
    canonical = _TIMEFRAME_ALIASES.get(normalized.lower(), normalized)
    if canonical not in _TIMEFRAME_DELTAS:
        supported = ", ".join(sorted(_TIMEFRAME_DELTAS))
        raise ValidationError(f"Unsupported timeframe '{value}'. Supported values: {supported}.")
    return canonical


def timeframe_delta(value: str) -> timedelta:
    return _TIMEFRAME_DELTAS[normalize_timeframe(value)]


def polygon_timeframe(value: str) -> tuple[int, str]:
    return _POLYGON_TIMEFRAMES[normalize_timeframe(value)]


def ensure_time_range(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    start_utc = as_utc(start)
    end_utc = as_utc(end)
    if start_utc >= end_utc:
        raise ValidationError("Start time must be before end time.")
    return start_utc, end_utc


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
