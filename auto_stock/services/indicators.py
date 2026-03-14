from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from auto_stock.domain.market import Candle


@dataclass(frozen=True, slots=True)
class StandardIndicatorSet:
    sma_20: list[float | None]
    ema_12: list[float | None]
    ema_26: list[float | None]
    rsi_14: list[float | None]


def simple_moving_average(candles: Sequence[Candle], period: int) -> list[float | None]:
    _validate_period(period)

    values: list[float | None] = []
    running_total = 0.0
    closes = _extract_closes(candles)

    for index, close in enumerate(closes):
        running_total += close
        if index >= period:
            running_total -= closes[index - period]

        if index + 1 < period:
            values.append(None)
        else:
            values.append(running_total / period)
    return values


def exponential_moving_average(candles: Sequence[Candle], period: int) -> list[float | None]:
    _validate_period(period)

    closes = _extract_closes(candles)
    if not closes:
        return []

    values: list[float | None] = [None] * len(closes)
    if len(closes) < period:
        return values

    multiplier = 2.0 / (period + 1)
    seed = sum(closes[:period]) / period
    values[period - 1] = seed
    previous = seed

    for index in range(period, len(closes)):
        current = ((closes[index] - previous) * multiplier) + previous
        values[index] = current
        previous = current
    return values


def relative_strength_index(candles: Sequence[Candle], period: int = 14) -> list[float | None]:
    _validate_period(period)

    closes = _extract_closes(candles)
    if not closes:
        return []

    values: list[float | None] = [None] * len(closes)
    if len(closes) <= period:
        return values

    changes = [closes[index] - closes[index - 1] for index in range(1, len(closes))]
    gains = [max(change, 0.0) for change in changes]
    losses = [max(-change, 0.0) for change in changes]

    average_gain = sum(gains[:period]) / period
    average_loss = sum(losses[:period]) / period
    values[period] = _calculate_rsi(average_gain, average_loss)

    for index in range(period, len(changes)):
        average_gain = ((average_gain * (period - 1)) + gains[index]) / period
        average_loss = ((average_loss * (period - 1)) + losses[index]) / period
        values[index + 1] = _calculate_rsi(average_gain, average_loss)
    return values


def build_standard_indicators(candles: Sequence[Candle]) -> StandardIndicatorSet:
    return StandardIndicatorSet(
        sma_20=simple_moving_average(candles, 20),
        ema_12=exponential_moving_average(candles, 12),
        ema_26=exponential_moving_average(candles, 26),
        rsi_14=relative_strength_index(candles, 14),
    )


def _extract_closes(candles: Sequence[Candle]) -> list[float]:
    return [candle.close for candle in candles]


def _validate_period(period: int) -> None:
    if period <= 0:
        raise ValueError("period must be greater than zero")


def _calculate_rsi(average_gain: float, average_loss: float) -> float:
    if average_loss == 0.0 and average_gain == 0.0:
        return 50.0
    if average_loss == 0.0:
        return 100.0
    if average_gain == 0.0:
        return 0.0

    relative_strength = average_gain / average_loss
    return 100.0 - (100.0 / (1.0 + relative_strength))
